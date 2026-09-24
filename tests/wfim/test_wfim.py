
from world_series.wfim.algebra import basis, multiply, unit, assert_associativity_truncated, topk_prune, add
def test_algebra_laws():
    a,b = basis(1), basis(2)
    assert multiply(unit(), a).coeffs == a.coeffs
    assert assert_associativity_truncated(a,b,a,n=4)
