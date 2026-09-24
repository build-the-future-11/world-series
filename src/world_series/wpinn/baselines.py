from __future__ import annotations
import numpy as np
from world_series.wpinn.library import library_matrix
from world_series.wpinn.sparse_fit import thresholded_lstsq

def data_only_accel_fit(traj):
    t = traj.times
    qv = traj.observations
    # finite difference acceleration target (noise-sensitive baseline)
    v = qv[:, 1]
    a = np.gradient(v, t)
    Theta, names, scales = library_matrix(qv)
    xi = thresholded_lstsq(Theta, a, thresh=0.05)
    return dict(zip(names, (xi / scales).tolist()))

def known_support_fit(traj):
    t = traj.times
    qv = traj.observations
    v = qv[:, 1]
    a = np.gradient(v, t)
    Theta, names, scales = library_matrix(qv)
    # known support q,v indices 0,1
    xi = np.zeros(Theta.shape[1])
    xi[:2], *_ = np.linalg.lstsq(Theta[:, :2], a, rcond=None)
    return dict(zip(names, (xi / scales).tolist()))
