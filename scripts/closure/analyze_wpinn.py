"""Audit recorded choices, input splits, checkpoint predictions and every rollout."""
import hashlib
import importlib.util
import importlib.metadata
import json
from pathlib import Path

import numpy as np
import torch
from world_series.wpinn.structured import ObservationField, neural_observations, rollout


def main():
    torch.set_num_threads(1)
    spec = importlib.util.spec_from_file_location('wpinn_study', 'scripts/closure/wpinn_study.py')
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    root = Path('campaigns/wpinn-structured-v1')
    complete = json.loads((root / 'complete.json').read_text())
    assert complete['cells'] == 120
    frozen = json.loads((root / 'identity.json').read_text())
    for filename, digest in frozen['files'].items():
        assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == digest
    qualification = json.loads(Path('docs/closure/WPINN_PYSINDY_QUALIFICATION.json').read_text())
    distribution = importlib.metadata.distribution('pysindy')
    assert distribution.version == qualification['pysindy_version']
    for filename, digest in qualification['source_files'].items():
        assert hashlib.sha256(distribution.locate_file(filename).read_bytes()).hexdigest() == digest
    groups = {}
    ids = set()
    replayed, checkpoints, selections = 0, 0, 0
    hashes = {}
    cells = sorted(root.glob('*_*_*/results.json'))
    assert len(cells) == 120
    for path in cells:
        result = json.loads(path.read_text())
        seed, law, condition = map(int, path.parent.name.split('_'))
        fresh = study.dataset(seed, law, condition)
        arrays = np.load(path.parent / 'observations.npz')
        smooth = np.load(path.parent / 'smoothed.npz')
        for i, d in enumerate(fresh):
            assert d['id'] not in ids
            ids.add(d['id'])
            assert result['trajectory_ids'][i] == {'id': d['id'], 'role': d['role']}
            for field in ('t', 'y'):
                assert np.array_equal(arrays[f'{i}_{field}'], d[field])
            if i < 2:
                model = ObservationField(d['t'][0], d['t'][-1])
                model.load_state_dict(torch.load(path.parent / f'field_{i}.pt', weights_only=True))
                with torch.no_grad():
                    pred = model(torch.tensor(d['t'])).numpy()
                assert np.array_equal(pred, smooth[f'neural_{i}'])
                assert len(result['smoothing'][i]['neural']['losses']) == 400
                assert np.isfinite(result['smoothing'][i]['neural']['losses']).all()
                checkpoints += 1
        for method in result['methods']:
            candidates = method['candidates']
            for candidate in candidates:
                receipt = study.score(fresh[2], np.array(candidate['coefficients']))
                assert receipt == candidate['selection']
                replayed += 1
            chosen = min(range(len(candidates)), key=lambda i: float('inf') if candidates[i]['selection']['value'] is None else candidates[i]['selection']['value'])
            assert chosen == method['chosen']
            selections += 1
            coef = np.array(candidates[chosen]['coefficients'])
            for d, old in zip(fresh[3:], method['evaluations']):
                assert study.score(d, coef) == old
                replayed += 1
            entries = groups.setdefault(method['method'], [])
            entries.append({'seed': seed, 'law': result['law'], 'condition': result['condition'],
                            'value': method['value'], 'support': method['exact_support'],
                            'coefficient_error': method['coefficient_squared_error'],
                            'selection_failed': all(c['selection']['value'] is None for c in candidates),
                            'selected_threshold': candidates[chosen]['threshold']})
        for artifact in path.parent.iterdir():
            hashes[str(artifact.relative_to(root))] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    # Same-host replay, explicitly not independent replication.
    first = cells[0]
    original = json.loads(first.read_text())
    data = np.load(first.parent / 'observations.npz')
    fitted, trace, model = neural_observations(data['0_t'], data['0_y'], original['trajectory_ids'][0]['id'])
    assert trace == original['smoothing'][0]['neural']
    saved = torch.load(first.parent / 'field_0.pt', weights_only=True)
    assert all(torch.equal(value, saved[key]) for key, value in model.state_dict().items())
    summaries = {}
    rng = np.random.default_rng(250924)
    for method, rows in groups.items():
        failed = sum(row['value'] is None for row in rows)
        seed_values = [float(np.mean([r['value'] for r in rows if r['seed'] == s])) for s in study.SEEDS] if not failed else None
        interval = None if seed_values is None else np.quantile(np.mean(rng.choice(seed_values, (10000, 8)), axis=1), [.025, .975]).tolist()
        summaries[method] = {'cells': len(rows), 'failed_cells': failed,
                             'selection_failed_cells': sum(r['selection_failed'] for r in rows),
                             'primary_mean': None if failed else float(np.mean(seed_values)),
                             'descriptive_seed_bootstrap': interval,
                             'successful_cells_mean_only': float(np.mean([r['value'] for r in rows if r['value'] is not None])),
                             'exact_support_fraction': float(np.mean([r['support'] for r in rows])),
                             'seed_means': seed_values}
    out = {'source_identity': frozen, 'audit': {'files_hashed': len(hashes), 'unique_trajectory_ids': len(ids),
           'checkpoint_predictions': checkpoints, 'rollouts_replayed': replayed,
           'threshold_selections': selections, 'one_full_observation_fit_exact_replay': True},
           'summary': summaries, 'rows': groups, 'file_hashes': hashes,
           'scope': 'Same-host development audit; conditional successful-cell means are not complete primary results.'}
    Path('docs/closure/WPINN_RESULTS.json').write_text(json.dumps(out, indent=2, allow_nan=False))
    lines = ['# Structured WPINN development results', '',
             'DRAFT_NOT_AUTHORIZED for confirmation. Same-host audit; finite oscillator scope.', '',
             '| Method | Failed /120 | Primary mean MSE | Successful-cell mean only | Exact support |',
             '|---|---:|---:|---:|---:|']
    for method, s in summaries.items():
        primary = 'INCOMPLETE' if s['primary_mean'] is None else f"{s['primary_mean']:.8g}"
        lines.append(f"| {method} | {s['failed_cells']} | {primary} | {s['successful_cells_mean_only']:.8g} | {s['exact_support_fraction']:.3f} |")
    lines += ['', f'Audit: {replayed} rollout receipts replay exactly; {selections} threshold selections verified; '
               f'{checkpoints} saved fields reproduce predictions; all 600 whole-trajectory IDs are disjoint. '
               'One complete 400-update observation fit reproduces its trace and checkpoint exactly.', '',
               'Physical constraints and known support provide additional information. Neural fields fit '
               'observations only; this is not joint physics-informed neural training. No general PDE, '
               'novelty, independent replication, or publication-ready claim follows from these results.']
    Path('docs/closure/WPINN_RESULTS.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'audit': out['audit'], 'summary': summaries}, indent=2))


if __name__ == '__main__':
    main()
