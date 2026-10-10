# WFT full-mass numerical correction

State: SMOKE_PASSED (23 WFT tests). This is a development implementation correction, not new
benchmark or confirmatory evidence. All retained campaigns and conclusions stay
at their existing evidence boundary.

The previous `weighted_spectral(L, M)` read only `diag(M)`, although its public
API accepted a full matrix and `encode` used that full matrix. For
`L=[[2,-1],[-1,2]]` and `M=[[2,.5],[.5,1]]`, the generalized eigen-equation
residual was 1.1456439237 and the mass-orthogonality residual was 0.5.

The corrected dense path uses `M=C C.T`, solves the symmetric whitened problem
`C^-1 L C^-T`, and transforms its eigenvectors by `C^-T`. The diagonal path
retains its exact previous arithmetic. Inputs must be finite, real, symmetric,
nonempty square matrices of equal size, and M must be positive definite.

Regression checks compare a dense example to SciPy's independent generalized
solver, verify the original eigen-equation, reconstruction, mass-weighted
Parseval identity and permutation covariance, and require exact equality on the
legacy diagonal path. This does not establish a downstream learning benefit.

Reproduce with `PYTHONPATH=src python -m pytest tests/wft -q`.
