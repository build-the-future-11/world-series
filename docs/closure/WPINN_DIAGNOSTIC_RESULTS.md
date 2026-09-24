# Historical WPINN failure interventions

All 17 original failed values remain unchanged. The raw supplement is
campaigns/wpinn-diagnostics-v1/results.json; its SHA256 and frozen implementation
commit are recorded in WPINN_DIAGNOSTIC_RESULTS.json.

| Intervention | Successful integrations /17 |
|---|---:|
| Saved polynomial, RK45 | 0 |
| Saved polynomial, DOP853 | 0 |
| Saved polynomial, Radau | 0 |
| Remove fitted quadratic terms; retain fitted linear terms | 16 |
| Replace linear terms with true coefficients; retain quadratic terms | 3 |

For the ten weak/wrong-conservation failures, all 40 quadrature/test-derivative
factorial cells fail. Analytic derivatives of the same six tests and corrected
trapezoid endpoints do not rescue these fits. The original gradient/gradient
coefficients were reconstructed and checked before comparing interventions.

The lone failure after removing quadratic terms is seed101, k4/c.8/noise.1,
weak fit: q coefficient -13.62916 and v coefficient +8.12643. Positive v feedback
is negative damping, contrary to the generating dissipative system. Even the
linear-only counterfactual exceeds the declared state cap.

These are finite, privileged interventions. They show that the fitted nonlinear
terms matter to 16 integration failures under this protocol, and that a change
of integrator or these quadrature details does not make the saved fits usable.
They do not prove an exclusive causal origin in conditioning versus sparse
support selection, nor mathematical finite-time blowup: a work/state cap is a
bounded numerical failure. Identifiability and support-selection attribution
remain broader requirements rather than silently checked items.
