# Structured oscillator development study v1

Status: development, DRAFT_NOT_AUTHORIZED for confirmation. Freeze source before
running. No external independent replication or general PDE claim. The original
288 fits, 17 failures, and retrospective diagnostics remain separate.

## Data and decision rule

Eight generator seeds: 2503, 2521, 2531, 2539, 2543, 2549, 2551, 2557.
Physical laws (k,c): (1,0), (2,.3), (4,.8). Each physical law has five observation
conditions: 81 clean samples; 81 samples/noise .1; 41 samples/noise .1;
81 nominal samples/30% interior missing/noise .1; and 81 samples/noise .1 with
training and selection initial amplitudes scaled to .1 (low excitation).
Time horizon [0,5]. Noise is additive iid Gaussian in q and v. Endpoints retained.
Two complete training trajectories, one complete selection trajectory, and two
clean evaluation trajectories with fresh initial conditions. Whole trajectory
IDs and arrays saved; no pointwise split. Low-excitation evaluation uses ordinary
amplitude, explicitly testing extrapolation. No clean training states, true
parameters, or true noise level are passed into fit/smoothing functions.

Primary: all-term held-initial-condition rollout MSE. Report both mean among
successful integrations and failure count; no finite aggregate performance
claim if a method has failures. Two held trajectories first averaged within
cell, 15 law/condition cells within seed, then eight seeds. No condition cherry
picking. Support recovery and coefficient error secondary; cannot rescue the
primary. True held initial state is supplied equally to every rollout method.

## Methods and information budgets

All discovered models use the same ten degree<=3 polynomial acceleration terms
1,q,v,q2,qv,v2,q3,q2v,qv2,v3 with q'=v. Internal STLS uses RMS column scaling,
eight support iterations and refits; threshold candidates 0,.02,.1. Select by
rollout MSE against the one noisy selection trajectory, initialized from its
observed first state. Failed selection rollouts score infinity; if all fail,
retain the first threshold by declared order and report selection failure.
All candidates and selection receipts saved; no evaluation-dependent selection.

Methods: raw derivative STLS; raw weak STLS; spline weak STLS; neural weak STLS;
neural derivative STLS (weak-form ablation); neural weak odd-symmetry STLS;
neural weak passive STLS; neural weak wrong-conservation STLS; neural weak dense
least squares (sparsity ablation); known-support derivative fit (privileged
q/v support); official PySINDy derivative STLSQ; official PySINDy weak STLSQ.
Dense and known-support methods have threshold0 only. Official thresholds use
the package's physical coefficients without normalization; the three-value
grid has the same trial count but a different threshold coordinate system,
explicitly not identical regularization strength. Official weak designs use
32 seeded subdomains per trajectory, halfwidth1.25 and polynomial degree3;
the same generated design is reused for all thresholds.

The internal compact weak form uses 16 analytic polynomial bumps, halfwidth1.25
and irregular-grid trapezoid quadrature. Spline strength1 uses a robust observed
second-difference noise estimate (heuristic on irregular grids). Each neural
field has two width32 tanh layers, two outputs, float64 CPU; 400 Adam updates
at .01 on observation MSE only. Fixed budget, no early stopping or held labels.
Save every training loss and model state; each smoother reused across methods.
This is a learned observation field plus sparse discovery, not a jointly
physics-trained neural field. That architectural distinction stays explicit.

Odd symmetry removes even-degree terms. Passive structure additionally assumes
a valid quadratic energy certificate: q coefficient <=0 and v,q2v,v3 <=0;
all other coefficients zero. It is extra physical knowledge, not an
information-matched unconstrained model. Known support is separately labeled.
Wrong conservation retains only q and is intentionally false for damped laws.

## Bounds, provenance and evaluation

One numerical worker, CPU threads1, at most120 cells, 240 neural observation
fits, 96,000 Adam updates, at most7,680 selection/evaluation integrations.
RK45 rtol1e-8, atol1e-10, 6000 RHS calls, state magnitude1e6. Preserve every
failure and full coefficients; never silently clip damping or nonlinear terms.
Each cell saves source identity, input arrays, all model candidates and timing;
abort on unexpected exceptions with a distinct failure receipt. Profile uses
seed2499, separate directory, and does not count in the eight-seed study.
Protocol or implementation repair after profile requires a new frozen identity.

Official package qualification: PySINDy2.1.0 MIT, exact installed-source hashes
and dependency pins in WPINN_PYSINDY_QUALIFICATION.json/REQUIREMENTS.txt. Official
[weak ODE documentation](https://pysindy.readthedocs.io/en/stable/examples/12_weakform_SINDy_examples/example.html)
supports the API used. This is a qualified package comparator, not a reproduction
of a published WSINDy result. A subsequent audit must replay saved predictions,
check splits and selected thresholds, and verify source/artifact hashes.
