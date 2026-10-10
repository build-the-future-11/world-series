from __future__ import annotations
from dataclasses import dataclass, field
import math
from numbers import Integral, Real
import numpy as np

@dataclass
class EngramStore:
    capacity: int = 128
    keys: list[np.ndarray] = field(default_factory=list)
    values: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.capacity, (bool, np.bool_)) or not isinstance(self.capacity, Integral) or self.capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self.capacity = int(self.capacity)
        keys, values = list(self.keys), list(self.values)
        if len(keys) != len(values) or len(keys) > self.capacity:
            raise ValueError("initial memory keys/values must match and fit capacity")
        self.keys, self.values = [], []
        for key, value in zip(keys, values):
            self.write(key, value)

    def write(self, key: np.ndarray, value: float) -> None:
        if np.iscomplexobj(key):
            raise ValueError("memory key must be a finite real vector")
        array = np.asarray(key, dtype=np.float64)
        if array.ndim != 1 or not array.size or not np.isfinite(array).all():
            raise ValueError("memory key must be a finite nonempty real vector")
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real) or not math.isfinite(value):
            raise ValueError("memory value must be a finite real number")
        # Snapshot before eviction. The bytes owner prevents a caller from
        # re-enabling writes and changing a retained pre-observation context.
        snapshot = np.frombuffer(array.tobytes(), dtype=np.float64).reshape(array.shape)
        if len(self.keys) >= self.capacity:
            self.keys.pop(0)
            self.values.pop(0)
        self.keys.append(snapshot)
        self.values.append(float(value))

    def recent(self, k: int = 5) -> list[float]:
        if isinstance(k, (bool, np.bool_)) or not isinstance(k, Integral) or k < 0:
            raise ValueError("recent count must be a non-negative integer")
        if k == 0:
            return []
        return self.values[-k:]
