"""Uncertainty helpers for development analyses (not confirmation)."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def bootstrap_mean_ci(
    values: Sequence[float],
    *,
    n_boot: int = 200,
    seed: int = 0,
    alpha: float = 0.05,
) -> dict[str, float]:
    arr = np.asarray(list(values), dtype=np.float64)
    if arr.size == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0.0}
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n_boot):
        sample = rng.choice(arr, size=arr.size, replace=True)
        means.append(float(sample.mean()))
    lo = float(np.quantile(means, alpha / 2))
    hi = float(np.quantile(means, 1 - alpha / 2))
    return {"mean": float(arr.mean()), "lo": lo, "hi": hi, "n": float(arr.size)}
