
from world_series.wcode.dsl import BinOp, Var, Lit
from world_series.wcode.interpreter import interpret, Fuel, validate_ast
from world_series.core.contracts import WorldSeriesError
import pytest

def test_interp_and_fuel():
    prog = BinOp("+", Var("x"), Lit(1))
    assert interpret(prog, {"x":3}, Fuel(10)) == 4
    with pytest.raises(WorldSeriesError):
        interpret(prog, {"x":3}, Fuel(0))

def test_no_div_zero():
    prog = BinOp("//", Lit(1), Lit(0))
    with pytest.raises(WorldSeriesError):
        interpret(prog, {}, Fuel(10))
