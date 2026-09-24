from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from world_series.core.contracts import ErrorCode, WorldSeriesError

@dataclass
class GraphLevel:
    features: np.ndarray  # [N,H]
    edge_index: np.ndarray  # [2,E]
    parent_index: np.ndarray | None = None

def path_edges(n: int) -> np.ndarray:
    if n <= 1:
        return np.zeros((2, 0), dtype=np.int64)
    src = np.arange(n - 1)
    dst = src + 1
    return np.vstack([np.concatenate([src, dst]), np.concatenate([dst, src])])

def validate_parents(parent_index: np.ndarray, n_fine: int, n_coarse: int) -> None:
    if parent_index.shape != (n_fine,):
        raise WorldSeriesError(ErrorCode.INVALID_SHAPE, "parent_index shape mismatch")
    if np.any(parent_index < 0) or np.any(parent_index >= n_coarse):
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "parent out of bounds")
