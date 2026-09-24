from __future__ import annotations

import numpy as np

from world_series.wcode.dsl import AST, ast_nodes
from world_series.wcode.graph import extract_graph

OP_VOCAB = {"lit": 0, "var": 1, "binop": 2, "if": 3, "list": 4, "listop": 5}


def _bag_from_graph(g) -> np.ndarray:
    v = np.zeros(len(OP_VOCAB), dtype=np.float64)
    for n in g.node_features:
        v[OP_VOCAB.get(n["op"], 0)] += 1.0
    return v


def token_encode(ast: AST) -> np.ndarray:
    return _bag_from_graph(extract_graph(ast))


def flat_graph_encode(ast: AST) -> np.ndarray:
    g = extract_graph(ast)
    v = _bag_from_graph(g)
    rels = {"child": 0, "sibling": 0, "parent": 0}
    for _, _, r in g.edges:
        if r in rels:
            rels[r] += 1
    extra = np.array(
        [rels["child"], rels["sibling"], rels["parent"], len(g.node_features)],
        dtype=np.float64,
    )
    return np.concatenate([v, extra])


def hierarchical_encode(ast: AST) -> np.ndarray:
    # Reuse flat encoding (single graph extract inside flat_graph_encode)
    base = flat_graph_encode(ast)
    depth_proxy = float(ast_nodes(ast))
    return np.concatenate([base, np.array([depth_proxy, np.log1p(depth_proxy)])])


def score_candidate(ast: AST, examples: list[tuple[dict, int]], mode: str = "hierarchical") -> float:
    """Higher is better priority. Uses public examples only + structural prior."""
    from world_series.wcode.interpreter import Fuel, interpret

    match = 0
    for env, y in examples:
        try:
            out = interpret(ast, env, Fuel(32))
            match += int(out == y)
        except Exception:
            match -= 1
    if mode == "uniform":
        struct = 0.0
    elif mode == "length":
        struct = -float(ast_nodes(ast))
    elif mode == "token":
        struct = -float(np.linalg.norm(token_encode(ast)))
    elif mode == "flat":
        struct = -0.01 * float(np.linalg.norm(flat_graph_encode(ast)))
    else:
        struct = -0.01 * float(np.linalg.norm(hierarchical_encode(ast))) + 0.1 * match
    return float(match) * 10.0 + struct
