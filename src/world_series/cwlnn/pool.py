from __future__ import annotations

import numpy as np


def pool(features, parent, n_coarse):
    h = features.shape[1]
    out = np.zeros((n_coarse, h), dtype=np.float64)
    counts = np.zeros(n_coarse, dtype=np.float64)
    parent = np.asarray(parent, dtype=np.int64)
    np.add.at(out, parent, features)
    np.add.at(counts, parent, 1.0)
    return out / np.maximum(counts[:, None], 1.0)


def unpool(coarse_features, parent):
    return coarse_features[np.asarray(parent, dtype=np.int64)]
