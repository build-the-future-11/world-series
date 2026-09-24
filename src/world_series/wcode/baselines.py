from __future__ import annotations
from world_series.wcode.dsl import ast_nodes

def uniform_priority(prog) -> float:
    return 0.0

def length_priority(prog) -> float:
    return -float(ast_nodes(prog))
