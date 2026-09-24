
from world_series.qapen.mixture import mixture_moments
from world_series.qapen.experts import ExpertBank, ExpertState
from world_series.core.contracts import WorldSeriesError
import numpy as np, pytest
def test_mixture_and_capacity():
    w,m,v = mixture_moments(np.array([0.3,0.7]), np.array([0.,2.]), np.array([1.,0.5]))
    assert abs(m-1.4)<1e-9
    bank = ExpertBank(max_experts=1)
    bank.spawn()
    with pytest.raises(WorldSeriesError):
        bank.spawn()
