# Post-study passive solver diagnostic

Declared after observing the three failed passive cells, before retries.
The four failed held trajectories all hit the RK45 6000-RHS work budget.
Retry every one with Radau and BDF at unchanged rtol1e-8, atol1e-10,
6000-RHS and state1e6 bounds. Record the full coefficients, error and maximum
observed energy increment; no coefficient intervention or parameter retuning.

This is a retrospective integration diagnostic. The original three failed cells
and incomplete primary aggregate remain unchanged regardless of retry success.
Success under implicit solvers would support numerical stiffness sensitivity,
not correct identification or a positive efficacy conclusion.
