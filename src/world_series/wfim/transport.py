from __future__ import annotations
from world_series.wfim.algebra import SparseWordSeries, multiply, Word

def diagonal_transport(x: SparseWordSeries, scales: dict[int, float]) -> SparseWordSeries:
    # degree-preserving positive diagonal on letter indices inside words
    out = {}
    for w, c in x.coeffs.items():
        s = 1.0
        for letter in w:
            s *= scales.get(letter, 1.0)
        out[w] = c * s
    return SparseWordSeries(out, r=x.r)

def inverse_diagonal_transport(x: SparseWordSeries, scales: dict[int, float]) -> SparseWordSeries:
    inv = {k: 1.0 / v for k, v in scales.items()}
    return diagonal_transport(x, inv)

def transported_multiply(x, y, scales):
    sx = diagonal_transport(x, scales)
    sy = diagonal_transport(y, scales)
    return inverse_diagonal_transport(multiply(sx, sy), scales)
