from __future__ import annotations
import numpy as np
from world_series.cwlnn.local import sparse_mean_aggregate
from world_series.cwlnn.hierarchy import deterministic_coarsen
from world_series.cwlnn.pool import unpool
from world_series.cwlnn.routing import budgeted_select

def forward_multiscale(level0, route_budget: int | None = None):
    h1 = sparse_mean_aggregate(level0.features, level0.edge_index)
    coarse, parent = deterministic_coarsen(type(level0)(features=h1, edge_index=level0.edge_index))
    h2 = sparse_mean_aggregate(coarse.features, coarse.edge_index)
    if route_budget is not None:
        scores = np.linalg.norm(h2, axis=1)
        receipt = budgeted_select(scores, route_budget)
        mask = np.zeros(len(h2))
        mask[receipt.selected] = 1.0
        h2 = h2 * mask[:, None]
    else:
        receipt = None
    up = unpool(h2, parent)
    out = h1 + up
    return out, receipt
