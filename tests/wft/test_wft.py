
from world_series.wft.laplacian import path_graph, laplacian_from_weights, is_psd, weighted_spectral, encode, decode
import numpy as np
def test_psd_recon():
    W = path_graph(5)
    L = laplacian_from_weights(W)
    assert is_psd(L)
    M = np.eye(5)
    ev,Q,Phi = weighted_spectral(L,M)
    f = np.arange(5, dtype=float)
    assert np.allclose(f, decode(encode(f,Phi,M), Phi))
