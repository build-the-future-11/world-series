import pytest
import torch

from world_series.core.contracts import WorldSeriesError
from world_series.qlearn.functional import np_to_torch_spd
from world_series.qlearn.meta_train import finite_diff_check
from world_series.qlearn.policy import BoundedDiagonalPolicy
from world_series.qlearn.tasks import build_tasks


def test_bounds_and_reset():
    p = BoundedDiagonalPolicy()
    feats = torch.zeros(5, 4, dtype=torch.float64)
    eta, d = p(feats)
    assert float(eta) > 0 and torch.all(d > 0)
    p.reset_state()


def test_invalid_bounds():
    with pytest.raises(WorldSeriesError):
        BoundedDiagonalPolicy(eta_bounds=(-1, 0.1))


def test_meta_grad_fd():
    tasks = build_tasks(0, n=1, dim=3)
    t = tasks[0]
    A, b, x0 = np_to_torch_spd(t.optimizee.A, t.optimizee.b, t.optimizee.x0)
    policy = BoundedDiagonalPolicy(hidden=8).double()
    err = finite_diff_check(policy, A, b, x0, eps=1e-4)
    assert err < 5e-2
