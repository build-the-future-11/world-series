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
    """Solve ``L Phi = M Phi diag(evals)`` for a positive definite mass.

    ``Phi.T @ M @ Phi`` is the identity. ``Q`` is the orthonormal basis in
    whitened coordinates. The diagonal-mass path retains its original
    computation; a dense mass is whitened with its full Cholesky factor.
    """
    L = _symmetric_matrix(L, "L")
    M = _symmetric_matrix(M, "M")
    if L.shape != M.shape:
        raise WorldSeriesError(ErrorCode.INVALID_SHAPE, "L and M must have identical shape")
    diag_m = np.diag(M)
    if np.any(diag_m <= 0):
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "mass matrix diagonal must be positive")
    if np.array_equal(M, np.diag(diag_m)):
        inv_sqrt = 1.0 / np.sqrt(diag_m)
        S = inv_sqrt[:, None] * L * inv_sqrt[None, :]
        evals, Q = np.linalg.eigh(S)
        Phi = inv_sqrt[:, None] * Q
    else:
        try:
            C = np.linalg.cholesky(M)
        except np.linalg.LinAlgError as exc:
            raise WorldSeriesError(
                ErrorCode.INVALID_CONFIG, "mass matrix must be positive definite"
            ) from exc
        # M = C C.T; S = C^{-1} L C^{-T}; Phi = C^{-T} Q.
        left = np.linalg.solve(C, L)
        S = np.linalg.solve(C, left.T).T
        S = 0.5 * (S + S.T)
        evals, Q = np.linalg.eigh(S)
        Phi = np.linalg.solve(C.T, Q)
    return evals, Q, Phi


def _symmetric_matrix(value: np.ndarray, name: str) -> np.ndarray:
    raw = np.asarray(value)
    if np.iscomplexobj(raw):
        raise WorldSeriesError(ErrorCode.INVALID_DTYPE, f"{name} must be real")
    matrix = np.asarray(value, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[0] != matrix.shape[1]:
        raise WorldSeriesError(ErrorCode.INVALID_SHAPE, f"{name} must be nonempty and square")
    if not np.isfinite(matrix).all():
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"{name} must be finite")
    # Scale the symmetry tolerance to the matrix, including very small units.
    scale = float(np.max(np.abs(matrix)))
    if not np.allclose(matrix, matrix.T, rtol=0.0, atol=1e-12 * scale):
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"{name} must be symmetric")
    return matrix


def encode(f: np.ndarray, Phi: np.ndarray, M: np.ndarray) -> np.ndarray:
    return Phi.T @ (M @ f)


def decode(c: np.ndarray, Phi: np.ndarray) -> np.ndarray:
    return Phi @ c


def is_psd(L: np.ndarray, tol: float = 1e-8) -> bool:
    return float(np.linalg.eigvalsh(L).min()) >= -tol
