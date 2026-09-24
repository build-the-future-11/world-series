from dataclasses import replace

import numpy as np
import pytest
import torch

from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import WorldSeriesError
from world_series.qlearn.regression import (
    MetaTrainer, RecurrentUpdatePolicy, adapt, fixed_adapt,
    regression_task, trajectory_record,
)


def small_policy(**kwargs):
    torch.manual_seed(11)
    return RecurrentUpdatePolicy(hidden=4, layers=2, **kwargs)


def task(family='sin', seed=3):
    return regression_task(seed, family, width=3, dim=2, support_size=7, query_size=9)


def test_neural_update_does_not_use_query_labels_or_inputs():
    original = task()
    poisoned = replace(original, query_y=original.query_y * 900 + 42,
                       query_x=original.query_x.flip(0) * 3)
    policy = small_policy()
    before = adapt(original, policy, 3)
    after = adapt(poisoned, policy, 3)
    for key in before.parameters:
        torch.testing.assert_close(before.parameters[key], after.parameters[key], rtol=0, atol=0)
    assert float(before.query_losses[-1].detach()) != float(after.query_losses[-1].detach())
    assert not torch.equal(original.support_x, original.query_x[:len(original.support_x)])


def test_full_outer_gradient_matches_finite_difference():
    policy = small_policy()
    optimizee = task()
    parameter = policy.step_head.bias
    trajectory = adapt(optimizee, policy, 3)
    objective = torch.stack(trajectory.query_losses[1:]).mean() / optimizee.scale
    analytic, = torch.autograd.grad(objective, parameter)
    base = parameter.detach().clone()
    epsilon = 1e-5
    values = []
    for direction in (1, -1):
        with torch.no_grad():
            parameter.copy_(base + direction * epsilon)
        result = adapt(optimizee, policy, 3)
        values.append(float((torch.stack(result.query_losses[1:]).mean() / optimizee.scale).detach()))
    with torch.no_grad():
        parameter.copy_(base)
    finite_difference = (values[0] - values[1]) / (2 * epsilon)
    assert abs(float(analytic)) > 1e-8
    assert float(analytic) == pytest.approx(finite_difference, rel=1e-5, abs=1e-7)


def test_evaluation_matches_exact_training_updates_without_retaining_outer_graph():
    policy = small_policy()
    optimizee = task()
    full = adapt(optimizee, policy, 8)
    evaluation = adapt(optimizee, policy, 8, gradient_mode='evaluation')
    for key in full.parameters:
        torch.testing.assert_close(full.parameters[key], evaluation.parameters[key], rtol=0, atol=0)
        assert evaluation.parameters[key].grad_fn is None
    torch.testing.assert_close(torch.stack(full.query_losses), torch.stack(evaluation.query_losses), rtol=0, atol=0)
    assert evaluation.policy_state.grad_fn is None


def test_constant_diagonal_update_matches_torch_sgd():
    class ConstantPolicy:
        def __call__(self, features, state):
            return torch.tensor(0.03), torch.ones_like(features[:, 0]), None
    optimizee = task('linear')
    candidate = adapt(optimizee, ConstantPolicy(), 4)
    reference = fixed_adapt(optimizee, 'sgd', 4, eta=float(torch.tensor(0.03)))
    np.testing.assert_allclose([float(v.detach()) for v in candidate.query_losses],
                               reference['query_losses'], rtol=1e-12, atol=1e-12)


def test_meta_checkpoint_restores_optimizer_and_same_next_update():
    tasks = [task('linear'), task('sin', seed=6)]
    trainer = MetaTrainer(small_policy())
    trainer.step(tasks, 3)
    checkpoint = trainer.checkpoint()
    expected_metrics = trainer.step(tasks, 3)
    expected = {k: v.detach().clone() for k, v in trainer.policy.state_dict().items()}
    restored = MetaTrainer(small_policy(), lr=0.9)
    restored.restore(checkpoint)
    assert restored.step(tasks, 3) == expected_metrics
    for key, value in restored.policy.state_dict().items():
        torch.testing.assert_close(value, expected[key], rtol=0, atol=0)
    assert restored.completed_steps == 2


def test_ablations_change_computation_and_state_is_per_task():
    full = small_policy()
    features = torch.randn(5, 4, dtype=torch.float64)
    eta1, gates1, state = full(features)
    eta2, _, _ = full(features, state)
    assert not torch.equal(eta1, eta2)
    torch.testing.assert_close(full(features)[0], eta1, rtol=0, atol=0)
    no_budget = small_policy(use_budget=False)
    changed = features.clone()
    changed[:, 3] += 100
    for a, b in zip(no_budget(features)[:2], no_budget(changed)[:2]):
        torch.testing.assert_close(a, b, rtol=0, atol=0)
    no_gates = small_policy(learn_gates=False)
    assert torch.equal(no_gates(features)[1], torch.ones(5, dtype=torch.float64))
    assert small_policy(use_recurrence=False)(features)[2] is None
    assert 0.001 <= float(eta1.detach()) <= 0.1
    assert bool(((gates1 >= 0.1) & (gates1 <= 2)).all())


def test_budget_exhaustion_prevents_extra_update():
    ledger = BudgetLedger(Budget(max_steps=2, max_wall_seconds=60))
    with pytest.raises(WorldSeriesError, match='step budget'):
        adapt(task(), small_policy(), 3, ledger=ledger)
    assert ledger.steps_used == 2


def test_fixed_scale_and_compute_trace_include_initial_state():
    optimizee = task()
    candidate = trajectory_record(optimizee, 'candidate', adapt(optimizee, small_policy(), 3), 3)
    fixed = trajectory_record(optimizee, 'sgd', fixed_adapt(optimizee, 'sgd', 3, 0.03), 3)
    assert candidate['normalization_scale'] == fixed['normalization_scale'] == optimizee.scale
    assert candidate['query_losses'][0] == fixed['query_losses'][0]
    assert candidate['gradient_evaluations'] == 3
    assert candidate['forward_evaluations'] == 7
    assert len(candidate['elapsed_seconds']) == 4
    assert candidate['gradient_step_auc'] == pytest.approx(
        np.trapezoid(np.array(candidate['query_losses']) / optimizee.scale))


def test_divergent_control_retained_and_not_aggregated_as_full_trajectory():
    optimizee = task('linear')
    raw = fixed_adapt(optimizee, 'sgd', 16, eta=1e8)
    record = trajectory_record(optimizee, 'unstable_control', raw, 16)
    assert record['diverged'] is True
    assert record['gradient_step_auc'] is None
    assert record['gradient_evaluations'] < 16
    assert record['query_losses']
