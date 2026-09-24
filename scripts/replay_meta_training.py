#!/usr/bin/env python3
"""Replay all 400 original learned-policy trials using archived source and arrays."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]

def same(a, b):
    if isinstance(a, torch.Tensor):
        return a.shape == b.shape and a.dtype == b.dtype and torch.equal(a, b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b

def main(archive_source, output):
    sys.path.insert(0, str(archive_source / 'src'))
    from world_series.qlearn.regression import RegressionTask, RecurrentUpdatePolicy, MetaTrainer
    from world_series.qlearn.regression_study import VARIANTS
    from world_series.core.identity import source_identity
    expected_source = '6a0fa8d2eff817671edba7a1fc806928f46fadb2a2c10a72e7ffc39f1659b924'
    assert source_identity(archive_source)['content_hash'] == expected_source
    output.mkdir(parents=True, exist_ok=True)
    original = ROOT / 'runs/20260923T231444_deaee7ec'
    config = json.loads((original / 'artifacts/neural-study/input_manifest.json').read_text())['config']
    p = config['params']
    source_metrics = json.loads((original / 'metrics.json').read_text())
    hashes = {r['path']: r['sha256'] for r in source_metrics['artifacts']}
    def verified(relative):
        path = original / relative
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != hashes[relative]:
            raise RuntimeError(f'Changed reference artifact {relative}')
        return raw
    torch.set_num_threads(1)
    results = []
    started = time.perf_counter()
    for seed in p['training_seeds']:
        prefix = f'artifacts/neural-study/seed-{seed}'
        data = np.load(io.BytesIO(verified(prefix + '/datasets.npz')))
        metadata = json.loads(verified(prefix + '/datasets.json'))
        tasks = [RegressionTask(m['task_id'], m['family'], m['initialization_seed'], m['width'],
                 *(torch.tensor(data[f'task_{i}_{f}']) for f in ['support_x', 'support_y', 'query_x', 'query_y']))
                 for i, m in enumerate(metadata[:p['train_tasks']])]
        for variant in p['variants']:
            for trial, rate in enumerate(p['outer_learning_rates']):
                receipt = output / f'{seed}-{variant}-{trial:02}.json'
                expected_bytes = verified(prefix + f'/{variant}-trial-{trial:02}.pt')
                expected = torch.load(io.BytesIO(expected_bytes), map_location='cpu', weights_only=True)
                reference = json.loads(verified(prefix + f'/{variant}-trial-{trial:02}.json'))
                checkpoint_hash = hashlib.sha256(expected_bytes).hexdigest()
                if receipt.exists():
                    prior = json.loads(receipt.read_text())
                    if prior['reference_checkpoint_sha256'] != checkpoint_hash or prior['source_content_hash'] != expected_source:
                        raise RuntimeError('Resume identity mismatch')
                    results.append(prior)
                    continue
                torch.manual_seed(seed)
                policy = RecurrentUpdatePolicy(hidden=p['controller_hidden'], layers=p['controller_layers'], **VARIANTS[variant])
                trainer = MetaTrainer(policy, lr=rate)
                history = []; failure = None; trial_started = time.perf_counter()
                try:
                    for _ in range(p['meta_steps']):
                        history.append(trainer.step(tasks, p['adaptation_steps']))
                except FloatingPointError as exc:
                    failure = str(exc)
                actual = torch.load(io.BytesIO(trainer.checkpoint()), map_location='cpu', weights_only=True)
                matched = all(same(actual[k], expected[k]) for k in ['policy', 'optimizer', 'completed_steps'])
                history_matched = same(history, reference['training_history'])
                failure_matched = failure == reference['trial']['failure']
                record = {'seed': seed, 'variant': variant, 'trial': trial,
                          'source_content_hash': expected_source, 'reference_checkpoint_sha256': checkpoint_hash,
                          'parameters_optimizer_counters_exact': matched, 'training_history_exact': history_matched,
                          'failure_exact': failure_matched, 'failure': failure,
                          'completed_meta_steps': actual['completed_steps'],
                          'elapsed_seconds': time.perf_counter() - trial_started}
                receipt.write_text(json.dumps(record, indent=2) + '\n')
                results.append(record)
                print(json.dumps(record), flush=True)
    expected_trials = len(p['training_seeds']) * len(p['variants']) * len(p['outer_learning_rates'])
    result = {'scope': 'Same-host full meta-training replay; not independent replication',
              'expected_trials': expected_trials, 'replayed_trials': len(results),
              'all_exact': len(results) == expected_trials and all(r['parameters_optimizer_counters_exact'] and r['training_history_exact'] and r['failure_exact'] for r in results),
              'elapsed_seconds_this_invocation': time.perf_counter() - started, 'trials': results}
    (output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    return 0 if result['all_exact'] else 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.source, args.output))
