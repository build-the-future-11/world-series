from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from world_series.core.contracts import ErrorCode, WorldSeriesError

@dataclass
class RoutingReceipt:
    selected: list[int]
    requested: int
    actual: int
    dropped: int

def budgeted_select(scores: np.ndarray, budget: int) -> RoutingReceipt:
    if budget < 0:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "routing budget must be >=0")
    order = np.argsort(-scores)
    selected = order[:budget].tolist()
    return RoutingReceipt(selected=selected, requested=budget, actual=len(selected), dropped=max(0, len(scores) - len(selected)))
