from __future__ import annotations

import numpy as np


def test_functions(t: np.ndarray, n: int = 4) -> np.ndarray:
    s = (t - t[0]) / (t[-1] - t[0] + 1e-12)
    m = np.arange(1, n + 1, dtype=np.float64)
    # shape [T, n]
    return (np.sin(np.pi * s) ** 2)[:, None] * np.sin(np.pi * s[:, None] * m)


def assemble_weak_system(t: np.ndarray, x: np.ndarray, Theta: np.ndarray, psi: np.ndarray):
    """Least-squares system for xi without differentiating noisy x for regression targets.

    For ``x' = Theta xi`` with test ψ vanishing at endpoints:
    ``∫ ψ x' = -∫ ψ' x = ∫ ψ (Theta xi)``, hence ``(∫ ψ Theta) xi = -∫ ψ' x``.
    """
    dt = np.gradient(t)
    psi_t = np.gradient(psi, t, axis=0)
    w = psi * dt[:, None]  # [T, n_test]
    b = -(psi_t * dt[:, None] * x[:, None]).sum(axis=0)
    # A[j,k] = sum_t psi[t,j] * dt[t] * Theta[t,k]
    A = w.T @ Theta
    return A, b


def weak_residual(t, x, Theta, xi, psi):
    """Residual of ``∫ ψ (Theta xi) + ∫ ψ' x`` (≈0 under the weak identity)."""
    dt = np.gradient(t)
    psi_t = np.gradient(psi, t, axis=0)
    pred = Theta @ xi
    term_theta = (psi * dt[:, None] * pred[:, None]).sum(axis=0)
    term_ibp = (psi_t * dt[:, None] * x[:, None]).sum(axis=0)
    return term_theta + term_ibp
