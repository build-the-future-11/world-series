from __future__ import annotations

import numpy as np

from world_series.core.contracts import ErrorCode, WorldSeriesError


def path_graph(n: int):
    if n < 1:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "n>=1")
    W = np.zeros((n, n), dtype=np.float64)
    if n == 1:
        return W
    idx = np.arange(n - 1)
    W[idx, idx + 1] = 1.0
    W[idx + 1, idx] = 1.0
    return W


def laplacian_from_weights(W: np.ndarray) -> np.ndarray:
    if np.any(W < 0):
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "edge weights must be nonnegative")
    deg = W.sum(axis=1)
    return np.diag(deg) - W


def weighted_spectral(L: np.ndarray, M: np.ndarray):
    # S = M^{-1/2} L M^{-1/2}
    diag_m = np.diag(M)
    if np.any(diag_m <= 0):
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "mass matrix diagonal must be positive")
    inv_sqrt = 1.0 / np.sqrt(diag_m)
    # S_ij = L_ij / sqrt(m_i m_j)
    S = inv_sqrt[:, None] * L * inv_sqrt[None, :]
    evals, Q = np.linalg.eigh(S)
    Phi = inv_sqrt[:, None] * Q
    return evals, Q, Phi


def encode(f: np.ndarray, Phi: np.ndarray, M: np.ndarray) -> np.ndarray:
    return Phi.T @ (M @ f)


def decode(c: np.ndarray, Phi: np.ndarray) -> np.ndarray:
    return Phi @ c


def is_psd(L: np.ndarray, tol: float = 1e-8) -> bool:
    return float(np.linalg.eigvalsh(L).min()) >= -tol
