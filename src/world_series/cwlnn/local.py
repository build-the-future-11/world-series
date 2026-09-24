from __future__ import annotations

import numpy as np


def sparse_mean_aggregate(features: np.ndarray, edge_index: np.ndarray) -> np.ndarray:
    n, _h = features.shape
    out = features.copy()
    if edge_index.size == 0:
        return out
    src = np.asarray(edge_index[0], dtype=np.int64)
    dst = np.asarray(edge_index[1], dtype=np.int64)
    acc = np.zeros_like(features)
    np.add.at(acc, dst, features[src])
    deg = np.zeros(n, dtype=np.float64)
    np.add.at(deg, dst, 1.0)
    deg = np.maximum(deg, 1.0)
    return out + acc / deg[:, None]


def dense_mean_aggregate(features: np.ndarray, adj: np.ndarray) -> np.ndarray:
    deg = adj.sum(axis=1, keepdims=True)
    deg = np.maximum(deg, 1.0)
    return features + (adj @ features) / deg
