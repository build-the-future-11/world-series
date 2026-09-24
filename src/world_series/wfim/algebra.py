from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
from world_series.core.contracts import ErrorCode, WorldSeriesError

Word = Tuple[int, ...]

@dataclass
class SparseWordSeries:
    coeffs: Dict[Word, float]
    r: float = 1.0

    def copy(self) -> "SparseWordSeries":
        return SparseWordSeries(dict(self.coeffs), r=self.r)

def word_norm(x: SparseWordSeries) -> float:
    return float(sum(abs(c) * (x.r ** len(w)) for w, c in x.coeffs.items()))

def add(x: SparseWordSeries, y: SparseWordSeries) -> SparseWordSeries:
    out = x.copy()
    for w, c in y.coeffs.items():
        out.coeffs[w] = out.coeffs.get(w, 0.0) + c
        if abs(out.coeffs[w]) < 1e-15:
            del out.coeffs[w]
    return out

def multiply(x: SparseWordSeries, y: SparseWordSeries) -> SparseWordSeries:
    out: Dict[Word, float] = {}
    for u, a in x.coeffs.items():
        for v, b in y.coeffs.items():
            w = u + v
            out[w] = out.get(w, 0.0) + a * b
    return SparseWordSeries(out, r=min(x.r, y.r))

def project_degree(x: SparseWordSeries, n: int) -> SparseWordSeries:
    return SparseWordSeries({w: c for w, c in x.coeffs.items() if len(w) <= n}, r=x.r)

def truncated_multiply(x: SparseWordSeries, y: SparseWordSeries, n: int) -> SparseWordSeries:
    """Degree-truncated product without materializing discarded high-degree terms."""
    out: Dict[Word, float] = {}
    for u, a in x.coeffs.items():
        lu = len(u)
        if lu > n:
            continue
        for v, b in y.coeffs.items():
            if lu + len(v) > n:
                continue
            w = u + v
            out[w] = out.get(w, 0.0) + a * b
    return SparseWordSeries(out, r=min(x.r, y.r))

def unit() -> SparseWordSeries:
    return SparseWordSeries({(): 1.0})

def basis(i: int) -> SparseWordSeries:
    return SparseWordSeries({(i,): 1.0})

def assert_associativity_truncated(x, y, z, n: int, tol: float = 1e-10) -> bool:
    left = truncated_multiply(truncated_multiply(x, y, n), z, n)
    right = truncated_multiply(x, truncated_multiply(y, z, n), n)
    keys = set(left.coeffs) | set(right.coeffs)
    return all(abs(left.coeffs.get(k, 0) - right.coeffs.get(k, 0)) <= tol for k in keys)

def topk_prune(x: SparseWordSeries, k: int) -> SparseWordSeries:
    items = sorted(x.coeffs.items(), key=lambda kv: abs(kv[1]), reverse=True)[:k]
    return SparseWordSeries(dict(items), r=x.r)

def refuse_degree(n: int, max_degree: int) -> None:
    if n > max_degree:
        raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, f"degree {n} > max {max_degree}")
