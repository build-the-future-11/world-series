from __future__ import annotations

import math

import numpy as np


def _real_vector(value, name):
    array = np.asarray(value)
    mixed_boolean = not isinstance(value, np.ndarray) and any(
        isinstance(item, (bool, np.bool_)) for item in np.asarray(value, dtype=object).flat
    )
    if array.ndim != 1 or not len(array) or array.dtype.kind not in "iuf" or mixed_boolean:
        raise ValueError(f"{name} must be a non-empty real vector")
    with np.errstate(over="ignore"):
        array = array.astype(np.float64)
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must contain finite float64 values")
    return array


def mixture_moments(weights: np.ndarray, means: np.ndarray, vars_: np.ndarray):
    """Gaussian-mixture moments using the centered law of total variance."""
    weights = _real_vector(weights, "weights")
    means = _real_vector(means, "means")
    variances = _real_vector(vars_, "variances")
    if weights.shape != means.shape or means.shape != variances.shape:
        raise ValueError("mixture weights, means and variances must have equal shapes")
    if np.any(weights < 0) or not np.any(weights > 0) or np.any(variances < 0):
        raise ValueError(
            "nonnegative weights with positive mass and nonnegative variances required"
        )
    scaled = weights / float(weights.max())
    w = scaled / float(scaled.sum())
    if np.any((weights > 0) & (w == 0)):
        raise ValueError("normalized mixture weights underflow the positive numeric range")
    positive = w > 0
    origin = float(means[positive][0])
    with np.errstate(over="ignore", invalid="ignore"):
        offsets = means[positive] - origin
        if np.isfinite(offsets).all():
            mean = origin + float(w[positive] @ offsets)
        else:
            scale = float(np.max(np.abs(means[positive])))
            mean = scale * float(w[positive] @ (means[positive] / scale))
        centered = means[positive] - mean
        roots = np.sqrt(w[positive])
        # Weight before squaring: a tiny-weight, large-offset component can
        # have finite variance even when its unweighted square overflows.
        spread = roots * centered
        overflowed = ~np.isfinite(centered)
        spread[overflowed] = (
            roots[overflowed] * means[positive][overflowed] - roots[overflowed] * mean
        )
        variance = float(w @ variances) + float(spread @ spread)
    if not math.isfinite(mean) or not math.isfinite(variance):
        raise ValueError("mixture mean or variance exceeds the finite numeric range")
    return w, mean, variance
