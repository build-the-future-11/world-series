from __future__ import annotations
from typing import Any
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import RunStatus
from world_series.evaluation.runner import RunDirectory
from world_series.wcode.dataset import build_tasks
from world_series.wcode.search import compare_rankers, synthesize
from world_series.wcode.verifier import verify_program
from world_series.wcode.graph import extract_graph, ast_hash

def run_experiment(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    budget = Budget(**cfg.get("budget", {}))
    tasks = build_tasks(int(cfg["seed"]))
    # evaluate each family with shared enumerator / matched candidate budget
    per_task = []
    for t in tasks:
        def ledger_factory(b=budget):
            return BudgetLedger(b)
        comps = compare_rankers(t.public_examples, t.heldout, ledger_factory, max_candidates=48)
        per_task.append({"family": t.family_id, "comparisons": comps})
    # primary smoke synthesis with hierarchical
    ledger = BudgetLedger(budget)
    t0 = tasks[0]
    prog, found, used = synthesize(t0.public_examples, ledger, rank_mode="hierarchical")
    ver = verify_program(prog, t0.heldout, exhaustive_domain=list(range(-5, 6))) if found else {"ok": False}
    metrics = {
        "status": RunStatus.SUCCEEDED.value if found else RunStatus.FAILED.value,
        "primary_metric": "verified_solve_rate_at_fixed_candidate_budget",
        "hierarchical_solved": found,
        "hierarchical_candidates_used": used,
        "verifier": ver,
        "per_task_ranker_compare": per_task,
        "ast_hash": ast_hash(prog) if prog is not None else None,
        "graph_nodes": len(extract_graph(prog).node_features) if prog is not None else 0,
        "cost": ledger.snapshot(),
        "research_outcome": "INCONCLUSIVE",
        "note": "Equal enumerator/verifier budget across encoders; not a P vs NP claim.",
    }
    run.store.write_json("wcode_result.json", metrics)
    return metrics
