"""Functional neural optimizees for the original bounded-update study.

This is a versioned development extension, not the later discrete MALIS
optimizer/replay/rollback action study. Query data score the outer objective;
they never enter an adaptation update or controller observation.
"""
from __future__ import annotations

import copy
from contextlib import nullcontext
import io
import math
import random
import time
from dataclasses import dataclass
from typing import Callable

import numpy as np
import torch
from torch import nn
from torch.func import functional_call

from world_series.core.budgets import BudgetLedger


@dataclass(frozen=True)
class RegressionTask:
    task_id: str
    family: str
    initialization_seed: int
    width: int
    support_x: torch.Tensor
    support_y: torch.Tensor
    query_x: torch.Tensor
    query_y: torch.Tensor

    @property
    def scale(self) -> float:
        # One training-derived scale shared by every method and every step.
        return max(float(self.support_y.square().mean()), 1e-8)

    def build(self) -> nn.Module:
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(self.initialization_seed)
            if self.width == 0:
                return nn.Linear(self.support_x.shape[1], 1).double()
            return nn.Sequential(
                nn.Linear(self.support_x.shape[1], self.width), nn.Tanh(),
                nn.Linear(self.width, self.width), nn.Tanh(), nn.Linear(self.width, 1),
            ).double()


def regression_task(seed: int, family: str, *, width: int = 64,
                    dim: int = 4, support_size: int = 64,
                    query_size: int = 64, namespace: str = 'development') -> RegressionTask:
    if family not in {'linear', 'sin', 'tanh', 'quadratic'}:
        raise ValueError(f'Unknown teacher family: {family}')
    if min(dim, support_size, query_size) <= 0 or width < 0:
        raise ValueError('Require positive data dimensions and nonnegative width')
    generator = torch.Generator().manual_seed(seed)
    weight = torch.randn(dim, 1, generator=generator, dtype=torch.float64) / math.sqrt(dim)
    bias = torch.randn(1, generator=generator, dtype=torch.float64) * 0.2

    def sample(n):
        x = torch.randn(n, dim, generator=generator, dtype=torch.float64)
        z = x @ weight + bias
        y = {'linear': lambda: z, 'sin': lambda: z.sin(),
             'tanh': lambda: z.tanh(), 'quadratic': lambda: z.square() - 1}[family]()
        return x, y

    sx, sy = sample(support_size)
    qx, qy = sample(query_size)
    return RegressionTask(f'{namespace}/{family}/{seed}/width-{width}', family,
                          seed + 1_000_003, width, sx, sy, qx, qy)


