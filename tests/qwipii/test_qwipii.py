
from fractions import Fraction
from world_series.qwipii.projective import mobius, cross_ratio
from world_series.qwipii.domains import RingState
from world_series.qwipii.search import bfs, quotient_bfs, replay
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import WorldSeriesError
import pytest

def test_cross_ratio_and_pole():
    pts = [Fraction(0),Fraction(1),Fraction(2),Fraction(4)]
    cr = cross_ratio(*pts)
    assert cr != 0
    with pytest.raises(WorldSeriesError):
        mobius(1,0,0,0,Fraction(1))  # singular
    with pytest.raises(WorldSeriesError):
        mobius(1,0,1,-1,Fraction(1))  # pole at x=1

def test_search_lift():
    start = RingState((1,0,2),(0,1,2))
    ledger = BudgetLedger(Budget())
    path, _, st = bfs(start, ledger)
    assert st == "solved"
    assert replay(start, path).tokens == start.goal
