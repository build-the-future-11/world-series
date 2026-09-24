from __future__ import annotations
import numpy as np

def thresholded_lstsq(A: np.ndarray, b: np.ndarray, thresh: float = 0.1, iters: int = 5):
    xi, *_ = np.linalg.lstsq(A, b, rcond=None)
    for _ in range(iters):
        support = np.abs(xi) >= thresh
        if not np.any(support):
            support[np.argmax(np.abs(xi))] = True
        xi_new = np.zeros_like(xi)
        xi_new[support], *_ = np.linalg.lstsq(A[:, support], b, rcond=None)
        xi = xi_new
    return xi
