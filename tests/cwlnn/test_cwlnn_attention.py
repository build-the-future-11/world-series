
import numpy as np
from world_series.cwlnn.baselines import tiny_attention
def test_attention_budgeted():
    f = np.ones((10,3))
    out, meta = tiny_attention(f, budget_pairs=8)
    assert meta["selected"] >= 1
    assert out.shape == f.shape
