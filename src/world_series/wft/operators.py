from __future__ import annotations

import numpy as np


def fixed_operator_from_W(W):
    return np.asarray(W, dtype=np.float64).copy()


def learn_operator_ridge(X: np.ndarray, Y: np.ndarray, lam: float = 1e-2) -> np.ndarray:
    """Fit A minimizing ||A X - Y||_F^2 + lam ||A||_F^2 (X,Y shape [n, s]).

    Closed form: A = Y X^T (X X^T + lam I)^{-1}. Same as per-row ridge solves.
    """
    n = X.shape[0]
    gram = X @ X.T
    gram.flat[:: n + 1] += lam
    # Solve (XX^T + lam I) A^T = X Y^T  => A = Y X^T inv(...)
    return np.linalg.solve(gram, X @ Y.T).T


def constrained_sym_nonneg(A: np.ndarray) -> np.ndarray:
    A = 0.5 * (A + A.T)
    A = np.maximum(A, 0.0)
    np.fill_diagonal(A, 0.0)
    return A
