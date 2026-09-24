# WPINN retrospective failure interventions

Development only; DRAFT_NOT_AUTHORIZED for confirmation. Original 288 fits and
17 failed rollout values stay immutable. This supplement operates on all 17
failed rows in campaigns/closure-20260924/wpinn.json without selecting successes.

For each exact saved polynomial, compare RK45, DOP853 and Radau at rtol 1e-8,
atol 1e-10, 6000 RHS calls and state magnitude 1e6. These are stricter tolerances
but a larger work budget than the historical check. A successful retry does not
retroactively replace a failed original value. Report reasons and cross-solver
agreement where available; disagreement is unresolved integration sensitivity.

Intervene separately by removing the three fitted quadratic terms (retaining
the fitted linear coefficients), and by replacing only the two linear
coefficients with the true -k/-c (retaining fitted quadratic terms). Both are
oracle diagnostic interventions, never benchmark competitors or causal claims
about the fitting algorithm. They can identify which parts of a saved vector
are necessary for a bounded-horizon integration failure under these controls.

For all original weak/wrong-conservation failures, recompute the original
five-term normalized design using the original six global tests. Cross the
original gradient integration weights versus true trapezoid weights with
numerical versus analytic derivatives of those SAME tests (2x2). Use the same
original thresholded least-squares implementation and threshold .05. Preserve
wrong-conservation's final zero damping step. This isolates quadrature and test
derivative changes without replacing the library or support algorithm.
Record coefficients, singular values and rollout outcomes for all four cells.
No post-hoc best cell is used as a research result.

Clean-data or true-coefficient interventions are explicitly privileged. A
stable counterfactual is evidence about that finite intervention, not proof of
one exclusive cause, support-selection consistency, or population performance.