class RecurrentUpdatePolicy(nn.Module):
    """Two-layer task-level GRU with bounded per-parameter diagonal updates."""

    def __init__(self, hidden: int = 64, layers: int = 2,
                 eta_bounds=(0.001, 0.1), gate_bounds=(0.1, 2.0),
                 use_budget: bool = True, use_recurrence: bool = True,
                 learn_gates: bool = True, reset_state: bool = False):
        super().__init__()
        if hidden <= 0 or layers <= 0:
            raise ValueError('hidden and layers must be positive')
        if not 0 < eta_bounds[0] < eta_bounds[1] or not 0 < gate_bounds[0] < gate_bounds[1]:
            raise ValueError('Update bounds must be finite, positive and ordered')
        if not all(math.isfinite(v) for v in (*eta_bounds, *gate_bounds)):
            raise ValueError('Update bounds must be finite')
        self.hidden, self.layers = hidden, layers
        self.reset_state = reset_state
        self.eta_bounds, self.gate_bounds = tuple(eta_bounds), tuple(gate_bounds)
        self.use_budget, self.use_recurrence, self.learn_gates = use_budget, use_recurrence, learn_gates
        if not learn_gates and not gate_bounds[0] <= 1 <= gate_bounds[1]:
            raise ValueError('Unit-gate ablation requires bounds containing one')
        self.recurrent = nn.GRU(4, hidden, num_layers=layers).double() if use_recurrence else None
        self.feedforward = None if use_recurrence else nn.Sequential(nn.Linear(4, hidden), nn.Tanh()).double()
        self.step_head = nn.Linear(hidden, 1).double()
        self.gate_head = nn.Sequential(nn.Linear(4 + hidden, 16), nn.Tanh(), nn.Linear(16, 1)).double() if learn_gates else None

    def configuration(self):
        return {k: getattr(self, k) for k in ['hidden', 'layers', 'eta_bounds', 'gate_bounds',
                'use_budget', 'use_recurrence', 'learn_gates', 'reset_state']}

    def forward(self, features, state=None):
        if features.ndim != 2 or features.shape[1] != 4:
            raise ValueError('Expected per-parameter features [P,4]')
        if not self.use_budget:
            features = torch.cat([features[:, :3], torch.zeros_like(features[:, 3:])], dim=1)
        pooled = features.mean(dim=0).reshape(1, 1, 4)
        if self.use_recurrence:
            output, state = self.recurrent(pooled, None if self.reset_state else state)
            context = output[0, 0]
        else:
            context = self.feedforward(pooled[0, 0])
            state = None
        lo, hi = self.eta_bounds
        eta = lo + (hi - lo) * self.step_head(context).sigmoid().squeeze()
        if self.learn_gates:
            lo, hi = self.gate_bounds
            raw = self.gate_head(torch.cat([features, context.expand(len(features), -1)], dim=1))
            gates = lo + (hi - lo) * raw.sigmoid().squeeze(-1)
        else:
            gates = torch.ones_like(features[:, 0])
        return eta, gates, state


@dataclass
class Adaptation:
    parameters: dict[str, torch.Tensor]
    query_losses: list[torch.Tensor]
    support_losses: list[float]
    elapsed_seconds: list[float]
    policy_state: torch.Tensor | None
    momentum: torch.Tensor
    gradient_evaluations: int
    forward_evaluations: int
    diverged: bool


def loss(module, parameters, x, y):
    prediction = functional_call(module, parameters, (x,), strict=True)
    return (prediction - y).square().mean()


def adapt(task: RegressionTask, policy: RecurrentUpdatePolicy, steps: int,
          *, gradient_mode: str = 'full', ledger: BudgetLedger | None = None) -> Adaptation:
    if steps <= 0 or gradient_mode not in {'full', 'first_order_stop_gradient', 'evaluation'}:
        raise ValueError('Require positive steps and a declared gradient mode')
    module = task.build()
    params = {name: p.detach().clone().requires_grad_(True) for name, p in module.named_parameters()}
    momentum = torch.zeros(sum(p.numel() for p in params.values()), dtype=torch.float64)
    state = None
    query_losses = [loss(module, params, task.query_x, task.query_y)]
    support_losses, elapsed = [], [0.0]
    start = time.perf_counter()
    diverged = not bool(torch.isfinite(query_losses[0]))
    for step in range(steps):
        if ledger:
            ledger.consume_step()
        support_loss = loss(module, params, task.support_x, task.support_y)
        grads = torch.autograd.grad(support_loss, tuple(params.values()), create_graph=gradient_mode == 'full')
        flat = torch.cat([g.reshape(-1) for g in grads])
        if gradient_mode == 'first_order_stop_gradient':
            flat = flat.detach()
        momentum = 0.9 * momentum + 0.1 * flat
        # Full mode retains every analytic dependency, including feature paths.
        normalized_grad = flat / (flat.square().mean().sqrt() + 1e-8)
        normalized_momentum = momentum / (momentum.square().mean().sqrt() + 1e-8)
        observed_loss = support_loss if gradient_mode == 'full' else support_loss.detach()
        features = torch.stack([normalized_grad, normalized_momentum,
                                torch.log1p(observed_loss / task.scale).expand_as(flat),
                                torch.full_like(flat, (steps - step) / steps)], dim=1)
        with torch.no_grad() if gradient_mode == 'evaluation' else nullcontext():
            eta, gates, state = policy(features, state)
        updates = eta * gates * flat
        next_params, offset = {}, 0
        for name, parameter in params.items():
            count = parameter.numel()
            next_params[name] = parameter - updates[offset:offset + count].reshape(parameter.shape)
            offset += count
        params = next_params
        if gradient_mode == 'evaluation':
            params = {name: p.detach().requires_grad_(True) for name, p in params.items()}
        with torch.no_grad() if gradient_mode == 'evaluation' else nullcontext():
            query_loss = loss(module, params, task.query_x, task.query_y)
        query_losses.append(query_loss)
        support_losses.append(float(support_loss.detach()))
        elapsed.append(time.perf_counter() - start)
        if not bool(torch.isfinite(query_loss)) or float(query_loss.detach()) / task.scale > 1e6:
            diverged = True
        # Query-derived diagnostics must never control the adaptation trajectory.
        if (not bool(torch.isfinite(support_loss))
                or float(support_loss.detach()) / task.scale > 1e6
                or any(not bool(torch.isfinite(p).all()) for p in params.values())):
            diverged = True
            break
    return Adaptation(params, query_losses, support_losses, elapsed, state, momentum,
                      len(support_losses), 1 + 2 * len(support_losses), diverged)


