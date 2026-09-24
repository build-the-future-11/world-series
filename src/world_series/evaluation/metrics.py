"""Metric helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def mean_std(values: Sequence[float]) -> dict[str, float]:
    arr = np.asarray(list(values), dtype=np.float64)
    if arr.size == 0:
        return {"mean": float("nan"), "std": float("nan"), "n": 0.0}
    return {"mean": float(arr.mean()), "std": float(arr.std(ddof=1) if arr.size > 1 else 0.0), "n": float(arr.size)}


def paired_diffs(a: Sequence[float], b: Sequence[float]) -> np.ndarray:
    aa = np.asarray(list(a), dtype=np.float64)
    bb = np.asarray(list(b), dtype=np.float64)
    if aa.shape != bb.shape:
        raise ValueError("paired arrays must match")
    return aa - bb
