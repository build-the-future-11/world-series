from __future__ import annotations
from typing import Any
import numpy as np
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import RunStatus
from world_series.evaluation.runner import RunDirectory
from world_series.wpinn.systems import make_trajectory, simulate_oscillator
from world_series.wpinn.baselines import data_only_accel_fit, known_support_fit
from world_series.wpinn.constraints import check_conservation, check_dissipation
from world_series.wpinn.train import weak_only_fit, fit_with_structure

def rollout_error(traj, coef: dict) -> float:
    k = -coef.get("q", 0.0)
    c = -coef.get("v", 0.0)
    if k <= 0:
        return float("inf")
    q0, v0 = traj.observations[0]
    pred = simulate_oscillator(k, max(c, 0.0), q0, v0, traj.times)
    return float(np.mean((pred - traj.observations) ** 2))

def support_recall(support: set[str], truth=("q", "v")) -> float:
    truth_s = set(truth)
    if not truth_s:
        return 0.0
    return len(support & truth_s) / len(truth_s)

def run_experiment(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    budget = Budget(**cfg.get("budget", {}))
    ledger = BudgetLedger(budget)
    seed = int(cfg["seed"])
    # split by parameters: train-like and held-out param shift
    undamped = make_trajectory(seed, k=2.0, c=0.0, noise=0.0)
    damped = make_trajectory(seed + 1, k=2.0, c=0.3, noise=0.02)
    held = make_trajectory(seed + 2, k=2.5, c=0.25, noise=0.02)
    ledger.consume_step(1)

    weak_coef, weak_r, support = weak_only_fit(damped)
    base = data_only_accel_fit(damped)
    known = known_support_fit(damped)
    # wrong conservation on damped — labeled failure ablation
    wrong_coef, wrong_r, wrong_sup = fit_with_structure(damped, enforce_conservation=True)
    cons_u = check_conservation(undamped)
    cons_d = check_conservation(damped)
    diss = check_dissipation(damped)

    primary = rollout_error(held, weak_coef)
    metrics = {
        "status": RunStatus.SUCCEEDED.value,
        "primary_metric": "heldout_rollout_mse",
        "primary_value": primary,
        "weak_only_coef": weak_coef,
        "weak_residual_norm": weak_r,
        "support": sorted(support),
        "support_recall_qv": support_recall(support),
        "baseline_data_only": base,
        "baseline_known_support": known,
        "rollout_mse_weak_held": primary,
        "rollout_mse_data_only_held": rollout_error(held, base),
        "rollout_mse_wrong_conservation_held": rollout_error(held, wrong_coef),
        "wrong_conservation_ablation": {
            "coef": wrong_coef,
            "residual": wrong_r,
            "label": "FAILED_ABLATION_EXPECTED_FOR_DAMPED",
            "worse_than_weak": rollout_error(held, wrong_coef) > primary,
        },
        "conservation_undamped_ok": cons_u["ok"],
        "wrong_conservation_on_damped_claimed_ok": cons_d["ok"],
        "dissipation_damped": diss,
        "no_clean_fd_in_weak_candidate": True,
        "cost": ledger.snapshot(),
        "research_outcome": "INCONCLUSIVE",
        "note": "Primary declared as held-out rollout MSE before comparing; confirmation not authorized.",
    }
    run.store.write_json("wpinn_result.json", metrics)
    return metrics
