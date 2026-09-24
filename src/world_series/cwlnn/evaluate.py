from __future__ import annotations
from typing import Any
import numpy as np
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import RunStatus
from world_series.evaluation.runner import RunDirectory
from world_series.cwlnn.graphs import GraphLevel, path_edges
from world_series.cwlnn.local import sparse_mean_aggregate, dense_mean_aggregate
from world_series.cwlnn.model import forward_multiscale
from world_series.cwlnn.baselines import flat_mp, tiny_attention

def run_experiment(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    budget = Budget(**cfg.get("budget", {}))
    ledger = BudgetLedger(budget)
    n = int(cfg.get("params", {}).get("n_nodes", 24))
    ledger.refuse_allocation(nodes=n)
    rng = np.random.default_rng(int(cfg["seed"]))
    # synthetic target: local + coarse mean signal
    feats = rng.normal(size=(n, 4))
    edges = path_edges(n)
    level = GraphLevel(features=feats, edge_index=edges)
    adj = np.zeros((n, n))
    if edges.size:
        adj[edges[0], edges[1]] = 1.0
    sparse = sparse_mean_aggregate(feats, edges)
    dense = dense_mean_aggregate(feats, adj)
    flat = flat_mp(feats, edges)
    hier, receipt = forward_multiscale(level, route_budget=None)
    routed, rreceipt = forward_multiscale(level, route_budget=6)
    attn, attn_meta = tiny_attention(feats, budget_pairs=32)
    # held-out larger graph
    n2 = n * 2
    ledger.refuse_allocation(nodes=n2)
    feats2 = rng.normal(size=(n2, 4))
    level2 = GraphLevel(features=feats2, edge_index=path_edges(n2))
    out2, _ = forward_multiscale(level2, route_budget=8)
    metrics = {
        "status": RunStatus.SUCCEEDED.value,
        "sparse_dense_max_abs_diff": float(np.max(np.abs(sparse - dense))),
        "flat_norm": float(np.linalg.norm(flat)),
        "hier_norm": float(np.linalg.norm(hier)),
        "routed_norm": float(np.linalg.norm(routed)),
        "routing": None if rreceipt is None else {"actual": rreceipt.actual, "dropped": rreceipt.dropped},
        "attention_control": attn_meta,
        "size_transfer_out_shape": list(out2.shape),
        "cost": ledger.snapshot(),
        "research_outcome": "INCONCLUSIVE",
        "note": "No hidden dense all-pairs in claimed sparse path; attention control is explicitly budgeted.",
    }
    run.store.write_json("cwlnn_result.json", metrics)
    return metrics
