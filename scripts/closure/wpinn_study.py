"""Frozen, observed-only structured oscillator development protocol."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import traceback
import warnings

import numpy as np
import pysindy as ps
import torch

from world_series.wpinn.structured import (
    NAMES, derivative_system, neural_observations, rollout, sparse_fit,
    spline_observations, weak_system,
)
from world_series.wpinn.systems import simulate_oscillator

SEEDS = [2503, 2521, 2531, 2539, 2543, 2549, 2551, 2557]
LAWS = [(1., 0.), (2., .3), (4., .8)]
CONDITIONS = ['clean', 'noisy', 'sparse', 'missing', 'low_excitation']


def identity():
    paths = sorted(Path('src/world_series').rglob('*.py')) + [Path(__file__), Path('docs/closure/WPINN_PROTOCOL.md')]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'files': hashes, 'sha256': hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()}


def dataset(seed, law_index, condition_index):
    k, c = LAWS[law_index]
    condition = CONDITIONS[condition_index]
    data = []
    for index in range(5):
        sid = seed * 10000 + law_index * 100 + condition_index * 10 + index
        rng = np.random.default_rng(sid)
        held = index >= 3
        t = np.linspace(0, 5, 41 if condition == 'sparse' and not held else 81)
        initial = rng.normal(size=2) * (.1 if condition == 'low_excitation' and not held else 1.)
        y = simulate_oscillator(k, c, *initial, t)
        if not held and condition != 'clean':
            y = y + .1 * rng.normal(size=y.shape)
        if not held and condition == 'missing':
            keep = np.r_[True, rng.random(len(t) - 2) >= .3, True]
            t, y = t[keep], y[keep]
        data.append({'id': sid, 'role': 'train' if index < 2 else 'selection' if index == 2 else 'evaluation',
                     't': t, 'y': y})
    return data


def official_design(trajectories, weak, seed):
    aa, bb = [], []
    previous = np.random.get_state()
    try:
        np.random.seed(seed)
        for t, y in trajectories:
            base = ps.PolynomialLibrary(degree=3, include_bias=True)
            if weak:
                lib = ps.WeakPDELibrary(function_library=base, spatiotemporal_grid=t,
                                       K=32, H_xt=[1.25])
                design = np.asarray(lib.fit_transform(y))
                target = np.asarray(lib.convert_u_dot_integral(y))[:, 1]
            else:
                lib = base
                design = np.asarray(lib.fit_transform(y))
                target = ps.FiniteDifference(order=2)._differentiate(y, t)[:, 1]
            assert lib.get_feature_names() == ['1', 'x0', 'x1', 'x0^2', 'x0 x1', 'x1^2',
                                               'x0^3', 'x0^2 x1', 'x0 x1^2', 'x1^3']
            aa.append(design)
            bb.append(target)
    finally:
        np.random.set_state(previous)
    return np.vstack(aa), np.concatenate(bb)


def score(data, coef):
    pred, receipt = rollout(data['t'], data['y'][0], coef)
    return {**receipt, 'value': None if pred is None else float(np.mean((pred - data['y']) ** 2))}


def cell(seed, law_index, condition_index, out):
    started = time.perf_counter()
    out.mkdir()
    data = dataset(seed, law_index, condition_index)
    np.savez_compressed(out / 'observations.npz', **{f'{i}_{field}': d[field] for i, d in enumerate(data) for field in ('t', 'y')})
    raw = [(d['t'], d['y']) for d in data[:2]]
    spline, neural, smoothing = [], [], []
    for i, (t, y) in enumerate(raw):
        smooth, spline_info = spline_observations(t, y)
        spline.append((t, smooth))
        fitted, neural_info, model = neural_observations(t, y, data[i]['id'], steps=400)
        neural.append((t, fitted))
        torch.save(model.state_dict(), out / f'field_{i}.pt')
        smoothing.append({'spline': spline_info, 'neural': neural_info})
    np.savez_compressed(out / 'smoothed.npz', **{f'{method}_{i}': y for method, trajectories in [('spline', spline), ('neural', neural)] for i, (_, y) in enumerate(trajectories)})
    designs = {'raw_derivative': derivative_system(raw), 'raw_weak': weak_system(raw),
               'spline_weak': weak_system(spline), 'neural_weak': weak_system(neural),
               'neural_derivative': derivative_system(neural),
               'official_derivative': official_design(raw, False, seed),
               'official_weak': official_design(raw, True, seed)}
    np.savez_compressed(out / 'designs.npz', **{f'{name}_{part}': value for name, pair in designs.items() for part, value in zip(('a', 'b'), pair)})
    methods = [(name, name, 'none', False) for name in ('raw_derivative', 'raw_weak', 'spline_weak', 'neural_weak', 'neural_derivative')]
    methods += [(f'neural_weak_{prior}', 'neural_weak', prior, False) for prior in ('odd', 'passive', 'wrong_conservation')]
    methods += [('neural_weak_dense', 'neural_weak', 'none', True),
                ('known_support', 'raw_derivative', 'known_support', True),
                ('official_derivative', 'official_derivative', 'none', False),
                ('official_weak', 'official_weak', 'none', False)]
    results = []
    k, c = LAWS[law_index]
    truth = np.zeros(10)
    truth[1:3] = [-k, -c]
    for name, design, structure, dense in methods:
        tick = time.perf_counter()
        a, b = designs[design]
        candidates = []
        for threshold in ([0.] if dense else [0., .02, .1]):
            if name.startswith('official'):
                with warnings.catch_warnings(record=True) as captured:
                    optimizer = ps.STLSQ(threshold=threshold, alpha=0., normalize_columns=False, max_iter=20)
                    optimizer.fit(a, b)
                coef = optimizer.coef_.reshape(-1)
                details = {'warnings': [str(w.message) for w in captured]}
            else:
                coef, details = sparse_fit(a, b, threshold, structure)
            candidates.append({'threshold': threshold, 'coefficients': coef.tolist(),
                               'details': details, 'selection': score(data[2], coef)})
        chosen = min(range(len(candidates)), key=lambda i: float('inf') if candidates[i]['selection']['value'] is None else candidates[i]['selection']['value'])
        coef = np.array(candidates[chosen]['coefficients'])
        evaluations = [score(d, coef) for d in data[3:]]
        value = None if any(e['value'] is None for e in evaluations) else float(np.mean([e['value'] for e in evaluations]))
        results.append({'method': name, 'candidates': candidates, 'chosen': chosen,
                        'evaluations': evaluations, 'value': value,
                        'coefficient_squared_error': float(np.sum((coef - truth) ** 2)),
                        'exact_support': bool(np.array_equal(abs(coef) > 1e-6, abs(truth) > 1e-6)),
                        'fit_select_evaluate_seconds': time.perf_counter() - tick})
    result = {'seed': seed, 'law': [k, c], 'condition': CONDITIONS[condition_index],
              'trajectory_ids': [{'id': d['id'], 'role': d['role']} for d in data],
              'names': NAMES, 'smoothing': smoothing, 'methods': results,
              'elapsed_seconds': time.perf_counter() - started}
    (out / 'results.json').write_text(json.dumps(result, indent=2, allow_nan=False))
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True)
    p.add_argument('--profile', action='store_true')
    args = p.parse_args()
    torch.set_num_threads(1)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    frozen = identity()
    (out / 'identity.json').write_text(json.dumps(frozen, indent=2))
    jobs = [(2499, 1, 1)] if args.profile else [(s, l, c) for s in SEEDS for l in range(3) for c in range(5)]
    started = time.perf_counter()
    try:
        for index, (seed, law, condition) in enumerate(jobs):
            assert identity()['sha256'] == frozen['sha256'], 'Source changed during campaign'
            result = cell(seed, law, condition, out / f'{seed}_{law}_{condition}')
            print(json.dumps({'completed': index + 1, 'total': len(jobs), 'seconds': result['elapsed_seconds']}), flush=True)
        (out / 'complete.json').write_text(json.dumps({'cells': len(jobs), 'elapsed_seconds': time.perf_counter() - started}))
    except Exception:
        (out / 'failure.txt').write_text(traceback.format_exc())
        raise


if __name__ == '__main__':
    main()
