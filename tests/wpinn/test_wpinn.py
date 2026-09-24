
from world_series.wpinn.systems import make_trajectory
from world_series.wpinn.constraints import check_conservation, check_dissipation
def test_energy_structure():
    u = make_trajectory(0, 2.0, 0.0)
    d = make_trajectory(1, 2.0, 0.4)
    assert check_conservation(u)["ok"]
    assert not check_conservation(d)["ok"]
    assert check_dissipation(d)["ok"]
