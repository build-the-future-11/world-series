"""Mass-aware graph diffusion with nontrivial symmetry/coarsening penalties.

Fine graphs have equitable two-node blocks. Coarse and fine edge fields have
independent trainable coefficients; consistency is not enforced by construction.
"""
from dataclasses import dataclass
import math
import numpy as np
import torch
from torch import nn


@dataclass
class Domain:
    incidence:torch.Tensor
    basis:torch.Tensor
    horizontal:torch.Tensor
    scale:torch.Tensor
    mass:torch.Tensor
    reflection:torch.Tensor
    wrong_action:torch.Tensor
    level:int
    groups:int
    topology:str


def domain(groups,topology='cycle',level=0):
    if topology not in {'cycle','path'} or level not in {0,1} or not 3<=groups<=64:
        raise ValueError('Supported domain: 3..64 groups, cycle/path, fine/coarse')
    fine=level==0;n=groups*2 if fine else groups
    edges=[];positions=[];horizontal=[];scales=[]
    for i in range(groups if topology=='cycle' else groups-1):
        j=(i+1)%groups;x=(i+.5)/(groups if topology=='cycle' else groups-1)
        pairs=[(2*i+a,2*j+b) for a in range(2) for b in range(2)] if fine else [(i,j)]
        for a,b in pairs:edges.append((a,b));positions.append(x);horizontal.append(True);scales.append(.5 if fine else 2.)
    if fine:
        for i in range(groups):edges.append((2*i,2*i+1));positions.append(0.);horizontal.append(False);scales.append(1.)
    incidence=torch.zeros(len(edges),n,dtype=torch.float64)
    for i,(a,b) in enumerate(edges):incidence[i,a]=1.;incidence[i,b]=-1.
    positions=torch.tensor(positions,dtype=torch.float64)
    basis=torch.stack([torch.ones_like(positions),torch.cos(2*math.pi*positions),torch.sin(2*math.pi*positions),
                       torch.cos(4*math.pi*positions),torch.sin(4*math.pi*positions)],1)
    reflect=lambda g:(-g)%groups if topology=='cycle' else groups-1-g
    reflection=[2*reflect(i//2)+i%2 if fine else reflect(i) for i in range(n)]
    wrong=[2*((i//2+1)%groups)+i%2 if fine else (i+1)%groups for i in range(n)]
    return Domain(incidence,basis,torch.tensor(horizontal),torch.tensor(scales,dtype=torch.float64),
                  torch.full((n,),1. if fine else 2.,dtype=torch.float64),torch.tensor(reflection),
                  torch.tensor(wrong),level,groups,topology)


def restriction(groups):
    result=torch.zeros(groups,2*groups,dtype=torch.float64)
    for i in range(groups):result[i,2*i:2*i+2]=.5
    return result


class DiffusionField(nn.Module):
    def __init__(self):
        super().__init__()
        coefficients=torch.zeros(2,5,dtype=torch.float64);coefficients[:,0]=math.log(math.expm1(1.))
        self.coefficients=nn.Parameter(coefficients)
        self.within=nn.Parameter(torch.tensor(math.log(math.expm1(1.)),dtype=torch.float64))

    def laplacian(self,graph):
        raw=graph.basis@self.coefficients[graph.level]
        weights=torch.where(graph.horizontal,torch.nn.functional.softplus(raw),torch.nn.functional.softplus(self.within))*graph.scale
        return graph.incidence.T@(weights[:,None]*graph.incidence)

    def action(self,graph):return self.laplacian(graph)/graph.mass[:,None]

    def transition(self,graph,dt=.15):
        if dt<=0:raise ValueError('Positive diffusion time required')
        return torch.matrix_exp(-dt*self.action(graph))

    def penalties(self,fine,coarse,wrong=False):
        a=self.action(fine);b=self.action(coarse)
        p=fine.wrong_action if wrong else fine.reflection
        q=coarse.wrong_action if wrong else coarse.reflection
        sym=((a[p][:,p]-a)**2).sum()/len(a)+((b[q][:,q]-b)**2).sum()/len(b)
        r=restriction(fine.groups)
        scale=((r@a-b@r)**2).sum()/fine.groups
        return sym,scale


def teacher(seed, stratum='compatible'):
    """Finite teacher fields.

    ``compatible`` matches the original WFT development generator (cosine-only,
    shared fine/coarse coefficients). Misspecification strata deliberately break
    reflection and/or equitable coarsening identities for falsification studies.
    """
    rng=np.random.default_rng(seed);model=DiffusionField()
    if stratum=='compatible':
        coefficients=torch.tensor([rng.uniform(.2,.8),rng.uniform(.3,.8),0.,rng.uniform(.1,.4),0.],dtype=torch.float64)
        with torch.no_grad():model.coefficients.copy_(coefficients.repeat(2,1));model.within.fill_(rng.uniform(.2,1.))
    elif stratum=='sine_perturbed':
        # Nonzero sine modes: weight field is not reflection-symmetric.
        coefficients=torch.tensor([rng.uniform(.2,.8),rng.uniform(.3,.8),rng.uniform(.25,.7),
                                   rng.uniform(.1,.4),rng.uniform(.25,.7)],dtype=torch.float64)
        with torch.no_grad():model.coefficients.copy_(coefficients.repeat(2,1));model.within.fill_(rng.uniform(.2,1.))
    elif stratum=='unequal_degree':
        # Independent fine/coarse fields: R Af = Ac R need not hold.
        fine=torch.tensor([rng.uniform(.2,.8),rng.uniform(.3,.8),0.,rng.uniform(.1,.4),0.],dtype=torch.float64)
        coarse=torch.tensor([rng.uniform(.15,.9),rng.uniform(.1,.55),0.,rng.uniform(.2,.75),0.],dtype=torch.float64)
        with torch.no_grad():
            model.coefficients[0].copy_(fine);model.coefficients[1].copy_(coarse)
            model.within.fill_(rng.uniform(.2,1.))
    else:
        raise ValueError(f'Unknown teacher stratum: {stratum}')
    return model


def spectral_projection(laplacian,mass,signals,k=5,max_nodes=128):
    l=np.asarray(laplacian,dtype=np.float64);mass=np.asarray(mass,dtype=np.float64);signals=np.asarray(signals)
    if mass.ndim!=1 or signals.ndim!=2:raise ValueError('Mass vector and signal matrix required')
    n=len(mass)
    if not 1<=n<=max_nodes or l.shape!=(n,n) or signals.shape[0]!=n or not 1<=k<=n:
        raise ValueError('Invalid shapes, rank or dense allocation cap')
    if np.any(mass<=0) or not np.isfinite(mass).all() or not np.isfinite(l).all() or not np.isfinite(signals).all() or not np.allclose(l,l.T,atol=1e-10):
        raise ValueError('Positive masses and symmetric Laplacian required')
    inv=1/np.sqrt(mass);s=inv[:,None]*l*inv[None,:]
    eigenvalues,q=np.linalg.eigh(s)
    if eigenvalues[0]<-1e-8:raise ValueError('PSD operator required')
    # Never cut a numerically repeated cluster; report the actual retained rank.
    rank=k
    while rank<n and abs(eigenvalues[rank]-eigenvalues[rank-1])<=1e-8*max(1.,abs(eigenvalues[rank])):rank+=1
    white=np.sqrt(mass)[:,None]*signals;retained=q[:,:rank]
    decoded=inv[:,None]*(retained@(retained.T@white))
    residual=np.linalg.norm(s@q-q*eigenvalues[None,:])/max(1.,np.linalg.norm(s))
    full=inv[:,None]*(q@(q.T@white))
    return decoded,{'rank_requested':k,'rank_retained':rank,'min_eigenvalue':float(eigenvalues[0]),
                     'eigen_residual':float(residual),'full_basis_error':float(np.max(np.abs(full-signals))),
                     'mass_parseval_error':float(abs(np.sum(white**2)-np.sum((q.T@white)**2))),
                     'row_sum_error':float(np.max(np.abs(l.sum(1))))}
