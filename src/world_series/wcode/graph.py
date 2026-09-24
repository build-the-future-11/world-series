from __future__ import annotations
import hashlib
from dataclasses import dataclass
from world_series.wcode.dsl import AST, Lit, Var, BinOp, If, ListLit, ListOp

@dataclass
class ProgramGraph:
    node_features: list[dict]
    edges: list[tuple[int, int, str]]  # src, dst, relation

def _add(features, edges, node, parent=None, rel=None):
    idx = len(features)
    if isinstance(node, Lit):
        features.append({"op": "lit", "value": node.value, "typ": node.typ})
    elif isinstance(node, Var):
        features.append({"op": "var", "name": node.name, "typ": node.typ})
    elif isinstance(node, BinOp):
        features.append({"op": "binop", "binop": node.op, "typ": node.typ})
        l = _add(features, edges, node.left, idx, "left")
        r = _add(features, edges, node.right, idx, "right")
        edges.append((idx, l, "child"))
        edges.append((idx, r, "child"))
        edges.append((l, r, "sibling"))
    elif isinstance(node, If):
        features.append({"op": "if", "typ": node.typ})
        for name, child in ("cond", node.cond), ("then", node.then), ("else", node.else_):
            c = _add(features, edges, child, idx, name)
            edges.append((idx, c, "child"))
    elif isinstance(node, ListLit):
        features.append({"op": "list", "typ": node.typ})
        prev = None
        for item in node.items:
            c = _add(features, edges, item, idx, "item")
            edges.append((idx, c, "child"))
            if prev is not None:
                edges.append((prev, c, "sibling"))
            prev = c
    elif isinstance(node, ListOp):
        features.append({"op": "listop", "listop": node.op, "typ": node.typ})
        c = _add(features, edges, node.arg, idx, "arg")
        edges.append((idx, c, "child"))
    else:
        raise TypeError(type(node))
    if parent is not None and rel is not None:
        edges.append((idx, parent, "parent"))
    return idx

def extract_graph(ast: AST) -> ProgramGraph:
    feats, edges = [], []
    _add(feats, edges, ast)
    return ProgramGraph(feats, edges)

def ast_hash(ast: AST) -> str:
    g = extract_graph(ast)
    blob = repr((g.node_features, g.edges)).encode()
    return hashlib.sha256(blob).hexdigest()
