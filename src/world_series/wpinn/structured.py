"""Observed-data oscillator discovery; separate from the immutable v1 estimator.

Physical restrictions are extra prior information. The passive model certifies
quadratic energy dissipation, not general nonlinear oscillator discovery.
"""
from __future__ import annotations

import numpy as np
import torch
from scipy.integrate import solve_ivp
from scipy.interpolate import UnivariateSpline
from scipy.optimize import lsq_linear

NAMES = ('1', 'q', 'v', 'q2', 'qv', 'v2', 'q3', 'q2v', 'qv2', 'v3')
POWERS = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2),
          (3, 0), (2, 1), (1, 2), (0, 3))


def validate(t, y):
    t, y = np.asarray(t, dtype=float), np.asarray(y, dtype=float)
    if t.ndim != 1 or len(t) < 5 or y.shape != (len(t), 2):
        raise ValueError('Expected at least five times and two observed channels')
    if not np.isfinite(t).all() or not np.isfinite(y).all() or np.any(np.diff(t) <= 0):
        raise ValueError('Finite observations and strictly increasing times required')
    return t, y


def library(y):
    y = np.asarray(y)
    return np.stack([y[..., 0] ** a * y[..., 1] ** b for a, b in POWERS], axis=-1)


def trapezoid_weights(t):
    t = np.asarray(t, dtype=float)
    if t.ndim != 1 or len(t) < 2 or not np.isfinite(t).all() or np.any(np.diff(t) <= 0):
        raise ValueError('Strictly increasing finite quadrature grid required')
    d = np.diff(t)
    return np.r_[d[0] / 2, (d[:-1] + d[1:]) / 2, d[-1] / 2]


def compact_tests(t, count=16, fraction=.25):
    """Compact C3 polynomial bumps and their analytic physical-time derivative."""
    t = np.asarray(t, dtype=float)
    trapezoid_weights(t)
    if count < 1 or not 0 < fraction <= .5:
        raise ValueError('Invalid test-function configuration')
    width = fraction * (t[-1] - t[0])
    centers = np.linspace(t[0] + width, t[-1] - width, count)
    s = (t[:, None] - centers) / width
    u = np.maximum(1 - s * s, 0)
    return u ** 4, -8 * s * u ** 3 / width


def weak_system(trajectories, count=16, fraction=.25):
    aa, bb = [], []
    for t, y in trajectories:
        t, y = validate(t, y)
        psi, derivative = compact_tests(t, count, fraction)
        weights = trapezoid_weights(t)
        aa.append((psi * weights[:, None]).T @ library(y))
        bb.append(-(derivative * weights[:, None]).T @ y[:, 1])
    if not aa:
        raise ValueError('No observations')
    return np.vstack(aa), np.concatenate(bb)


def derivative_system(trajectories):
    aa, bb = [], []
    for t, y in trajectories:
        t, y = validate(t, y)
        aa.append(library(y))
        bb.append(np.gradient(y[:, 1], t, edge_order=2))
    if not aa:
        raise ValueError('No observations')
    return np.vstack(aa), np.concatenate(bb)


