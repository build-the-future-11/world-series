from __future__ import annotations
from typing import Any
from world_series.core.budgets import Budget
from world_series.core.contracts import RunStatus
from world_series.evaluation.runner import RunDirectory
from world_series.ultron.capabilities import bootstrap_adapters, available_ops
from world_series.ultron.state import EpisodeState
from world_series.ultron.router import static_route, cheapest_valid, random_valid
from world_series.ultron.executor import execute_action
from world_series.ultron.evidence import EvidenceDAG
from world_series.ultron.verifier_client import local_dev_verifier
from world_series.ultron.train_router import LinearRouter, OPS

TASK_DEFAULTS = {
    "invariant_puzzle": "solve_invariant_problem",
    "dsl_synthesis": "synthesize_dsl_program",
    "law_id": "identify_dynamical_law",
}

def _run_policy(name, chooser, avail, budget, task_types):
    rows = []
    for tt in task_types:
        state = EpisodeState("demo", tt, (), tuple(avail), 2)
        dag = EvidenceDAG()
        op = chooser(state, avail)
        if op is None:
            rows.append({"task_type": tt, "op": None, "ok": False, "cost": 0.0})
            continue
        state2, receipt = execute_action(state, op, budget, dag)
        ver = local_dev_verifier(tt, receipt.get("diagnostics") or {}, selected_op=op)
        cost = float((receipt.get("cost") or {}).get("wall_seconds", 0.0))
        rows.append({"task_type": tt, "op": op, "ok": bool(ver.get("ok")), "cost": cost, "verifier_tag": ver.get("tag")})
    return rows

def run_experiment(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    bootstrap_adapters()
    avail = available_ops()
    budget = Budget(**cfg.get("budget", {}))
    task_types = cfg.get("params", {}).get("task_types", ["invariant_puzzle", "dsl_synthesis", "law_id"])
    # development oracle traces for learned router (cost counted as training)
    traces = [{"task_type": tt, "best_op": TASK_DEFAULTS[tt]} for tt in task_types]
    learned = LinearRouter.from_oracle_traces(traces)

    def learned_choose(state, available):
        return learned.choose(state.task_type, available)

    policies = {
        "static": lambda s, a: static_route(s, a),
        "cheapest": lambda s, a: cheapest_valid(s, a),
        "random": lambda s, a: random_valid(s, a, seed=int(cfg["seed"])),
        "learned": learned_choose,
    }
    results = {}
    for name, fn in policies.items():
        results[name] = _run_policy(name, fn, avail, budget, task_types)
    def rate(rows):
        return sum(1 for r in rows if r["ok"]) / max(len(rows), 1)
    completion = {k: rate(v) for k, v in results.items()}
    # unsupported task handling
    bad_state = EpisodeState("x", "unknown_task", (), tuple(avail), 1)
    unsupported = static_route(bad_state, avail) is None
    metrics = {
        "status": RunStatus.SUCCEEDED.value,
        "primary_metric": "verified_completion_rate_at_fixed_budget",
        "completion_rates": completion,
        "policy_results": results,
        "available": avail,
        "unsupported_task_rejected": unsupported,
        "identical_tools_across_policies": True,
        "research_outcome": "INCONCLUSIVE",
        "note": "Local development verifier is PLUMBING_ONLY; not sealed external evaluation. Learned router fit on oracle traces — development only.",
    }
    run.store.write_json("ultron_result.json", metrics)
    return metrics
