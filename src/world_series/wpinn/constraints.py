from __future__ import annotations
import numpy as np
from world_series.wpinn.systems import energy

def check_conservation(traj, tol: float = 1e-2) -> dict:
    q = traj.observations[:, 0]
    v = traj.observations[:, 1]
    e = energy(q, v, traj.params.k)
    drift = float(np.max(e) - np.min(e))
    ok = drift <= tol and traj.params.c == 0.0
    return {"ok": ok, "energy_drift": drift, "c": traj.params.c}

def check_dissipation(traj) -> dict:
    q = traj.observations[:, 0]
    v = traj.observations[:, 1]
    e = energy(q, v, traj.params.k)
    # energy should be generally nonincreasing for c>0 (numerical ok)
    diffs = np.diff(e)
    frac_noninc = float(np.mean(diffs <= 1e-3))
    return {"ok": traj.params.c > 0 and frac_noninc > 0.7, "frac_nonincreasing": frac_noninc}
