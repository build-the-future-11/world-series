import json

from world_series.evaluation.runner import create_run
from world_series.qlearn.regression_study import run_experiment, summarize


def test_versioned_study_runs_all_declared_cells_and_preserves_artifacts(tmp_path):
    cfg = {'project': 'qlearn', 'experiment': 'test-neural-contract', 'seed': 11,
           'device': 'cpu', 'split': 'dev',
           'budget': {'max_steps': 500, 'max_wall_seconds': 60, 'max_artifact_bytes': 5_000_000},
           'params': {'training_seeds': [11], 'baseline_learning_rates': [0.01],
                      'outer_learning_rates': [0.001], 'evaluation_horizons': [2, 3],
                      'variants': ['full', 'no_budget'], 'adaptation_steps': 2,
                      'meta_steps': 1, 'controller_hidden': 4, 'controller_layers': 2,
                      'train_width': 3, 'evaluation_widths': [3, 5],
                      'train_tasks': 2, 'selection_tasks': 1, 'evaluation_tasks': 1,
                      'input_dim': 2, 'support_size': 7, 'query_size': 9}}
    run = create_run(tmp_path, cfg)
    result = run_experiment(cfg, run)
    assert result['status'] == 'SUCCEEDED'
    assert result['expected_evaluation_rows'] == result['actual_evaluation_rows'] == 20
    assert len(result['all_tuning_trials']) == 5
    assert result['failed_seed_methods'] == []
    # Baseline selection + meta-training + policy selection + held evaluation.
    assert result['cost']['steps_used'] == 6 + 8 + 4 + 50
    assert result['cost']['candidate_evals'] == 5
    assert result['cost']['artifact_bytes'] > 0
    import hashlib
    for ref in result['artifacts']:
        assert hashlib.sha256((run.path / ref['path']).read_bytes()).hexdigest() == ref['sha256']
    manifest = json.loads((run.path / 'artifacts/neural-study/input_manifest.json').read_text())
    assert set(manifest['training_families']).isdisjoint(manifest['evaluation_families'])
    assert set(manifest['selection_families']).isdisjoint(manifest['evaluation_families'])


def test_failed_member_does_not_disappear_from_summary():
    rows = [{'method': 'full', 'width': 4, 'requested_steps': 3, 'training_seed': 11,
             'diverged': False, 'complete': True, 'gradient_step_auc': 2.0,
             'measured_wall_time_auc': 0.1, 'normalized_final_loss': 0.5},
            {'method': 'full', 'width': 4, 'requested_steps': 3, 'training_seed': 12,
             'diverged': True, 'complete': False, 'gradient_step_auc': None,
             'measured_wall_time_auc': None, 'normalized_final_loss': None}]
    result = summarize(rows)[0]
    assert result['attempted_tasks'] == 2
    assert result['diverged_tasks'] == result['incomplete_tasks'] == 1
    assert result['mean_gradient_step_auc'] is None
    assert result['mean_normalized_final_loss'] is None
