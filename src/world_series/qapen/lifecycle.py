from __future__ import annotations
import numpy as np
from world_series.qapen.experts import ExpertBank, ExpertState
from world_series.qapen.memory import EngramStore
from world_series.qapen.mixture import mixture_moments

class QAPENModel:
    """predict -> record -> observe -> score -> update"""

    def __init__(self, max_experts: int = 8):
        self.bank = ExpertBank(max_experts=max_experts)
        self.memory = EngramStore()
        self._last_pred = None
        # start with one expert
        e = self.bank.spawn()
        self.bank.transition(e, ExpertState.WARMUP)
        self.bank.transition(e, ExpertState.ACTIVE)
        e.weight = 1.0

    def predict(self) -> tuple[float, float]:
        active = [e for e in self.bank.experts if e.state in {ExpertState.ACTIVE, ExpertState.REVIVED, ExpertState.WARMUP}]
        if not active:
            self._last_pred = (0.0, 1.0)
            return self._last_pred
        w = np.array([max(e.weight, 1e-6) for e in active], dtype=np.float64)
        means = np.array([e.mean for e in active])
        vars_ = np.array([e.var for e in active])
        _, mean, var = mixture_moments(w, means, vars_)
        self._last_pred = (mean, var)
        return mean, var

    def record(self, context: np.ndarray) -> None:
        # cannot use future targets
        assert self._last_pred is not None
        self.memory.write(context, self._last_pred[0])

    def observe(self, y: float) -> float:
        mean, var = self._last_pred
        # gaussian nll-like score
        score = 0.5 * np.log(2 * np.pi * var) + 0.5 * ((y - mean) ** 2) / var
        return float(score)

    def update(self, y: float, surprise_thresh: float = 4.0) -> None:
        mean, var = self._last_pred
        surprise = (y - mean) ** 2 / (var + 1e-8)
        active = [e for e in self.bank.experts if e.state == ExpertState.ACTIVE]
        # update closest expert
        if active:
            e = min(active, key=lambda ex: abs(ex.mean - y))
            e.n_obs += 1
            lr = 1.0 / e.n_obs
            e.mean = (1 - lr) * e.mean + lr * y
            e.var = max(0.05, (1 - lr) * e.var + lr * (y - e.mean) ** 2)
            e.weight = e.weight * 0.95 + 0.05
        if surprise > surprise_thresh and len(self.bank.experts) < self.bank.max_experts:
            e = self.bank.spawn()
            self.bank.transition(e, ExpertState.WARMUP)
            e.mean = y
            e.var = 1.0
            e.weight = 0.1
            self.bank.transition(e, ExpertState.ACTIVE)
