from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

@dataclass
class EngramStore:
    capacity: int = 128
    keys: list[np.ndarray] = field(default_factory=list)
    values: list[float] = field(default_factory=list)

    def write(self, key: np.ndarray, value: float) -> None:
        if len(self.keys) >= self.capacity:
            self.keys.pop(0)
            self.values.pop(0)
        self.keys.append(np.asarray(key, dtype=np.float64))
        self.values.append(float(value))

    def recent(self, k: int = 5) -> list[float]:
        return self.values[-k:]
