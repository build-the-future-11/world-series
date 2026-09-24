from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Union

@dataclass(frozen=True)
class Lit:
    value: int
    typ: str = "int"

@dataclass(frozen=True)
class Var:
    name: str
    typ: str = "int"

@dataclass(frozen=True)
class BinOp:
    op: str
    left: Any
    right: Any
    typ: str = "int"

@dataclass(frozen=True)
class If:
    cond: Any
    then: Any
    else_: Any
    typ: str = "int"

@dataclass(frozen=True)
class ListLit:
    items: tuple
    typ: str = "list[int]"

@dataclass(frozen=True)
class ListOp:
    op: str  # sum|reverse|take|len
    arg: Any
    n: int | None = None
    typ: str = "int"

AST = Union[Lit, Var, BinOp, If, ListLit, ListOp]
ALLOWED_BINOPS = {"+", "-", "*", "//", "%", "==", "<", ">"}

def ast_depth(node: Any) -> int:
    if isinstance(node, (Lit, Var)):
        return 1
    if isinstance(node, BinOp):
        return 1 + max(ast_depth(node.left), ast_depth(node.right))
    if isinstance(node, If):
        return 1 + max(ast_depth(node.cond), ast_depth(node.then), ast_depth(node.else_))
    if isinstance(node, ListLit):
        return 1 + (max((ast_depth(x) for x in node.items), default=0))
    if isinstance(node, ListOp):
        return 1 + ast_depth(node.arg)
    raise TypeError(type(node))

def ast_nodes(node: Any) -> int:
    if isinstance(node, (Lit, Var)):
        return 1
    if isinstance(node, BinOp):
        return 1 + ast_nodes(node.left) + ast_nodes(node.right)
    if isinstance(node, If):
        return 1 + ast_nodes(node.cond) + ast_nodes(node.then) + ast_nodes(node.else_)
    if isinstance(node, ListLit):
        return 1 + sum(ast_nodes(x) for x in node.items)
    if isinstance(node, ListOp):
        return 1 + ast_nodes(node.arg)
    raise TypeError(type(node))
