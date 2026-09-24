
from world_series.cwlnn.graphs import GraphLevel, path_edges
from world_series.cwlnn.local import sparse_mean_aggregate, dense_mean_aggregate
import numpy as np
def test_sparse_dense():
    n=6
    feats=np.random.default_rng(0).normal(size=(n,3))
    edges=path_edges(n)
    adj=np.zeros((n,n));
    for s,d in edges.T: adj[s,d]=1
    assert np.allclose(sparse_mean_aggregate(feats,edges), dense_mean_aggregate(feats,adj))
