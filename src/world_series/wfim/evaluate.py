from __future__ import annotations
from typing import Any
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import RunStatus
from world_series.evaluation.runner import RunDirectory
from world_series.wfim.algebra import (
    basis, multiply, unit, project_degree, truncated_multiply, assert_associativity_truncated,
    topk_prune, word_norm, add, SparseWordSeries,
)
from world_series.wfim.transport import transported_multiply, diagonal_transport

def series_bytes(x: SparseWordSeries) -> int:
    # rough stored coefficient bytes
    return sum(8 + 4 * len(w) for w in x.coeffs) + 8

def run_experiment(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    budget = Budget(**cfg.get("budget", {}))
    ledger = BudgetLedger(budget)
    n = min(4, budget.max_algebra_degree)
    ledger.refuse_allocation(degree=n)
    e = unit()
    a = basis(1)
    b = basis(2)
    assert multiply(e, a).coeffs == a.coeffs
    s = add(a, b)
    dist_ok = multiply(s, a).coeffs == add(multiply(a, a), multiply(b, a)).coeffs
    assoc_ok = assert_associativity_truncated(a, b, add(a, b), n=n)
    x = add(a, multiply(a, b))
    y = add(b, a)
    trunc_ok = truncated_multiply(project_degree(x, 2), project_degree(y, 2), 2).coeffs == project_degree(multiply(x, y), 2).coeffs
    big = add(multiply(a, a), add(multiply(b, b), multiply(multiply(a, b), a)))
    pruned = topk_prune(big, k=1)
    # Actual top-1 counterexample: intermediate pruning changes coefficients.
    from world_series.wfim.algebra import SparseWordSeries
    ca = SparseWordSeries({(): -2.0, (1,): -2.0})
    cb = SparseWordSeries({(): -2.0, (1,): -2.0})
    cc = SparseWordSeries({(): -2.0, (1,): -1.0})
    left = topk_prune(multiply(topk_prune(multiply(ca, cb), 1), cc), 1)
    right = topk_prune(multiply(ca, topk_prune(multiply(cb, cc), 1)), 1)
    topk_breaks = left.coeffs != right.coeffs
    scales = {1: 1.2, 2: 0.8}
    # equal-byte compositional compare: fixed algebra vs transported
    expr_fixed = multiply(add(a, b), multiply(a, b))
    expr_trans = transported_multiply(add(a, b), multiply(a, b), scales)
    metrics = {
        "status": RunStatus.SUCCEEDED.value,
        "distributivity_ok": dist_ok,
        "truncated_associativity_ok": assoc_ok,
        "degree_projection_consistency": trunc_ok,
        "topk_need_not_preserve_associativity": True,
        "topk_counterexample_triggered": topk_breaks,
        "topk_witness": {"left": str(left.coeffs), "right": str(right.coeffs)},
        "fixed_product_coeffs": {str(k): v for k, v in expr_fixed.coeffs.items()},
        "transported_product_coeffs": {str(k): v for k, v in expr_trans.coeffs.items()},
        "bytes_fixed": series_bytes(expr_fixed),
        "bytes_transport_params": len(scales) * 8,
        "norm_a": word_norm(a),
        "cost": ledger.snapshot(),
        "research_outcome": "INCONCLUSIVE",
        "note": "Invertible transported multiplication is isomorphic to the reference algebra; compare efficiency not novelty of numbers.",
    }
    run.store.write_json("wfim_result.json", metrics)
    return metrics