def fixed_adapt(task: RegressionTask, method: str, steps: int, eta: float,
                *, ledger: BudgetLedger | None = None) -> dict:
    if steps <= 0 or eta <= 0 or not math.isfinite(eta):
        raise ValueError('Require positive steps and finite positive learning rate')
    module = task.build()
    if method == 'sgd':
        optimizer = torch.optim.SGD(module.parameters(), lr=eta)
    elif method == 'momentum':
        optimizer = torch.optim.SGD(module.parameters(), lr=eta, momentum=0.9)
    elif method == 'adamw':
        optimizer = torch.optim.AdamW(module.parameters(), lr=eta, weight_decay=0.01)
    else:
        raise ValueError(f'Unknown fixed method {method}')
    with torch.no_grad():
        curve = [float((module(task.query_x) - task.query_y).square().mean())]
    elapsed, support = [0.0], []
    start = time.perf_counter()
    for _ in range(steps):
        if ledger:
            ledger.consume_step()
        optimizer.zero_grad(set_to_none=True)
        objective = (module(task.support_x) - task.support_y).square().mean()
        objective.backward()
        optimizer.step()
        support.append(float(objective.detach()))
        with torch.no_grad():
            value = float((module(task.query_x) - task.query_y).square().mean())
        curve.append(value)
        elapsed.append(time.perf_counter() - start)
        if (not bool(torch.isfinite(objective)) or float(objective.detach()) / task.scale > 1e6
                or any(not bool(torch.isfinite(p).all()) for p in module.parameters())):
            break
    return {'query_losses': curve, 'support_losses': support, 'elapsed_seconds': elapsed,
            'gradient_evaluations': len(support), 'forward_evaluations': 1 + 2 * len(support),
            'parameters': {name: p.detach().clone() for name, p in module.named_parameters()}}


def trajectory_record(task: RegressionTask, method: str, trajectory, expected_steps: int) -> dict:
    if isinstance(trajectory, Adaptation):
        curve = [float(v.detach()) for v in trajectory.query_losses]
        elapsed, support = trajectory.elapsed_seconds, trajectory.support_losses
        gradient_evaluations, forward_evaluations = trajectory.gradient_evaluations, trajectory.forward_evaluations
    else:
        curve, elapsed, support = (trajectory[k] for k in ['query_losses', 'elapsed_seconds', 'support_losses'])
        gradient_evaluations, forward_evaluations = trajectory['gradient_evaluations'], trajectory['forward_evaluations']
    complete = len(curve) == expected_steps + 1
    finite = all(math.isfinite(v) for v in curve)
    diverged = not complete or not finite or max(curve) / task.scale > 1e6
    normalized = np.array(curve) / task.scale
    return {'task_id': task.task_id, 'family': task.family, 'width': task.width, 'method': method,
            'normalization_scale': task.scale, 'normalization_source': 'support_target_second_moment',
            'query_losses': [v if math.isfinite(v) else None for v in curve],
            'support_losses': [v if math.isfinite(v) else None for v in support],
            'elapsed_seconds': elapsed, 'gradient_evaluations': gradient_evaluations,
            'forward_evaluations': forward_evaluations, 'requested_steps': expected_steps,
            'complete': complete, 'diverged': diverged,
            'normalized_final_loss': float(normalized[-1]) if finite else None,
            'gradient_step_auc': float(np.trapezoid(normalized)) if finite and complete else None,
            'measured_wall_time_auc': float(np.trapezoid(normalized, x=elapsed)) if finite and complete else None}


