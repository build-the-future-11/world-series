#!/usr/bin/env python3
"""Official Celo2 update with PyTorch optimizee gradients; no algorithm port."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
# Isolated external dependencies; preserve the reference environment's torch.
sys.path.append(str(ROOT / '.venv-celo2/lib/python3.12/site-packages'))
import jax
jax.config.update('jax_enable_x64', True)
import jax.numpy as jnp
import numpy as np
import optax
import torch
from celo2_optax import load_checkpoint, scale_by_celo2
from world_series.qlearn.natural_study import natural_tasks
from world_series.qlearn.regression import trajectory_record

torch.set_num_threads(1)

def optimizer(theta, lr):
    return optax.multi_transform(
        {'celo2': optax.chain(scale_by_celo2(theta, orthogonalize=True),
                             optax.add_decayed_weights(.01), optax.scale_by_learning_rate(lr)),
         'adam': optax.adamw(lr, b1=.9, b2=.95, weight_decay=.01)},
        lambda parameters: {k: 'adam' if v.ndim <= 1 else 'celo2' for k, v in parameters.items()})

def trajectory(task, steps, tx, update):
    model = task.build()
    parameters = {k: jnp.asarray(p.detach().numpy()) for k, p in model.named_parameters()}
    state = tx.init(parameters)
    with torch.no_grad():
        curve = [float((model(task.query_x) - task.query_y).square().mean())]
    support, elapsed = [], [0.]
    start = time.perf_counter()
    for _ in range(steps):
        model.zero_grad(set_to_none=True)
        objective = (model(task.support_x) - task.support_y).square().mean()
        objective.backward()
        gradients = {k: jnp.asarray(p.grad.numpy()) for k, p in model.named_parameters()}
        updates, state = update(gradients, state, parameters)
        parameters = optax.apply_updates(parameters, updates)
        with torch.no_grad():
            for k, p in model.named_parameters():
                p.copy_(torch.from_numpy(np.array(parameters[k], copy=True)))
            curve.append(float((model(task.query_x) - task.query_y).square().mean()))
        support.append(float(objective.detach()))
        elapsed.append(time.perf_counter() - start)
        if not np.isfinite(support[-1]) or support[-1] / task.scale > 1e6:
            break
    raw = dict(query_losses=curve, support_losses=support, elapsed_seconds=elapsed,
               gradient_evaluations=len(support), forward_evaluations=1+2*len(support))
    row = trajectory_record(task, 'official_celo2', raw, steps)
    with torch.no_grad():
        row['accuracy'] = float(((model(task.query_x) >= 0) == (task.query_y >= 0)).double().mean())
    return row

def main(plan_path, output):
    output.mkdir(parents=True, exist_ok=False)
    theta_path = ROOT / 'external/celo2/theta.state'
    theta = load_checkpoint(str(theta_path))
    plan = json.loads(plan_path.read_text())
    rates = plan['cells'][0]['params']['rates']
    transforms = {rate: optimizer(theta, rate) for rate in rates}
    updates = {rate: jax.jit(tx.update) for rate, tx in transforms.items()}
    # Test the official transformation/bridge before using any benchmark outcome.
    test_parameters = {'weight': jnp.asarray([[.2, -.4], [.1, .3]], dtype=jnp.float64),
                       'bias': jnp.asarray([.1, -.2], dtype=jnp.float64)}
    test_gradients = jax.tree.map(lambda x: jnp.ones_like(x)*.1, test_parameters)
    tx = transforms[rates[0]]; update = updates[rates[0]]
    initial = tx.init(test_parameters)
    first, next_state = update(test_gradients, initial, test_parameters)
    repeated, repeated_state = update(test_gradients, initial, test_parameters)
    assert all(np.array_equal(np.asarray(a), np.asarray(b)) for a, b in
               zip(jax.tree.leaves((first,next_state)), jax.tree.leaves((repeated,repeated_state))))
    assert all(np.isfinite(np.asarray(v)).all() for v in jax.tree.leaves(first))
    # Isolated bias branch must agree with the explicit AdamW first-step formula.
    bias = np.asarray(test_parameters['bias']); gradient = np.asarray(test_gradients['bias'])
    expected_bias_update = -rates[0]*(gradient/(np.abs(gradient)+1e-8)+.01*bias)
    assert np.allclose(np.asarray(first['bias']), expected_bias_update, rtol=1e-10, atol=1e-12)
    (output/'compatibility.json').write_text(json.dumps({
        'official_transform_replay_exact': True, 'bias_branch_matches_adamw_formula': True,
        'finite_matrix_and_bias_updates': True, 'dtype': 'float64 optimizee; upstream mixed-precision accumulators',
        'scope': 'Transformation and parameter bridge checks; not a full paper reproduction'}, indent=2)+'\n')
    rows, trials = [], []
    for cfg in plan['cells']:
        p = cfg['params']; seed = cfg['seed']
        _, selection, held, _ = natural_tasks(ROOT / p['data_root'], seed, p['width'], p['examples'])
        scores = []
        for rate in rates:
            rs = [trajectory(t, p['train_steps'], transforms[rate], updates[rate]) for t in selection]
            score = float(np.mean([r['gradient_step_auc'] for r in rs])) if all(not r['diverged'] for r in rs) else None
            trials.append({'seed': seed, 'rate': rate, 'score': score, 'rows': rs})
            scores.append(score if score is not None else float('inf'))
        if not any(np.isfinite(scores)):
            raise RuntimeError(f'All official Celo2 tuning trials failed for seed {seed}')
        rate = rates[int(np.argmin(scores))]
        for horizon in p['horizons']:
            for task in held:
                row = trajectory(task, horizon, transforms[rate], updates[rate])
                row['training_seed'] = seed; row['selected_rate'] = rate
                rows.append(row)
        (output / f'seed-{seed}.json').write_text(json.dumps({'rows': [r for r in rows if r['training_seed'] == seed],
            'trials': [r for r in trials if r['seed'] == seed]}, indent=2, allow_nan=False) + '\n')
        print(json.dumps({'seed': seed, 'selected_rate': rate, 'rows': len(rows)}), flush=True)
    result = {'status': 'SUCCEEDED', 'research_outcome': 'INCONCLUSIVE', 'rows': rows, 'trials': trials,
        'weights_sha256': hashlib.sha256(theta_path.read_bytes()).hexdigest(),
        'upstream_source_sha256': hashlib.sha256((ROOT/'external/celo2/celo2_optax.py').read_bytes()).hexdigest(),
        'scope': 'Official pretrained Celo2; author-selected external meta-training, not matched training compute. PyTorch/JAX bridge timing includes compilation and transfers; no wall-time superiority claim.',
        'jax_version': jax.__version__, 'optax_version': optax.__version__}
    (output / 'results.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    main(args.plan, args.output)
