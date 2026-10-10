import numpy as np
import pytest
from scipy.linalg import eigh

from world_series.core.contracts import WorldSeriesError
from world_series.wft.laplacian import decode, encode, weighted_spectral


def test_full_mass_solves_generalized_problem_and_preserves_energy():
    stiffness = np.array([[2.0, -1.0], [-1.0, 2.0]])
    mass = np.array([[2.0, 0.5], [0.5, 1.0]])
    eigenvalues, orthogonal, basis = weighted_spectral(stiffness, mass)
    np.testing.assert_allclose(eigenvalues, eigh(stiffness, mass, eigvals_only=True))
    np.testing.assert_allclose(stiffness @ basis, (mass @ basis) * eigenvalues, atol=1e-13)
    np.testing.assert_allclose(orthogonal.T @ orthogonal, np.eye(2), atol=1e-13)
    np.testing.assert_allclose(basis.T @ mass @ basis, np.eye(2), atol=1e-13)
    signals = np.array([[1.0, -3.0, 2.0], [2.0, 5.0, -1.0]])
    coefficients = encode(signals, basis, mass)
    np.testing.assert_allclose(decode(coefficients, basis), signals, atol=1e-13)
    np.testing.assert_allclose(coefficients.T @ coefficients, signals.T @ mass @ signals)


def test_diagonal_mass_keeps_original_numerical_path():
    stiffness = np.array([[2.0, -1.0], [-1.0, 2.0]])
    mass = np.diag([2.0, 3.0])
    inverse_root = 1.0 / np.sqrt(np.diag(mass))
    old_values, old_q = np.linalg.eigh(inverse_root[:, None] * stiffness * inverse_root[None, :])
    actual = weighted_spectral(stiffness, mass)
    for found, expected in zip(actual, (old_values, old_q, inverse_root[:, None] * old_q)):
        np.testing.assert_array_equal(found, expected)


def test_full_mass_permutation_covariance():
    rng = np.random.default_rng(71)
    a = rng.normal(size=(5, 5))
    b = rng.normal(size=(5, 5))
    stiffness = a @ a.T
    mass = b @ b.T + np.eye(5)
    order = np.array([3, 0, 4, 2, 1])
    values, _, basis = weighted_spectral(stiffness, mass)
    perm_values, _, perm_basis = weighted_spectral(stiffness[np.ix_(order, order)], mass[np.ix_(order, order)])
    np.testing.assert_allclose(values, perm_values, atol=1e-12)
    projector = basis[:, :2] @ basis[:, :2].T @ mass
    perm_projector = perm_basis[:, :2] @ perm_basis[:, :2].T @ mass[np.ix_(order, order)]
    np.testing.assert_allclose(perm_projector, projector[np.ix_(order, order)], atol=1e-12)


@pytest.mark.parametrize("mass", [
    np.array([[1.0, 2.0], [2.0, 1.0]]),
    np.ones((2, 2)),
    np.array([[1.0, 0.1], [0.0, 1.0]]),
    np.diag([1.0, np.nan]),
    np.diag([1.0, -1.0]),
    np.eye(3),
    np.ones(2),
])
def test_invalid_mass_is_rejected_instead_of_ignoring_off_diagonals(mass):
    with pytest.raises(WorldSeriesError):
        weighted_spectral(np.eye(2), mass)


@pytest.mark.parametrize("stiffness", [
    np.array([[1.0, 1.0], [0.0, 1.0]]),
    np.array([[1.0, np.inf], [np.inf, 1.0]]),
    np.eye(2, dtype=complex) * (1 + 1j),
])
def test_invalid_operator_is_rejected(stiffness):
    with pytest.raises(WorldSeriesError):
        weighted_spectral(stiffness, np.eye(2))
