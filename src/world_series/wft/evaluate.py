from __future__ import annotations
from typing import Any
import numpy as np
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import RunStatus
from world_series.evaluation.runner import RunDirectory
from world_series.wft.laplacian import path_graph, laplacian_from_weights, weighted_spectral, encode, decode, is_psd
from world_series.wft.operators import learn_operator_ridge, constrained_sym_nonneg, fixed_operator_from_W

def projector(Phi_cols):
    # M-orthogonal projector onto span; here M=I so Phi Phi^T if orthonormal in euclidean after transform
    return Phi_cols @ Phi_cols.T

def run_experiment(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    budget = Budget(**cfg.get("budget", {}))
    ledger = BudgetLedger(budget)
    n = int(cfg.get("params", {}).get("n_nodes", 12))
    ledger.refuse_allocation(nodes=n)
    W = path_graph(n)
    L = laplacian_from_weights(W)
    M = np.eye(n)
    evals, Q, Phi = weighted_spectral(L, M)
    rng = np.random.default_rng(int(cfg["seed"]))
    f = rng.normal(size=n)
    c = encode(f, Phi, M)
    f_hat = decode(c, Phi)
    # held-out size transfer
    n2 = n + 4
    ledger.refuse_allocation(nodes=n2)
    W2 = path_graph(n2)
    L2 = laplacian_from_weights(W2)
    # learn operators on train graphs
    X = rng.normal(size=(n, 24))
    Y = L @ X
    A_un = learn_operator_ridge(X, Y, lam=1e-2)
    A_c = constrained_sym_nonneg(np.abs(A_un))
    A_fixed = fixed_operator_from_W(W)
    # predictive task: forecast L f on held vectors
    Fte = rng.normal(size=(n, 8))
    Yte = L @ Fte
    err = {
        "fixed": float(np.mean((A_fixed @ Fte - Yte) ** 2)),
        "unconstrained": float(np.mean((A_un @ Fte - Yte) ** 2)),
        "constrained": float(np.mean((A_c @ Fte - Yte) ** 2)),
    }
    # subspace compare rather than eigenvector signs
    k = 3
    P1 = projector(Phi[:, :k])
    # flip a column sign — projector should match
    Phi2 = Phi.copy()
    Phi2[:, 0] *= -1
    P2 = projector(Phi2[:, :k])
    metrics = {
        "status": RunStatus.SUCCEEDED.value,
        "primary_metric": "held_vector_mse",
        "psd": is_psd(L),
        "reconstruction_mse": float(np.mean((f - f_hat) ** 2)),
        "energy_preserve": float(np.abs(f @ M @ f - c @ c)),
        "operator_errors": err,
        "projector_sign_invariance_ok": bool(np.allclose(P1, P2)),
        "held_size_psd": is_psd(L2),
        "cost": ledger.snapshot(),
        "research_outcome": "INCONCLUSIVE",
        "note": "Dense eigendecomposition is not FFT-speed computation.",
    }
    run.store.write_json("wft_result.json", metrics)
    return metrics
