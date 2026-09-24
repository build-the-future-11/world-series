import numpy as np
import pytest
import torch
from world_series.wft.constraints import DiffusionField,domain,restriction,teacher,spectral_projection


@pytest.mark.parametrize('topology',['cycle','path'])
def test_equitable_restriction_and_verified_reflection(topology):
    model=teacher(13);fine=domain(8,topology,0);coarse=domain(8,topology,1)
    a=model.action(fine);b=model.action(coarse);r=restriction(8)
    assert torch.allclose(r@a,b@r,atol=1e-12)
    assert torch.allclose(r@model.transition(fine),model.transition(coarse)@r,atol=1e-12)
    sym,scale=model.penalties(fine,coarse)
    assert float(sym.detach())<1e-20 and float(scale.detach())<1e-20
    assert float(model.penalties(fine,coarse,wrong=True)[0].detach())>1e-3


def test_consistency_loss_is_not_an_identity_and_has_gradients():
    model=DiffusionField()
    with torch.no_grad():model.coefficients[0,2]=.4;model.coefficients[1,0]+=.5
    sym,scale=model.penalties(domain(8),domain(8,level=1))
    assert float(sym.detach())>0 and float(scale.detach())>0
    (sym+scale).backward()
    assert model.coefficients.grad.abs().sum()>0


def test_psd_nonuniform_mass_parseval_and_permutation_covariance():
    graph=domain(8);model=teacher(8)
    l=model.laplacian(graph).detach().numpy();rng=np.random.default_rng(11)
    mass=rng.uniform(.5,2,16);x=rng.normal(size=(16,4))
    projected,receipt=spectral_projection(l,mass,x,k=16)
    assert np.allclose(projected,x) and receipt['mass_parseval_error']<1e-10
    perm=rng.permutation(16)
    changed,_=spectral_projection(l[perm][:,perm],mass[perm],x[perm],k=5)
    original,_=spectral_projection(l,mass,x,k=5)
    assert np.allclose(changed,original[perm],atol=1e-10)


def test_dense_cap_and_repeated_cluster():
    with pytest.raises(ValueError):domain(65)
    l=np.eye(4)-np.ones((4,4))/4
    _,receipt=spectral_projection(l,np.ones(4),np.eye(4),k=2)
    assert receipt['rank_retained']==4
    with pytest.raises(ValueError):spectral_projection(l,np.ones(4),np.eye(4),k=2,max_nodes=3)


def test_transition_gradient_matches_finite_difference():
    model=DiffusionField();graph=domain(4);x=torch.arange(8,dtype=torch.float64)[:,None]
    value=(model.transition(graph)@x).square().sum();value.backward()
    analytic=float(model.coefficients.grad[0,0]);delta=1e-5
    with torch.no_grad():
        model.coefficients[0,0]+=delta;a=float((model.transition(graph)@x).square().sum())
        model.coefficients[0,0]-=2*delta;b=float((model.transition(graph)@x).square().sum())
    assert abs((a-b)/(2*delta)-analytic)<1e-6
