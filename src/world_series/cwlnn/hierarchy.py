from __future__ import annotations

import numpy as np

from world_series.cwlnn.graphs import GraphLevel, path_edges, validate_parents


def deterministic_coarsen(level: GraphLevel) -> tuple[GraphLevel, np.ndarray]:
    n, h = level.features.shape
    n_c = (n + 1) // 2
    parent = np.arange(n) // 2
    validate_parents(parent, n, n_c)
    feats = np.zeros((n_c, h), dtype=np.float64)
    counts = np.zeros(n_c, dtype=np.float64)
    np.add.at(feats, parent, level.features)
    np.add.at(counts, parent, 1.0)
    feats /= np.maximum(counts[:, None], 1.0)
    coarse = GraphLevel(features=feats, edge_index=path_edges(n_c), parent_index=None)
    return coarse, parent
