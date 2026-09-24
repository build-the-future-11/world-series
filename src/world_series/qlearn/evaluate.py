from __future__ import annotations
from typing import Any
import numpy as np
import torch
from world_series.core.contracts import ErrorCode, RunStatus, WorldSeriesError
from world_series.core.budgets import BudgetLedger, Budget
from world_series.evaluation.runner import RunDirectory
from world_series.qlearn.tasks import build_tasks, family_split
from world_series.qlearn.baselines import (
    tune_fixed,
    auc_normalized,
    adamw_trajectory,
    sgd_trajectory,
    momentum_trajectory,
    is_diverged,
)
from world_series.qlearn.policy import BoundedDiagonalPolicy
from world_series.qlearn.meta_train import meta_step
from world_series.qlearn.functional import np_to_torch_spd
from world_series.qlearn.unroll import unroll_quadratic

def _policy_curve(task, policy, steps: int):
    A, b, x0 = np_to_torch_spd(task.optimizee.A, task.optimizee.b, task.optimizee.x0)
    _, qlosses = unroll_quadratic(A, b, x0, policy, steps=steps)
    return [float(q.detach()) for q in qlosses]

def run_experiment(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    if cfg.get('params', {}).get('optimizee') == 'neural_regression_v1':
        from world_series.qlearn.regression_study import run_experiment as run_neural
        return run_neural(cfg, run)
    budget = Budget(**cfg.get("budget", {}))
    ledger = BudgetLedger(budget)
    seed = int(cfg["seed"])
    params = cfg.get("params", {})
    steps = int(params.get("steps", 8))
    long_steps = int(params.get("long_steps", max(steps * 2, 16)))
    n_tasks = int(params.get("n_tasks", 4))
    meta_steps = int(params.get("meta_steps", 5))
    tasks = build_tasks(seed, n=n_tasks, dim=int(params.get("dim", 4)))
    splits = family_split(tasks, seed)
    train = [r.payload for r in splits["train"]]
    held = [r.payload for r in splits["dev"]]
    if not train or not held:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG,
                               'qlearn requires nonempty disjoint train/dev families')
    ledger.consume_step(1)

    # matched fixed baselines on held-out (tune on train proxy = first train task only to keep tiny)
    tune_task = train[0]
    sgd = tune_fixed(tune_task, "sgd", steps)
    mom = tune_fixed(tune_task, "momentum", steps)
    adam = tune_fixed(tune_task, "adamw", steps)

    policy = BoundedDiagonalPolicy().double()
    meta_losses = []
    for _ in range(meta_steps):
        ledger.consume_step(1)
        meta_losses.append(meta_step(train, policy, steps=min(4, steps)))

    raw_trajectories = []

    def eval_set(task_list, horizon):
        methods = ['candidate', 'sgd', 'momentum', 'adamw']
        outs = {k: [] for k in methods + ['auc_' + m for m in methods]}
        diverged = {m: 0 for m in methods}
        for t in task_list:
            cand = _policy_curve(t, policy, horizon)
            _, sgd_c = sgd_trajectory(t, horizon, eta=sgd["eta"])
            _, mom_c = momentum_trajectory(t, horizon, eta=mom["eta"])
            _, adam_c = adamw_trajectory(t, horizon, eta=adam["eta"])
            curves = dict(zip(methods, [cand, sgd_c, mom_c, adam_c]))
            for method, curve in curves.items():
                outs[method].append(curve[-1])
                outs['auc_' + method].append(auc_normalized(curve, initial=curve[0]))
                diverged[method] += int(is_diverged(curve))
            raw_trajectories.append({
                'task_id': t.task_id, 'family_id': t.family_id, 'horizon': horizon,
                'initial_loss': t.optimizee.loss(t.optimizee.x0), 'curves': curves,
                'diverged': {m: is_diverged(c) for m, c in curves.items()},
            })
            ledger.consume_step(1)
        summary = {k: float(np.mean(v)) for k, v in outs.items()}
        summary['divergence_counts'] = diverged
        summary['divergence_rates'] = {m: n / len(task_list) for m, n in diverged.items()}
        summary['n_tasks'] = len(task_list)
        return summary

    held_short = eval_set(held, steps)
    held_long = eval_set(held, long_steps)

    # primary: AUC loss-vs-compute on held short horizon (lower better)
    primary = held_short["auc_candidate"]
    best_base_auc = min(held_short['auc_' + m] for m in ['sgd', 'momentum', 'adamw'])
    metrics = {
        "status": RunStatus.SUCCEEDED.value,
        "primary_metric": "auc_normalized_loss_vs_step_held",
        "primary_value": primary,
        "best_baseline_final": float(min(held_short["sgd"], held_short["momentum"], held_short["adamw"])),
        "candidate_vs_best_baseline_final_delta": float(min(held_short["sgd"], held_short["momentum"], held_short["adamw"]) - held_short["candidate"]),
        "held_short": held_short,
        "held_long": held_long,
        "tuned_etas": {"sgd": sgd["eta"], "momentum": mom["eta"], "adamw": adam["eta"]},
        "tuning_evals_per_method": sgd["tuning_evals"],
        "meta_train_losses": meta_losses,
        "n_train": len(train),
        "n_held": len(held),
        "steps": steps,
        "long_steps": long_steps,
        "auc_delta_vs_best_fixed_finalproxy": None,
        "auc_delta_vs_best_fixed_auc": float(best_base_auc - primary),
        "metric_schema_version": 'development-diagnostics-v2',
        "metric_notes": [
            'The historical AUC-minus-final-loss proxy mixed metrics and is invalid.',
            'Legacy AUC primary retained for continuity; per-curve minimum and post-update '
            'normalization remain limitations, not a qualified common-scale comparison.',
            'Divergence diagnostic: nonfinite loss or absolute loss above 1e6; '
            'all trajectories remain in the denominator and retained raw evidence.',
        ],
        "split_families": {'train': sorted({t.family_id for t in train}),
                           'dev': sorted({t.family_id for t in held})},
        "cost": ledger.snapshot(),
        "meta_training_separated": True,
        "research_outcome": "INCONCLUSIVE",
        "research_outcome_note": "Development paired comparison only; protocol DRAFT_NOT_AUTHORIZED; sample too small for confirmation.",
        "query_labels_in_controller_features": False,
    }
    ref = run.store.write_json('qlearn_trajectories.json', raw_trajectories)
    metrics['raw_trajectories'] = {'path': ref.relative_path, 'sha256': ref.sha256}
    run.store.write_json("qlearn_metrics.json", metrics)
    return metrics
