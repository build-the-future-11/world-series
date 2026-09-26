"""Teacher strata for WFT misspecification studies."""
from world_series.wft.constraints import teacher, domain, restriction
import torch


def coarsen_resid(model):
    fine, coarse = domain(16, level=0), domain(16, level=1)
    a, b = model.action(fine), model.action(coarse)
    r = restriction(16)
    return float(((r @ a - b @ r) ** 2).sum().detach())


def test_compatible_nearly_equitable():
    assert coarsen_resid(teacher(7, "compatible")) < 1e-20


def test_sine_perturbed_has_sine_modes():
    c = teacher(7, "sine_perturbed").coefficients[0].detach()
    assert float(c[2].abs()) > 0.2 and float(c[4].abs()) > 0.2


def test_unequal_degree_breaks_coarsening():
    assert coarsen_resid(teacher(7, "unequal_degree")) > 1.0
