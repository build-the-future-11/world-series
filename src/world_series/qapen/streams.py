from __future__ import annotations
import numpy as np

def returning_regime_stream(seed: int, n: int = 200):
    rng = np.random.default_rng(seed)
    # two regimes that return
    schedule = []
    t = 0
    while t < n:
        regime = 0 if (t // 40) % 2 == 0 else 1
        length = min(40, n - t)
        schedule.extend([regime] * length)
        t += length
    xs = []
    for r in schedule:
        mu = 0.0 if r == 0 else 2.0
        xs.append(rng.normal(mu, 0.5))
    return np.asarray(schedule), np.asarray(xs, dtype=np.float64)
