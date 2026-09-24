# Development execution protocol, 24 September 2026

State: DRAFT_NOT_AUTHORIZED. These are visible development tasks, not a sealed
confirmation set. Existing raw runs and original configs are retained unchanged.
The initial repository snapshot is commit ae046d1. New studies use a separately
committed source candidate and preserve all failed attempts.

## Scope and denominators

The declared seeds are 101, 211, 307, 401, 503, 601, 701, 809. Eight non-QLearn
modules each receive eight development runs. QLearn receives eight natural-digit
meta-training runs with nine methods, four tuning trials per method, and two
evaluation tasks at three horizons. Seeds are the aggregation units; task rows
within seeds are dependent. All seeds share the finite underlying benchmark and
must not be treated as independent datasets.

All numerical jobs run serially on CPU. Each run has a wall-time and operation
budget. The matrix runner locks its campaign directory, binds source and config
hashes, and verifies every file before reusing a completed cell. Interrupted cells
receive new run IDs on retry; previous receipts are not overwritten. This is
cell-level resume, not mid-meta-training resume. Storage and memory monitoring
are distinct from an operating-system enforced memory cap.

## Evaluations

- QLearn: UCI Optical Recognition of Handwritten Digits, CC BY 4.0, original
  source files retained with SHA256 provenance. Binary +/-1 squared-loss tasks:
  meta-train on digits 0/1 and 2/3, select on 4/5, evaluate 6/7 and 8/9. Evaluation
  supports use original training writers; queries use original held writers.
  Inputs divide by the published range maximum 16; no query-fitted preprocessing.
  Two-hidden-layer width-24 tanh optimizees, 48 support and query examples per
  task, 8 adaptation steps in training, 4 outer steps, 8/16/32 evaluation steps.
  Full, reset-state, no-budget, no-gates, feedforward, SGD, momentum, AdamW and
  initialization-only controls are all reported. Reset-state retains exactly
  the full GRU parameterization. The initialization-only control meta-learns
  initial parameters with exact gradients and a fixed 0.03 inner SGD rate.
  It is an internal MAML-style control, not a claimed paper reproduction.
- Q-APEN: causal context memory, no-memory, random retrieval, one-expert memory,
  recent-history, cumulative and fixed controls. Four cycles of 80 ordinary and
  20 rare observations; score all/rare/ordinary/first-five-return observations.
  Retrieval uses previous observations only. The original candidate never read
  its memory; this intervention is a new bounded mechanism, not evidence that
  the entire lifecycle architecture is implemented. Equal prediction-call
  counts do not imply equal computation or parameter counts.
- QWIPII: sampled permutations of 4/5/6 labeled tokens, six per size per seed,
  12/120 expansion caps, brute/quotient/ranking searches. Replay every returned
  path in original coordinates. Canonical keys do not justify changing path
  coordinates. Distinct fixed goals can eliminate any quotient savings.
- WCODE: all distinct finite-domain behaviors in the existing 53-program pool,
  public examples sampled independently per seed, evaluation on remaining
  integers in [-8,8]. Candidate caps 8/24/53. Structural rankers cannot execute
  the full pool for free. These rankers remain untrained heuristics.
- WFIM: finite random supports, degrees 2/3/4, 12 cases each. Compare degree
  truncation, top-k at matching term count, and transported multiplication.
  Report coefficient error, terms, bytes and time separately. Matching terms
  does not match byte count; transport parameters are extra storage.
- WFT: weighted path graphs at sizes 12/24, observation noise 0/0.1/0.5, 8/32
  training vectors; score 32 independent vectors. Ridge and constrained
  Laplacian fits share observations. Fixed unit-weight and true-graph oracle
  baselines are labeled separately. Refit at each size is not transfer.
- WPINN: (k,c)=(1,0),(2,0.3),(4,0.8), observation noise 0/0.02/0.1. Fit on one
  trajectory and score a clean independent initial condition of the same law.
  Roll out every fitted polynomial term; never silently drop nonlinear terms
  or clip damping. Report integration failures in the denominator. The known
  support baseline is oracle-assisted. This is oscillator identification, not
  general PDE discovery.
- CWLNN: 12 training path graphs at size 24, eight independent evaluation graphs
  at sizes 24/48/96. Target is four-hop diffusion plus a graph mean, independent
  of the candidate hierarchy. Flat, hierarchy, routed, and limited-attention
  features each receive equal-sized ridge readouts. Report graph-level error
  and feature time. These are fixed features, not trained universal backbones.
- Ultron: actual bounded DSL solvers as tools; every policy gets all five tools
  and the same candidate caps. Split entire semantic program families for
  router training/evaluation. Static, measured-cheapest, unrestricted random,
  and nearest-neighbor learned selection execute a solver and verify its output
  on held task examples. Training tool calls count separately. This restricted
  routing study cannot establish general research-agent capability.

## Analysis and claim rules

Publish all method/condition cells, failures, raw trajectories and per-seed
contrasts. Missing or nonfinite rows invalidate the corresponding ordinary mean;
do not report a successful finite-only subset. QLearn's primary descriptive
contrast is full minus tuned SGD step-AUC at 32 steps. Secondary contrasts
include reset-state and other methods. Exact paired sign-flip diagnostics use
seed means and require sign symmetry; secondary diagnostics receive Holm
adjustment. Neither nonsignificance nor small differences prove equivalence.
Wall time includes implementation overhead and host contention; step matching
does not equalize meta-training or wall-time costs.

External pretrained comparator evaluation, discrete MALIS actions, original
full-meta-training replay, independent verification and confirmatory protocol
review have separate receipts and scope. No local artifact may assert that an
external evaluator has been sealed or that independent replication occurred.
