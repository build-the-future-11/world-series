import math
from decimal import Decimal, localcontext

import numpy as np
import pytest
import torch

from world_series.qapen.causal import CausalLifecycle, Engram, FrozenQuantizer, gaussian_nll
from world_series.qapen.mixture import mixture_moments


@pytest.mark.parametrize("offset", [0.0, 1e8, -1e12])
def test_common_translation_preserves_component_uncertainty(offset):
    weights, mean, variance = mixture_moments(
        np.array([0.5, 0.5]), np.array([offset, offset]), np.array([1.0, 1.0])
    )
    np.testing.assert_array_equal(weights, [0.5, 0.5])
    assert mean == offset
    assert variance == 1.0


def test_law_of_total_variance_uses_centered_component_offsets():
    _, mean, variance = mixture_moments(
        np.array([1.0, 3.0]), np.array([1e12, 1e12 + 4.0]), np.array([2.0, 6.0])
    )
    assert mean == 1e12 + 3.0
    assert variance == 8.0  # E[var] = 5; Var[mean] = 3.


def test_large_weight_scale_does_not_destroy_the_distribution():
    w, mean, variance = mixture_moments(np.array([1e308, 1e308]), np.array([0.0, 2.0]), np.ones(2))
    np.testing.assert_array_equal(w, [0.5, 0.5])
    assert (mean, variance) == (1.0, 2.0)


def test_small_weight_retains_large_representable_between_component_variance():
    _, mean, variance = mixture_moments(np.array([1.0, 1e-300]), np.array([0.0, 1e200]), np.ones(2))
    assert mean == pytest.approx(1e-100, rel=1e-14, abs=0)
    assert variance == pytest.approx(1e100, rel=1e-14)


@pytest.mark.parametrize(
    ("weights", "means", "variances"),
    [
        ([], [], []),
        ([0, 0], [1, 2], [1, 1]),
        ([-1, 2], [1, 2], [1, 1]),
        ([1, 1], [1], [1, 1]),
        ([1, 1], [1, 2], [1, -1]),
        ([1, 1], [1, np.inf], [1, 1]),
        ([True, 1.0], [1, 2], [1, 1]),
        ([1, 1], [1 + 1j, 2], [1, 1]),
    ],
)
def test_invalid_mixture_cannot_be_reported_as_finite_uncertainty(weights, means, variances):
    with pytest.raises(ValueError):
        mixture_moments(weights, means, variances)


@pytest.mark.parametrize(
    ("value", "mean", "variance"),
    [(0.0, 0.0, 1e308), (1e200, 0.0, 1e200), (1e308, -1e308, 1.7e308)],
)
def test_gaussian_nll_avoids_intermediate_overflow(value, mean, variance):
    with localcontext() as context:
        context.prec = 100
        v = Decimal(str(variance))
        error = Decimal(str(value)) - Decimal(str(mean))
        expected = float((Decimal(str(2 * math.pi)).ln() + v.ln() + error * error / v) / 2)
    assert gaussian_nll(value, mean, variance) == pytest.approx(expected, rel=2e-14)


@pytest.mark.parametrize("variance", [0.0, -1.0, np.inf, np.nan, True])
def test_nll_rejects_invalid_variance(variance):
    with pytest.raises(ValueError):
        gaussian_nll(0.0, 0.0, variance)


def test_actual_lifecycle_expert_and_memory_routes_keep_variance():
    model = CausalLifecycle(FrozenQuantizer(np.zeros((1, 1))), lifecycle=False)
    expert_id = next(iter(model.models))
    with torch.no_grad():
        model.models[expert_id].linear.bias.fill_(1e12)
    model.t = 1
    model.engrams.append(Engram(0, 0, [0.0], 1e12, 1.0, expert_id, 0))
    mean, variance = model.predict([0.0])
    assert mean == 1e12
    assert model.pending["base"][1] == 1.0
    assert variance == 1.0


def test_genuinely_unrepresentable_variance_is_rejected():
    with pytest.raises(ValueError, match="variance"):
        mixture_moments(np.ones(2), np.array([-1e308, 1e308]), np.ones(2))
