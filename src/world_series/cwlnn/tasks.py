"""Public sparse graph inputs and two declared synthetic signal tasks."""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply
import torch

from world_series.cwlnn.conditional import SparseWorld


def generate(seed, n, topology, tau, task):
    if n < 2 or topology not in ('path', 'cycle', 'tree') or task not in ('multiscale', 'diffusion'):
        raise ValueError('Unknown task or graph')
    rng = np.random.default_rng(seed)
    if topology in ('path', 'cycle'):
        a, b = np.arange(n-1), np.arange(1,n)
        if topology == 'cycle':
            a, b = np.r_[a,n-1], np.r_[b,0]
    else:
        # Random recursive tree, held out from training. No target-derived grouping.
        b = np.arange(1,n)
        a = np.array([rng.integers(i) for i in b])
    edges = np.stack([np.r_[a,b],np.r_[b,a]])
    signal = rng.normal(size=(n,2)) * rng.uniform(.5,1.5)
    ids = np.arange(n,dtype=np.int64)
    parent = ids//2
    count = int(parent.max())+1
    x = np.column_stack([signal,np.full(n,tau),np.linspace(-1,1,n)])
    adjacency = sparse.coo_matrix((np.ones(edges.shape[1]),(edges[0],edges[1])),shape=(n,n)).tocsr()
    laplacian = sparse.diags(np.asarray(adjacency.sum(axis=1)).ravel())-adjacency
    fine = expm_multiply(-tau*laplacian,signal[:,0])
    if task == 'multiscale':
        sums = np.bincount(parent,weights=signal[:,1],minlength=count)
        coarse_signal = sums/np.bincount(parent,minlength=count)
        coarse_pairs = np.unique(parent[edges].T,axis=0)
        coarse_pairs = coarse_pairs[coarse_pairs[:,0]!=coarse_pairs[:,1]]
        ca = sparse.coo_matrix((np.ones(len(coarse_pairs)),(coarse_pairs[:,0],coarse_pairs[:,1])),shape=(count,count)).tocsr()
        cl = sparse.diags(np.asarray(ca.sum(axis=1)).ravel())-ca
        coarse = expm_multiply(-tau*cl,coarse_signal)
        target = .5*np.sin(fine)+.5*np.tanh(coarse[parent])
    else:
        # Label generation never accesses the public hierarchy in this task.
        fine = expm_multiply(-2*tau*laplacian,signal[:,0])
        target = np.sin(fine)+.2*signal[:,1]
    return {'x':x,'edges':edges,'node_id':ids,'target':target,
            'seed':seed,'n':n,'topology':topology,'tau':tau,'task':task}


def prepare(sample):
    """Included in inference timings: input copies and public parent construction."""
    ids = torch.tensor(sample['node_id'],dtype=torch.long)
    return SparseWorld(torch.tensor(sample['x'],dtype=torch.float64),
                       torch.tensor(sample['edges'],dtype=torch.long),ids//2,
                       torch.zeros(len(ids),dtype=torch.long),ids)
