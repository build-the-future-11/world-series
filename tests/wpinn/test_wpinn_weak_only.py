
from world_series.wpinn.systems import make_trajectory
from world_series.wpinn.train import weak_only_fit, fit_with_structure

def test_weak_only_no_crash_and_wrong_conservation_labeled():
    traj = make_trajectory(0, k=2.0, c=0.3, noise=0.0)
    coef, r, support = weak_only_fit(traj)
    assert "q" in coef
    wcoef, _, _ = fit_with_structure(traj, enforce_conservation=True)
    assert wcoef["v"] == 0.0
