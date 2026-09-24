from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm


@dataclass
class OscillatorParams:
    k: float
    c: float


@dataclass
class Trajectory:
    times: np.ndarray
    observations: np.ndarray  # [T,2] q,v
    trajectory_id: str
    params: OscillatorParams
    noisy: bool


def simulate_oscillator(k: float, c: float, q0: float, v0: float, t: np.ndarray) -> np.ndarray:
    """Integrate linear oscillator. Uses exact matrix exponential on uniform grids."""
    t = np.asarray(t, dtype=np.float64)
    y = np.empty((len(t), 2), dtype=np.float64)
    state = np.array([q0, v0], dtype=np.float64)
    y[0] = state
    if len(t) < 2:
        return y
    A = np.array([[0.0, 1.0], [-k, -c]], dtype=np.float64)
    dts = np.diff(t)
    # Fast path: constant step size
    if np.allclose(dts, dts[0], rtol=0.0, atol=1e-12):
        step = expm(A * float(dts[0]))
        for i in range(1, len(t)):
            state = step @ state
            y[i] = state
        return y
    # Variable steps: still hoist A; one expm per interval
    for i, dt in enumerate(dts, start=1):
        state = expm(A * float(dt)) @ state
        y[i] = state
    return y


def make_trajectory(seed: int, k: float, c: float, noise: float = 0.0) -> Trajectory:
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 5, 81)
    q0, v0 = rng.normal(size=2)
    clean = simulate_oscillator(k, c, q0, v0, t)
    obs = clean if noise == 0.0 else clean + noise * rng.normal(size=clean.shape)
    return Trajectory(t, obs, f"traj_{seed}", OscillatorParams(k, c), noisy=noise > 0)


def energy(q, v, k):
    return 0.5 * (v * v + k * q * q)
