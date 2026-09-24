
from world_series.qapen.baselines import FixedEnsemble, nll
def test_fixed_ensemble_nll():
    m,v = FixedEnsemble().predict()
    assert nll(0.0, m, v) > 0
