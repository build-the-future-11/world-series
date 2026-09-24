import math
import pytest
import torch
from world_series.wfim.coordinates import WordCoordinates


def test_transport_unit_associativity_and_gradient():
    torch.manual_seed(4101)
    algebra=WordCoordinates(2,3)
    with torch.no_grad(): algebra.theta.copy_(torch.randn_like(algebra.theta))
    x,y,z=[torch.randn(2,len(algebra.words),dtype=torch.float64) for _ in range(3)]
    unit=torch.zeros_like(x);unit[:,0]=1
    assert torch.allclose(algebra.transport(algebra.transport(x),inverse=True),x,atol=1e-12)
    assert torch.allclose(algebra.multiply(x,unit),x,atol=1e-12)
    assert torch.allclose(algebra.multiply(algebra.multiply(x,y),z),algebra.multiply(x,algebra.multiply(y,z)),atol=1e-11)
    algebra.multiply(x,y).square().sum().backward()
    assert torch.isfinite(algebra.theta.grad).all() and algebra.theta.grad.abs().sum()>0
    scales=algebra.scales()
    assert scales[0]==1 and scales.min()>=math.exp(-1) and scales.max()<=math.exp(1)


def test_nonmultiplicative_word_scales_change_product():
    algebra=WordCoordinates(2,2)
    a=torch.zeros(len(algebra.words),dtype=torch.float64);a[algebra.index[(0,)]]=1
    b=torch.zeros_like(a);b[algebra.index[(1,)]]=1
    before=algebra.multiply(a,b)
    with torch.no_grad(): algebra.theta[algebra.index[(0,1)]-1]=1
    after=algebra.multiply(a,b)
    assert not torch.allclose(before,after)
    assert after[algebra.index[(0,1)]]>0
    assert algebra.storage()["parameter_bytes"]==algebra.theta.numel()*8


def test_caps_checked_before_allocation():
    with pytest.raises(ValueError,match="cap"):
        WordCoordinates(4,20)
