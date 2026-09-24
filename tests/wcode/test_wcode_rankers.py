
from world_series.core.budgets import Budget, BudgetLedger
from world_series.wcode.search import compare_rankers

def test_ranker_compare_runs():
    examples = [({"x":1},2),({"x":3},4)]
    held = [({"x":5},6)]
    out = compare_rankers(examples, held, lambda: BudgetLedger(Budget()), max_candidates=32)
    assert "hierarchical" in out and "uniform" in out
