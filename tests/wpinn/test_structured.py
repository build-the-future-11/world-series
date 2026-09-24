import numpy as np
import pytest
import torch

from world_series.wpinn.structured import (
    NAMES, ObservationField, compact_tests, library, neural_observations,
    rollout, sparse_fit, spline_observations, trapezoid_weights, weak_system,
)
from world_series.wpinn.systems import simulate_oscillator


def test_irregular_quadrature_and_analytic_bump_derivative():
    t = np.array([0., .01, .14, .31, .9, 1.])
    assert trapezoid_weights(t) @ (3 * t + 2) == pytest.approx(3.5)
    grid = np.linspace(0, 5, 10001)
    psi, dpsi = compact_tests(grid, 7)
    assert np.max(np.abs(psi[[0, -1]])) == 0
    assert np.max(np.abs(np.gradient(psi, grid, axis=0)[2:-2] - dpsi[2:-2])) < 4e-6
    with pytest.raises(ValueError):
        trapezoid_weights([0, 1, 1])


def test_analytic_weak_identity_and_quadrature_convergence():
    errors = []
    for n in (41, 81, 161):
        t = np.linspace(0, 5, n)
        y = simulate_oscillator(2., .3, .7, -1.1, t)
        a, b = weak_system([(t, y)])
        true = np.zeros(10)
        true[1:3] = [-2., -.3]
        errors.append(np.linalg.norm(a @ true - b))
    assert errors[2] < errors[1] < errors[0]
    assert errors[2] < 2e-5


def test_sparse_units_support_and_empty_solution():
    y = np.random.default_rng(71).normal(size=(500, 2))
    a = library(y)
    true = np.zeros(10)
    true[1:3] = [-2., -.3]
    coef, details = sparse_fit(a, a @ true, .02)
    assert np.allclose(coef, true, atol=1e-12)
    assert details['support'] == ['q', 'v']
    # Changing feature units must invert the physical coefficients after normalization.
    units = np.geomspace(.001, 1000, 10)
    changed, _ = sparse_fit(a * units, a @ true, .02)
    assert np.allclose(changed * units, true, atol=1e-10)
    zero, _ = sparse_fit(a, a @ true, 1e9)
    assert np.array_equal(zero, np.zeros(10))


def test_passive_certificate_and_wrong_conservation():
    y = np.random.default_rng(12).normal(size=(1000, 2))
    a = library(y)
    true = np.zeros(10)
    true[[1, 2, 7, 9]] = [-2., -.3, -.1, -.2]
    coef, _ = sparse_fit(a, a @ true, .001, 'passive')
    assert np.allclose(coef, true, atol=1e-10)
    energy_dot = y[:, 1] * (a @ coef) - coef[1] * y[:, 0] * y[:, 1]
    assert np.max(energy_dot) <= 1e-12
    wrong, _ = sparse_fit(a, a @ true, .001, 'wrong_conservation')
    assert np.count_nonzero(wrong) == 1
    assert np.linalg.norm(a @ wrong - a @ true) > 1


def test_full_rollout_and_failure_receipts():
    t = np.linspace(0, 5, 81)
    coef = np.zeros(10)
    coef[1:3] = [-2., -.3]
    pred, receipt = rollout(t, [.7, -1.1], coef)
    assert receipt['status'] == 'ok'
    assert np.max(np.abs(pred - simulate_oscillator(2., .3, .7, -1.1, t))) < 1e-7
    coef[9] = 10
    pred, receipt = rollout(t, [1., 1.], coef)
    assert pred is None and receipt['status'] == 'failed'
    coef[:] = 0
    pred, receipt = rollout(t, [1., 1.], coef, max_calls=1)
    assert pred is None and receipt['reason'] == 'rhs_budget'


def test_observed_only_field_replay_and_second_derivatives():
    t = np.linspace(0, 1, 21)
    y = np.column_stack([np.cos(t), -np.sin(t)])
    before = torch.random.get_rng_state().clone()
    first, receipt, model = neural_observations(t, y, 13, steps=8)
    assert torch.equal(before, torch.random.get_rng_state())
    second, replay, _ = neural_observations(t, y, 13, steps=8)
    assert np.array_equal(first, second) and receipt == replay
    x = torch.tensor([.4], dtype=torch.float64, requires_grad=True)
    value = model(x)[0, 0]
    derivative = torch.autograd.grad(value, x, create_graph=True)[0]
    d2 = torch.autograd.grad(derivative, x)[0].item()
    h = 1e-4
    fd = (model(x + h)[0, 0] - 2 * value + model(x - h)[0, 0]).item() / h ** 2
    assert d2 == pytest.approx(fd, abs=1e-7)
    fitted, info = spline_observations(t, y)
    assert fitted.shape == y.shape and len(info['estimated_noise']) == 2