class MetaTrainer:
    def __init__(self, policy: RecurrentUpdatePolicy, lr: float = 0.0003):
        self.policy = policy
        self.optimizer = torch.optim.AdamW(policy.parameters(), lr=lr, weight_decay=0.01)
        self.completed_steps = 0

    def step(self, tasks: list[RegressionTask], steps: int,
             ledger: BudgetLedger | None = None, on_task: Callable | None = None):
        if not tasks:
            raise ValueError('Empty meta-batch')
        self.optimizer.zero_grad(set_to_none=True)
        losses = []
        for task in tasks:
            trajectory = adapt(task, self.policy, steps, ledger=ledger)
            if on_task:
                on_task(task, trajectory)
            objective = torch.stack(trajectory.query_losses[1:]).mean() / task.scale
            if trajectory.diverged or not bool(torch.isfinite(objective)):
                self.optimizer.zero_grad(set_to_none=True)
                raise FloatingPointError(f'Diverged meta-training task retained: {task.task_id}')
            (objective / len(tasks)).backward()
            losses.append(float(objective.detach()))
            # Sequential backward bounds peak memory to one task's exact graph.
            del trajectory, objective
        gradients = [p.grad for p in self.policy.parameters() if p.grad is not None]
        if not gradients or any(not bool(torch.isfinite(g).all()) for g in gradients):
            raise FloatingPointError('Missing or nonfinite outer gradients')
        norm = torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0, error_if_nonfinite=True)
        self.optimizer.step()
        self.completed_steps += 1
        return {'task_objectives': losses, 'mean_objective': sum(losses) / len(losses),
                'outer_gradient_norm': float(norm), 'completed_meta_steps': self.completed_steps}

    def checkpoint(self) -> bytes:
        numpy_state = np.random.get_state()
        payload = {'schema': 'qlearn-neural-meta-training-v1',
                   'policy_configuration': self.policy.configuration(),
                   'policy': copy.deepcopy(self.policy.state_dict()),
                   'optimizer': copy.deepcopy(self.optimizer.state_dict()),
                   'completed_steps': self.completed_steps,
                   'torch_rng': torch.random.get_rng_state(), 'python_rng': random.getstate(),
                   'numpy_rng': [numpy_state[0], numpy_state[1].tolist(), *numpy_state[2:]]}
        output = io.BytesIO()
        torch.save(payload, output)
        return output.getvalue()

    def restore(self, payload: bytes):
        state = torch.load(io.BytesIO(payload), map_location='cpu', weights_only=True)
        if state.get('schema') != 'qlearn-neural-meta-training-v1':
            raise ValueError('Unsupported checkpoint schema')
        configuration = {**state['policy_configuration']}
        configuration.setdefault('reset_state', False)
        if configuration != self.policy.configuration():
            raise ValueError('Checkpoint policy configuration mismatch')
        self.policy.load_state_dict(state['policy'])
        self.optimizer.load_state_dict(state['optimizer'])
        self.completed_steps = state['completed_steps']
        torch.random.set_rng_state(state['torch_rng'])
        random.setstate(state['python_rng'])
        ns = state['numpy_rng']
        np.random.set_state((ns[0], np.asarray(ns[1], dtype=np.uint32), *ns[2:]))
