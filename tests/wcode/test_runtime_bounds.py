import pytest
from world_series.core.contracts import WorldSeriesError
from world_series.wcode.dsl import BinOp,Lit,Var,ListLit,ListOp
from world_series.wcode.interpreter import Fuel,interpret


@pytest.mark.parametrize('node,env',[
    (Var('x'),{'x':True}), (Var('x'),{'x':10001}),
    (Var('xs','list[int]'),{'xs':[True]}),
    (Var('xs','list[int]'),{'xs':list(range(33))}),
    (Lit(1.5),{}), (BinOp('+',BinOp('<',Lit(1),Lit(2)),Lit(3)),{}),
    (ListOp('sum',ListLit((Lit(9999),Lit(9999)))),{}),
    (ListOp('take',ListLit((Lit(1),)),1.5),{}),
])
def test_invalid_runtime_values_are_typed_failures(node,env):
    with pytest.raises(WorldSeriesError):interpret(node,env,Fuel(100))


def test_oversized_list_rejected_before_evaluating_children():
    fuel=Fuel(2)
    with pytest.raises(WorldSeriesError,match='list length'):
        interpret(ListLit(tuple(Var('missing') for _ in range(33))),{},fuel)
    assert fuel.remaining==1
