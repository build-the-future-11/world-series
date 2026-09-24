from types import SimpleNamespace

import numpy as np
import pytest
import torch

from world_series import projects
from world_series.qlearn.baselines import adamw_trajectory
from world_series.qlearn.tasks import build_tasks
from world_series.core.artifacts import ArtifactStore
from world_series.core.contracts import WorldSeriesError
from world_series.qlearn.evaluate import run_experiment


def test_adamw_matches_independent_torch_optimizer_with_weight_decay():
    task = build_tasks(19, n=1, dim=3)[0]
    actual, curve = adamw_trajectory(task, 6, eta=0.02, wd=0.3)
    x = torch.tensor(task.optimizee.x0, dtype=torch.float64, requires_grad=True)
    a = torch.tensor(task.optimizee.A, dtype=torch.float64)
    b = torch.tensor(task.optimizee.b, dtype=torch.float64)
    optimizer = torch.optim.AdamW([x], lr=0.02, weight_decay=0.3)
    expected_curve = []
    for _ in range(6):
        optimizer.zero_grad()
        (0.5 * x @ a @ x + b @ x).backward()
        optimizer.step()
        expected_curve.append(task.optimizee.loss(x.detach().numpy()))
    np.testing.assert_allclose(actual, x.detach().numpy(), rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(curve, expected_curve, rtol=1e-12, atol=1e-12)


def test_dispatch_replays_recorded_seed_after_unrelated_rng_use(monkeypatch):
    def stochastic_runner(cfg, run):
        return {'torch': torch.randn(4).tolist(), 'numpy': np.random.random(4).tolist()}

    monkeypatch.setattr(projects, '_load_runners', lambda: {'qlearn': stochastic_runner})
    run = SimpleNamespace(append_event=lambda *args: None)
    cfg = {'project': 'qlearn', 'seed': 19}
    first = projects.dispatch_run(cfg, run)
    torch.randn(100)
    np.random.random(100)
    assert projects.dispatch_run(cfg, run) == first
    assert projects.dispatch_run({**cfg, 'seed': 20}, run) != first


def test_evaluation_retains_every_trajectory_and_matches_metric_units(tmp_path):
    run = SimpleNamespace(store=ArtifactStore(tmp_path, run_id='test'))
    metrics = run_experiment({'seed': 2, 'params': {
        'n_tasks': 4, 'dim': 3, 'steps': 3, 'long_steps': 5, 'meta_steps': 1,
    }}, run)
    import json
    rows = json.loads((tmp_path / metrics['raw_trajectories']['path']).read_text())
    assert len(rows) == 2 * metrics['n_held']
    assert {r['horizon'] for r in rows} == {3, 5}
    assert not set(metrics['split_families']['train']) & set(metrics['split_families']['dev'])
    short = metrics['held_short']
    assert metrics['auc_delta_vs_best_fixed_finalproxy'] is None
    assert metrics['auc_delta_vs_best_fixed_auc'] == pytest.approx(
        min(short['auc_' + m] for m in ['sgd', 'momentum', 'adamw']) - metrics['primary_value'])
    for method in ['candidate', 'sgd', 'momentum', 'adamw']:
        curves = [r['curves'][method] for r in rows if r['horizon'] == 3]
        assert short[method] == pytest.approx(np.mean([c[-1] for c in curves]))
        assert short['divergence_rates'][method] == short['divergence_counts'][method] / len(curves)


def test_single_family_cannot_be_reused_as_heldout(tmp_path):
    run = SimpleNamespace(store=ArtifactStore(tmp_path, run_id='test'))
    with pytest.raises(WorldSeriesError, match='disjoint train/dev families'):
        run_experiment({'seed': 0, 'params': {'n_tasks': 1}}, run)
