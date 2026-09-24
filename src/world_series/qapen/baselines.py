from __future__ import annotations
import numpy as np
from world_series.qapen.mixture import mixture_moments

class FixedEnsemble:
    def __init__(self, means=(0.0, 2.0), vars_=(1.0, 1.0), weights=(0.5, 0.5)):
        self.means = np.asarray(means, dtype=np.float64)
        self.vars = np.asarray(vars_, dtype=np.float64)
        self.weights = np.asarray(weights, dtype=np.float64)

    def predict(self):
        w, mean, var = mixture_moments(self.weights, self.means, self.vars)
        return mean, var

class AdaptiveNoMemory:
    """Adaptive means without engram writes."""
    def __init__(self):
        self.mean = 0.0
        self.var = 1.0
        self.n = 0
        self._pred = (0.0, 1.0)

    def predict(self):
        self._pred = (self.mean, self.var)
        return self._pred

    def update(self, y: float):
        self.n += 1
        lr = 1.0 / self.n
        self.mean = (1 - lr) * self.mean + lr * y
        self.var = max(0.05, (1 - lr) * self.var + lr * (y - self.mean) ** 2)

class RecentMemoryControl:
    def __init__(self, k: int = 5):
        self.buf = []
        self.k = k
        self._pred = (0.0, 1.0)

    def predict(self):
        if not self.buf:
            self._pred = (0.0, 1.0)
        else:
            arr = np.asarray(self.buf[-self.k:], dtype=np.float64)
            self._pred = (float(arr.mean()), float(max(arr.var(), 0.05)))
        return self._pred

    def update(self, y: float):
        self.buf.append(float(y))

def nll(y, mean, var):
    return float(0.5 * np.log(2 * np.pi * var) + 0.5 * ((y - mean) ** 2) / var)
