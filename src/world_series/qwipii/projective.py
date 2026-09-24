from __future__ import annotations
from fractions import Fraction
from world_series.core.contracts import ErrorCode, WorldSeriesError

def mobius(a, b, c, d, x):
    a, b, c, d, x = map(Fraction, (a, b, c, d, x))
    det = a * d - b * c
    if det == 0:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "singular Möbius transform (ad-bc=0)")
    den = c * x + d
    if den == 0:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "pole: denominator zero")
    return (a * x + b) / den

def cross_ratio(p, q, r, s):
    p, q, r, s = map(Fraction, (p, q, r, s))
    if len({p, q, r, s}) < 4:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "cross-ratio requires four distinct points")
    return ((p - r) * (q - s)) / ((p - s) * (q - r))

def cross_ratio_invariant(a, b, c, d, pts):
    mapped = [mobius(a, b, c, d, x) for x in pts]
    return cross_ratio(*pts), cross_ratio(*mapped)
