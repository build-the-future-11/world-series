from __future__ import annotations
from typing import Any
import numpy as np
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import RunStatus
from world_series.evaluation.runner import RunDirectory
from world_series.qapen.streams import returning_regime_stream
from world_series.qapen.lifecycle import QAPENModel
from world_series.qapen.mixture import mixture_moments
from world_series.qapen.baselines import FixedEnsemble, AdaptiveNoMemory, RecentMemoryControl, nll

def run_experiment(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    budget = Budget(**cfg.get("budget", {}))
    ledger = BudgetLedger(budget)
    schedule, xs = returning_regime_stream(int(cfg["seed"]), n=int(cfg.get("params", {}).get("n", 160)))
    model = QAPENModel(max_experts=budget.max_experts)
    fixed = FixedEnsemble()
    adapt = AdaptiveNoMemory()
    recent = RecentMemoryControl(k=5)
    scores = {"qapen": [], "fixed": [], "adapt_no_mem": [], "recent": []}
    rare = {k: [] for k in scores}
    ordinary = {k: [] for k in scores}
    for t, y in enumerate(xs):
        ledger.consume_sim(1)
        y = float(y)
        # predict->record->observe->score->update causal order for candidate
        m, v = model.predict()
        model.record(np.array([float(t)]))
        scores["qapen"].append(nll(y, m, v))
        model.update(y)
        fm, fv = fixed.predict()
        scores["fixed"].append(nll(y, fm, fv))
        am, av = adapt.predict()
        scores["adapt_no_mem"].append(nll(y, am, av))
        adapt.update(y)
        rm, rv = recent.predict()
        scores["recent"].append(nll(y, rm, rv))
        recent.update(y)
        if schedule[t] == 1:
            for k in scores:
                rare[k].append(scores[k][-1])
        else:
            for k in scores:
                ordinary[k].append(scores[k][-1])
    w, mean, var = mixture_moments(np.array([0.3, 0.7]), np.array([0.0, 2.0]), np.array([1.0, 0.5]))
    means = {k: float(np.mean(v)) for k, v in scores.items()}
    # Toy-scale interpretation vs strongest simple memory control (not confirmation).
    vs_recent = means["qapen"] < means["recent"]
    vs_fixed = means["qapen"] < means["fixed"]
    if vs_recent and vs_fixed:
        outcome = "INCONCLUSIVE"  # still underpowered / DRAFT
        outcome_note = "Candidate beat fixed and recent on mean NLL at this seed/scale; not confirmation."
    elif (not vs_recent) and vs_fixed:
        outcome = "NOT_SUPPORTED"
        outcome_note = "Candidate lost to recent-memory control on mean NLL; lifecycle/engram claim unsupported at this toy scale."
    else:
        outcome = "NOT_SUPPORTED"
        outcome_note = "Candidate did not beat required simple controls on mean NLL at this toy scale."
    metrics = {
        "status": RunStatus.SUCCEEDED.value,
        "primary_metric": "mean_nll",
        "mean_nll": means,
        "rare_regime_nll": {k: float(np.mean(v)) if v else None for k, v in rare.items()},
        "ordinary_regime_nll": {k: float(np.mean(v)) if v else None for k, v in ordinary.items()},
        "regime_counts": {"regime_1": int(sum(schedule == 1)), "regime_0": int(sum(schedule == 0))},
        "memory_affects_predictions": False,
        "regime_label_note": "Legacy schedule is balanced; regime 1 is not statistically rare.",
        "ordinary_regime_tradeoff_note": "Report both ordinary and rare; do not hide ordinary-error tradeoff.",
        "beat_recent_memory": vs_recent,
        "beat_fixed_ensemble": vs_fixed,
        "n_experts": len(model.bank.experts),
        "mixture_check_mean": mean,
        "mixture_check_var": var,
        "cost": ledger.snapshot(),
        "research_outcome": outcome,
        "research_outcome_note": outcome_note,
        "lineage_note": "Finite expandable experts; not infinite computation or Bayesian posterior. APEN/PEN historical identity preserved as separate.",
    }
    run.store.write_json("qapen_result.json", metrics)
    return metrics
