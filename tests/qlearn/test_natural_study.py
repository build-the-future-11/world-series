from pathlib import Path
import torch
from world_series.qlearn.natural_study import natural_tasks, run_experiment
from world_series.qlearn.regression import RecurrentUpdatePolicy
from world_series.evaluation.runner import create_run

DATA = Path(__file__).resolve().parents[2] / 'data/optdigits'

def test_natural_split_is_disjoint_and_writer_sources_are_preserved():
    train, selection, held, records = natural_tasks(DATA, 11, 3, 8)
    assert {t.family for t in train}.isdisjoint({t.family for t in selection + held})
    assert {t.family for t in selection}.isdisjoint({t.family for t in held})
    for pair in {(tuple(r['pair'])) for r in records}:
        rs = [r for r in records if tuple(r['pair']) == pair]
        if rs[0]['role'] == 'evaluation':
            assert rs[0]['source'] == 'optdigits.tra' and rs[1]['source'] == 'optdigits.tes'
        else:
            assert set(rs[0]['row_ids']).isdisjoint(rs[1]['row_ids'])

def test_reset_state_ablation_matches_parameters_but_removes_cross_step_state():
    torch.manual_seed(1)
    full = RecurrentUpdatePolicy(hidden=3)
    reset = RecurrentUpdatePolicy(hidden=3, reset_state=True)
    reset.load_state_dict(full.state_dict())
    assert sum(p.numel() for p in full.parameters()) == sum(p.numel() for p in reset.parameters())
    f = torch.randn(8, 4, dtype=torch.float64)
    _, _, s = full(f)
    a, _, _ = reset(f, s)
    b, _, _ = full(f, None)
    c, _, _ = full(f, s)
    assert torch.equal(a, b) and not torch.equal(a, c)

def test_natural_matrix_preserves_every_comparator(tmp_path):
    torch.set_num_threads(1)
    cfg = dict(project='qlearn', experiment='test-natural', split='dev', seed=11, device='cpu',
               budget=dict(max_steps=1000, max_candidate_evals=20, max_wall_seconds=60),
               params=dict(data_root=str(DATA), width=3, hidden=3, examples=8,
                           rates=[.01], outer_rates=[.001], train_steps=2, meta_steps=1, horizons=[2]))
    result = run_experiment(cfg, create_run(tmp_path, cfg))
    assert result['status'] == 'SUCCEEDED'
    assert len(result['trials']) == 9 and len(result['rows']) == 18
    assert result['cost']['candidate_evals'] == 9
