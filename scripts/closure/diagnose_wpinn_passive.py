"""Post-study stiff-solver diagnostic, never a replacement primary estimate."""
import json
from pathlib import Path

import numpy as np
from world_series.wpinn.structured import rollout

rows = []
for path in sorted(Path('campaigns/wpinn-structured-v1').glob('*_*_*/results.json')):
    data = json.loads(path.read_text())
    for method in data['methods']:
        if method['method'] != 'neural_weak_passive' or method['value'] is not None:
            continue
        coef = np.array(method['candidates'][method['chosen']]['coefficients'])
        arrays = np.load(path.parent / 'observations.npz')
        for i, old in enumerate(method['evaluations'], start=3):
            if old['status'] == 'ok':
                continue
            t, y = arrays[f'{i}_t'], arrays[f'{i}_y']
            retries = {}
            for solver in ('Radau', 'BDF'):
                pred, receipt = rollout(t, y[0], coef, method=solver)
                receipt['value'] = None if pred is None else float(np.mean((pred - y) ** 2))
                if pred is not None:
                    energy = .5 * (pred[:, 1] ** 2 - coef[1] * pred[:, 0] ** 2)
                    receipt['max_energy_increase'] = float(np.max(np.diff(energy)))
                retries[solver] = receipt
            rows.append({'cell': path.parent.name, 'held_index': i, 'original': old,
                         'coefficients': coef.tolist(), 'retries': retries})
assert len(rows) == 4
out = Path('campaigns/wpinn-passive-diagnostic-v1')
out.mkdir(exist_ok=False)
(out / 'results.json').write_text(json.dumps({'rows': rows, 'scope':
    'Post-study Radau/BDF retries of all four failed held trajectories in three passive cells. Same 6000-call and state caps. Original primary failures remain unchanged.'}, indent=2))
print(json.dumps(rows, indent=2))
