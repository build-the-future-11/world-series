from __future__ import annotations
import numpy as np
from world_series.wpinn.library import library_matrix
from world_series.wpinn.weak_form import test_functions, assemble_weak_system, weak_residual
from world_series.wpinn.sparse_fit import thresholded_lstsq

def weak_only_fit(traj, thresh: float = 0.05):
    t = traj.times
    qv = traj.observations
    Theta, names, scales = library_matrix(qv)
    psi = test_functions(t, n=6)
    # identify acceleration: use velocity as the IBP state channel
    A, b = assemble_weak_system(t, qv[:, 1], Theta, psi)
    xi = thresholded_lstsq(A, b, thresh=thresh)
    r = weak_residual(t, qv[:, 1], Theta, xi, psi)
    coef = dict(zip(names, (xi / scales).tolist()))
    support = {n for n, c in coef.items() if abs(c) > 1e-6}
    return coef, float(np.linalg.norm(r)), support

def fit_with_structure(traj, enforce_conservation: bool = False):
    coef, rnorm, support = weak_only_fit(traj)
    if enforce_conservation:
        # wrong for damped: force v-coefficient (damping) toward 0
        coef = dict(coef)
        coef["v"] = 0.0
        support = {k for k, v in coef.items() if abs(v) > 1e-6}
    return coef, rnorm, support
