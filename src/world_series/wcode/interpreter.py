from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from world_series.core.contracts import ErrorCode, WorldSeriesError
from world_series.wcode.dsl import AST, Lit, Var, BinOp, If, ListLit, ListOp, ALLOWED_BINOPS, ast_depth

@dataclass
class Fuel:
    remaining: int
    def tick(self, n: int = 1):
        self.remaining -= n
        if self.remaining < 0:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "DSL fuel exhausted")

def _type_of(val: Any) -> str:
    if isinstance(val, bool):
        return "bool"
    if isinstance(val, int):
        return "int"
    if isinstance(val, list) and all(type(x) is int for x in val):
        return "list[int]"
    raise WorldSeriesError(ErrorCode.INVALID_DTYPE, f"unsupported runtime value {type(val)}")

def interpret(node: AST, env: dict[str, Any], fuel: Fuel, *, max_list_len: int = 32, max_int_abs: int = 10_000) -> Any:
    fuel.tick()
    if isinstance(node, Lit):
        if type(node.value) is not int:
            raise WorldSeriesError(ErrorCode.INVALID_DTYPE, "integer literal required")
        if abs(node.value) > max_int_abs:
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "integer magnitude exceeded")
        return int(node.value)
    if isinstance(node, Var):
        if node.name not in env:
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"unbound var {node.name}")
        value=env[node.name]
        if _type_of(value)!=node.typ:
            raise WorldSeriesError(ErrorCode.INVALID_DTYPE, "variable type mismatch")
        if isinstance(value,list):
            if len(value)>max_list_len:
                raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "list length exceeded")
            if any(abs(x)>max_int_abs for x in value):
                raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "integer magnitude exceeded")
        elif type(value) is int and abs(value)>max_int_abs:
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "integer magnitude exceeded")
        return value
    if isinstance(node, BinOp):
        if node.op not in ALLOWED_BINOPS:
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"binop not allowed: {node.op}")
        a = interpret(node.left, env, fuel, max_list_len=max_list_len, max_int_abs=max_int_abs)
        b = interpret(node.right, env, fuel, max_list_len=max_list_len, max_int_abs=max_int_abs)
        if type(a) is not int or type(b) is not int:
            raise WorldSeriesError(ErrorCode.INVALID_DTYPE, "binary operators require integers")
        if node.op == "+":
            out = a + b
        elif node.op == "-":
            out = a - b
        elif node.op == "*":
            out = a * b
        elif node.op == "//":
            if b == 0:
                raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "division by zero")
            out = a // b
        elif node.op == "%":
            if b == 0:
                raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "modulo by zero")
            out = a % b
        elif node.op == "==":
            out = bool(a == b)
        elif node.op == "<":
            out = bool(a < b)
        elif node.op == ">":
            out = bool(a > b)
        else:
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, node.op)
        if isinstance(out, int) and abs(out) > max_int_abs:
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "integer magnitude exceeded")
        return out
    if isinstance(node, If):
        cond = interpret(node.cond, env, fuel, max_list_len=max_list_len, max_int_abs=max_int_abs)
        if not isinstance(cond, bool):
            raise WorldSeriesError(ErrorCode.INVALID_DTYPE, "If condition must be bool")
        branch = node.then if cond else node.else_
        return interpret(branch, env, fuel, max_list_len=max_list_len, max_int_abs=max_int_abs)
    if isinstance(node, ListLit):
        if len(node.items)>max_list_len:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "list length exceeded")
        items = [interpret(x, env, fuel, max_list_len=max_list_len, max_int_abs=max_int_abs) for x in node.items]
        if len(items) > max_list_len:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "list length exceeded")
        if not all(type(x) is int for x in items):
            raise WorldSeriesError(ErrorCode.INVALID_DTYPE, "list[int] required")
        return items
    if isinstance(node, ListOp):
        arg = interpret(node.arg, env, fuel, max_list_len=max_list_len, max_int_abs=max_int_abs)
        if node.op == "len":
            if not isinstance(arg, list):
                raise WorldSeriesError(ErrorCode.INVALID_DTYPE, "len expects list")
            return len(arg)
        if node.op == "sum":
            if not isinstance(arg, list):
                raise WorldSeriesError(ErrorCode.INVALID_DTYPE, "sum expects list")
            result=sum(arg)
            if abs(result)>max_int_abs:
                raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "integer magnitude exceeded")
            return result
        if node.op == "reverse":
            if not isinstance(arg, list):
                raise WorldSeriesError(ErrorCode.INVALID_DTYPE, "reverse expects list")
            return list(reversed(arg))
        if node.op == "take":
            if not isinstance(arg, list) or type(node.n) is not int:
                raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "take requires list and n")
            return arg[: max(0, node.n)]
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"unknown list op {node.op}")
    raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"malformed AST node {type(node)}")

def validate_ast(node: AST, max_depth: int = 6, max_nodes: int = 64) -> None:
    d = ast_depth(node)
    if d > max_depth:
        raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, f"AST depth {d} > {max_depth}")
    from world_series.wcode.dsl import ast_nodes
    n = ast_nodes(node)
    if n > max_nodes:
        raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, f"AST nodes {n} > {max_nodes}")
