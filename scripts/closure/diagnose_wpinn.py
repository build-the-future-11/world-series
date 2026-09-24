"""Retrospective finite interventions; preserves all historical failure values."""
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
from world_series.wpinn.library import library_matrix
from world_series.wpinn.sparse_fit import thresholded_lstsq
from world_series.wpinn.structured import NAMES, rollout, trapezoid_weights
from world_series.wpinn.systems import make_trajectory
from world_series.wpinn.weak_form import test_functions


def assess(t, clean, coef, method='RK45'):
    pred, receipt = rollout(t, clean[0], coef, method=method)
    receipt['mse'] = None if pred is None else float(np.mean((pred - clean) ** 2))
    return receipt


def diagnose(source):
    data = json.loads(source.read_text())
    failures = [r for r in data['rows'] if r['value'] is None]
    assert len(failures) == 17
    rows = []
    for row in failures:
        k, c, noise = map(float, re.fullmatch(r'k([^/]+)/c([^/]+)/noise(.+)', row['condition']).groups())
        train = make_trajectory(row['seed'] * 100 + 1, k, c, noise)
        held = make_trajectory(row['seed'] * 100 + 2, k, c, 0.)
        coef = np.array([row['coefficients'].get(n, 0.) for n in NAMES])
        record = {'seed': row['seed'], 'method': row['method'], 'condition': row['condition'],
                  'historical_value': None, 'coefficients': coef.tolist(), 'solvers': {}}
        for solver in ('RK45', 'DOP853', 'Radau'):
            record['solvers'][solver] = assess(held.times, held.observations, coef, solver)
        linear_only = coef.copy()
        linear_only[[3, 4, 5]] = 0
        true_linear = coef.copy()
        true_linear[1:3] = [-k, -c]
        record['oracle_interventions'] = {
            'remove_quadratic': assess(held.times, held.observations, linear_only),
            'replace_linear_with_truth': assess(held.times, held.observations, true_linear)}
        record['quadrature_factorial'] = []
        if row['method'] in ('weak', 'wrong_conservation'):
            t, y = train.times, train.observations
            theta, names, scales = library_matrix(y)
            psi = test_functions(t, n=6)
            span = t[-1] - t[0] + 1e-12
            s = (t - t[0]) / span
            m = np.arange(1, 7)
            analytic = (2 * np.pi * (np.sin(np.pi*s)*np.cos(np.pi*s))[:, None]
                        * np.sin(np.pi*s[:, None]*m)
                        + np.sin(np.pi*s)[:, None]**2 * np.pi*m
                        * np.cos(np.pi*s[:, None]*m)) / span
            for weighting, weights in [('gradient', np.gradient(t)), ('trapezoid', trapezoid_weights(t))]:
                for differentiation, derivative in [('gradient', np.gradient(psi, t, axis=0)), ('analytic', analytic)]:
                    a = (psi * weights[:, None]).T @ theta
                    b = -(derivative * weights[:, None]).T @ y[:, 1]
                    fit = dict(zip(names, thresholded_lstsq(a, b, thresh=.05) / scales))
                    if row['method'] == 'wrong_conservation':
                        fit['v'] = 0.
                    vector = np.array([fit.get(n, 0.) for n in NAMES])
                    if weighting == differentiation == 'gradient':
                        assert np.allclose(vector, coef, atol=1e-10, rtol=1e-10)
                    record['quadrature_factorial'].append({
                        'weights': weighting, 'test_derivative': differentiation,
                        'coefficients': vector.tolist(),
                        'singular_values': np.linalg.svd(a, compute_uv=False).tolist(),
                        'rollout': assess(held.times, held.observations, vector)})
        rows.append(record)
        print(f"Completed {len(rows)}/{len(failures)}", flush=True)
    return {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'rows': rows,
            'scope': 'Retrospective finite interventions; no original metric overwritten; oracle information only in explicitly labeled diagnostics.'}


if __name__ == '__main__':
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as f:
        json.dump(diagnose(Path('campaigns/closure-20260924/wpinn.json')), f, indent=2)
