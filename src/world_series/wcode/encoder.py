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
    """Structural ordering only: executing the entire pool here would evade budgets.

    These are untrained structural heuristics, not learned relational encoders.
    Public examples are intentionally unused until charged candidate evaluation.
    """
    if mode == "uniform":
        return 0.0
    if mode == "length":
        return -float(ast_nodes(ast))
    if mode == "token":
        return -float(np.linalg.norm(token_encode(ast)))
    if mode == "flat":
        return -float(np.linalg.norm(flat_graph_encode(ast)))
    if mode == "hierarchical":
        return -float(np.linalg.norm(hierarchical_encode(ast)))
    raise ValueError(f"Unknown ranker {mode}")
