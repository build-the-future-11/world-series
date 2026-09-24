from __future__ import annotations
import numpy as np

def mixture_moments(weights: np.ndarray, means: np.ndarray, vars_: np.ndarray):
    w = weights / weights.sum()
    mean = float(w @ means)
    second = float(w @ (vars_ + means ** 2))
    var = second - mean ** 2
    return w, mean, var