def sparse_fit(a, b, threshold=.05, structure='none', iterations=8):
    """RMS-column STLS; threshold is in scaled coefficient units.

    passive: q' = v, v' = -k q - (c + d q² + e v²)v, k,c,d,e >= 0.
    Thus E=(v²+kq²)/2 has E'=-c v²-d q²v²-e v⁴ <= 0.
    wrong_conservation removes all damping, intentionally wrong for damped data.
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.ndim != 2 or a.shape[1] != len(NAMES) or b.shape != (len(a),) or not len(a):
        raise ValueError('Invalid regression shapes')
    if not np.isfinite(a).all() or not np.isfinite(b).all() or threshold < 0:
        raise ValueError('Finite regression data and nonnegative threshold required')
    allowed = {
        'none': list(range(10)), 'odd': [1, 2, 6, 7, 8, 9],
        'passive': [1, 2, 7, 9], 'wrong_conservation': [1],
        'known_support': [1, 2],
    }
    if structure not in allowed:
        raise ValueError('Unknown physical prior')
    scales = np.sqrt(np.mean(a * a, axis=0))
    scales = np.where(scales > 1e-12, scales, 1.)
    design = a / scales
    active = np.zeros(10, dtype=bool)
    active[allowed[structure]] = True
    xi = np.zeros(10)
    constrained = structure in ('passive', 'wrong_conservation')
    for _ in range(iterations):
        xi[:] = 0
        if not active.any():
            break
        if constrained:
            result = lsq_linear(design[:, active], b, bounds=(-np.inf, 0.), tol=1e-12)
            if not result.success:
                raise RuntimeError('Constrained coefficient fit failed')
            xi[active] = result.x
        else:
            xi[active] = np.linalg.lstsq(design[:, active], b, rcond=None)[0]
        new = active & (np.abs(xi) >= threshold)
        if np.array_equal(active, new):
            break
        active = new
    # Always refit the final support, including a support changed on the last iteration.
    xi[:] = 0
    if active.any():
        if constrained:
            result = lsq_linear(design[:, active], b, bounds=(-np.inf, 0.), tol=1e-12)
            if not result.success:
                raise RuntimeError('Final constrained refit failed')
            xi[active] = result.x
        else:
            xi[active] = np.linalg.lstsq(design[:, active], b, rcond=None)[0]
    coef = xi / scales
    singular = np.linalg.svd(design, compute_uv=False)
    return coef, {'scales': scales.tolist(), 'singular_values': singular.tolist(),
                  'rank': int(np.linalg.matrix_rank(design)),
                  'support': [NAMES[i] for i in np.flatnonzero(active)],
                  'residual': float(np.linalg.norm(a @ coef - b)), 'structure': structure}


def spline_observations(t, y, strength=1.):
    """Observed-only robust noise estimate; no true noise or clean targets accepted."""
    t, y = validate(t, y)
    # Second differences are a heuristic on irregular grids, explicitly not oracle noise.
    diff = np.diff(y, n=2, axis=0)
    sigma = np.median(np.abs(diff - np.median(diff, axis=0)), axis=0) / (.67448975 * np.sqrt(6))
    fitted = np.column_stack([UnivariateSpline(t, y[:, j], s=strength * len(t) * sigma[j] ** 2)(t)
                              for j in range(2)])
    return fitted, {'estimated_noise': sigma.tolist(), 'strength': strength}


class ObservationField(torch.nn.Module):
    def __init__(self, start, stop, width=32):
        super().__init__()
        self.register_buffer('start', torch.tensor(float(start), dtype=torch.float64))
        self.register_buffer('span', torch.tensor(float(stop - start), dtype=torch.float64))
        self.net = torch.nn.Sequential(torch.nn.Linear(1, width), torch.nn.Tanh(),
                                      torch.nn.Linear(width, width), torch.nn.Tanh(),
                                      torch.nn.Linear(width, 2)).double()

    def forward(self, t):
        return self.net(2 * (t.reshape(-1, 1) - self.start) / self.span - 1)


def neural_observations(t, y, seed, steps=400, learning_rate=.01):
    """Observation MSE only. No physical parameters or held trajectory can enter."""
    t, y = validate(t, y)
    with torch.random.fork_rng():
        torch.manual_seed(seed)
        model = ObservationField(t[0], t[-1])
    tx, target = torch.tensor(t), torch.tensor(y)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    losses = []
    for _ in range(steps):
        optimizer.zero_grad()
        loss = (model(tx) - target).square().mean()
        if not torch.isfinite(loss):
            raise FloatingPointError('Nonfinite observation loss')
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
    with torch.no_grad():
        fitted = model(tx).numpy()
    return fitted, {'losses': losses, 'seed': seed, 'steps': steps,
                    'parameters': sum(p.numel() for p in model.parameters())}, model


def rollout(t, initial, coef, method='RK45', rtol=1e-8, atol=1e-10, max_calls=6000):
    """Return explicit failure receipts; never discard fitted nonlinear terms."""
    calls = 0
    coef = np.asarray(coef, dtype=float)
    if coef.shape != (10,) or not np.isfinite(coef).all():
        raise ValueError('Ten finite physical coefficients required')

    def rhs(_, state):
        nonlocal calls
        calls += 1
        if calls > max_calls:
            raise FloatingPointError('rhs_budget')
        if not np.isfinite(state).all() or np.max(np.abs(state)) > 1e6:
            raise FloatingPointError('state_cap')
        return [state[1], float(library(state) @ coef)]
    try:
        with np.errstate(over='raise', invalid='raise'):
            sol = solve_ivp(rhs, (t[0], t[-1]), initial, t_eval=t, method=method, rtol=rtol, atol=atol)
        if not sol.success or sol.y.shape != (2, len(t)) or not np.isfinite(sol.y).all():
            return None, {'status': 'failed', 'reason': sol.message, 'calls': calls, 'method': method}
        return sol.y.T, {'status': 'ok', 'calls': calls, 'method': method}
    except FloatingPointError as error:
        return None, {'status': 'failed', 'reason': str(error), 'calls': calls, 'method': method}
