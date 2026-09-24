from __future__ import annotations
import numpy as np
from world_series.cwlnn.local import sparse_mean_aggregate

def flat_mp(features, edge_index, layers: int = 2):
    h = features
    for _ in range(layers):
        h = sparse_mean_aggregate(h, edge_index)
    return h

def tiny_attention(features, budget_pairs: int):
    """Feasible attention control: only top-score pairs, not dense all-pairs hidden as sparse."""
    n = features.shape[0]
    # score by feature norm
    scores = np.linalg.norm(features, axis=1)
    order = np.argsort(-scores)
    selected = order[: max(1, int(np.sqrt(2 * budget_pairs)))]
    # attend only within selected subset
    sub = features[selected]
    # softmax-like avg
    w = np.exp(np.linalg.norm(sub, axis=1))
    w = w / w.sum()
    ctx = (w[:, None] * sub).sum(axis=0)
    out = features.copy()
    out[selected] = out[selected] + ctx
    return out, {"selected": len(selected), "pairs_budget": budget_pairs}
