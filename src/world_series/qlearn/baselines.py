from __future__ import annotations

import numpy as np


def sgd_trajectory(task, steps: int, eta: float = 0.05):
    x = task.optimizee.x0.copy()
    losses = []
    for _ in range(steps):
        g = task.optimizee.grad(x)
        x = x - eta * g
        losses.append(task.optimizee.loss(x))
    return x, losses


def momentum_trajectory(task, steps: int, eta: float = 0.05, beta: float = 0.9):
    x = task.optimizee.x0.copy()
    m = np.zeros_like(x)
    losses = []
    for _ in range(steps):
        g = task.optimizee.grad(x)
        m = beta * m + (1 - beta) * g
        x = x - eta * m
        losses.append(task.optimizee.loss(x))
    return x, losses


def adamw_trajectory(task, steps: int, eta: float = 0.05, beta1=0.9, beta2=0.999, eps=1e-8, wd=0.0):
    x = task.optimizee.x0.copy()
    m = np.zeros_like(x)
    v = np.zeros_like(x)
    losses = []
    for t in range(1, steps + 1):
        g = task.optimizee.grad(x)
        m = beta1 * m + (1 - beta1) * g
        v = beta2 * v + (1 - beta2) * (g * g)
        mhat = m / (1 - beta1 ** t)
        vhat = v / (1 - beta2 ** t)
        # AdamW decay is separate from the gradient and its moment estimates.
        x = (1 - eta * wd) * x - eta * mhat / (np.sqrt(vhat) + eps)
        losses.append(task.optimizee.loss(x))
    return x, losses


def tune_fixed(task, method: str, steps: int, etas=(0.01, 0.05, 0.1, 0.2)):
    """Matched tiny tuning budget over step sizes; returns best final loss + eta + curve."""
    best = None
    for eta in etas:
        if method == "sgd":
            _, losses = sgd_trajectory(task, steps, eta=eta)
        elif method == "momentum":
            _, losses = momentum_trajectory(task, steps, eta=eta)
        elif method == "adamw":
            _, losses = adamw_trajectory(task, steps, eta=eta)
        else:
            raise ValueError(method)
        score = losses[-1]
        if best is None or score < best[0]:
            best = (score, eta, losses)
    return {"final": best[0], "eta": best[1], "curve": best[2], "tuning_evals": len(etas)}


def auc_normalized(curve, initial=None):
    """Area under loss-vs-step after shifting to be nonnegative.

    Quadratic losses can be negative; raw AUC was unstable across seeds.
    We shift by the curve minimum so values are >=0, then normalize by the
    shifted initial value. Lower is better.
    """
    c = np.asarray(curve, dtype=np.float64)
    if c.size == 0:
        return float("nan")
    shifted = c - np.min(c)
    scale = float(shifted[0]) if initial is None else abs(float(initial))
    scale = max(scale, 1e-8)
    return float(np.trapezoid(shifted / scale, dx=1.0))


def is_diverged(curve, thresh: float = 1e6) -> bool:
    c = np.asarray(curve, dtype=np.float64)
    if c.size == 0:
        return True
    return bool(not np.all(np.isfinite(c)) or np.max(np.abs(c)) > thresh)
