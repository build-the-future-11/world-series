# Bounded recurrent updates on neural regression optimizees

Development study, 23 September 2026. This document describes the implemented
`neural_regression_v1` extension. It does not replace the original quadratic
records, certify the later discrete MALIS proposal, or authorize confirmation.
The completed experiment is `20260923T231444_deaee7ec`. Results are INCONCLUSIVE;
see [results and evidence](QLEARN_NEURAL_DEVELOPMENT_V1_RESULTS.md).

## Question and scope

Can a bounded, task-conditioned diagonal update policy transfer from small
neural regression tasks to a distinct teacher family, wider optimizees, and
longer adaptation horizons? The present experiment supplies a reproducible
development answer for constructed regression tasks. It cannot establish
performance on natural images, sequences, large models, or deployment systems.

Learning update rules through an outer objective follows a substantial existing
literature. Andrychowicz et al. formulate optimizer design as learning and study
recurrent update rules across several task classes
([2016](https://arxiv.org/abs/1606.04474)). Wichrowska et al. investigate
hierarchical recurrent architectures and generalization beyond training tasks
([2017](https://arxiv.org/abs/1703.04813)). Those papers motivate the family,
architecture-size, and horizon separation here; they do not qualify our
implementation as a reproduction of their systems.

Optimizer overhead is part of the scientific comparison. Metz et al. examine
memory, compute, and performance tradeoffs of learned optimizers
([2022](https://proceedings.mlr.press/v199/metz22a.html)). Consequently, equal
support-gradient counts and equal tuning-trial counts below must not be described
as equal total training cost or equal wall time. Stability and generalization
also depend on optimizer inductive biases; bounded outputs alone do not prove
convergence ([Harrison et al., 2022](https://arxiv.org/abs/2209.11208)).

## Tasks and separation

Each task has a seeded teacher, a support set, a separately sampled query set,
and an independently seeded optimizee initialization. Inputs are four-dimensional
standard normal vectors. A sampled linear projection plus bias is transformed
by the chosen teacher function. Meta-training uses linear and sine teachers;
selection uses quadratic teachers; evaluation uses hyperbolic-tangent teachers.
There is no observation-noise model in this version.

Each set contains 64 examples. The optimizee is an MLP with two hidden tanh
layers, each of width 64 during training and selection. Evaluation uses widths
64 and 128 with the same task data paired across widths. A linear optimizee
constructor is implemented and exercised in unit-level comparisons; the active
development matrix concerns the MLP, so it does not certify a separate linear
optimizee benchmark matrix.

There are four training, four selection, and four evaluation task identities
per training seed and evaluation width. Five explicit training seeds are used:
101, 211, 307, 401, and 503. Full arrays, task identities, initialization seeds,
and array hashes are retained. A query may score an outer objective, but its
inputs, targets, and loss cannot control adaptation updates or early stopping.
The query-poisoning regression checks this invariant directly.

## Update policy

For support loss L and current parameters theta, let g be its gradient and let
m be the exponential first-moment trace, initialized to zero for each task:

    m_t = 0.9 m_(t-1) + 0.1 g_t
    theta_(t+1) = theta_t - eta_t d_t * g_t

The multiplication is elementwise. Four features per parameter are supplied:
the gradient divided by its root mean square plus 1e-8, the similarly normalized
first moment, log(1 + L/c), and remaining steps divided by total requested steps.
The fixed task scale c is the support-target second moment floored at 1e-8. It
does not depend on a candidate's best observed loss.

The mean feature vector across parameters enters a two-layer GRU with 64 hidden
units per layer. A sigmoid head gives eta in (0.001, 0.1). A per-parameter
16-hidden-unit tanh network, receiving that parameter's four features and the
task context, gives the diagonal gate d in (0.1, 2.0). Recurrent state and moments
reset for every task. Parameter count and computational cost therefore depend
on the controller architecture, while per-parameter work scales with optimizee
size.

Three ablations accompany the full policy: zero remaining-budget feature,
feedforward task context in place of recurrence, and fixed unit diagonal gates.
Inactive modules are absent from the corresponding policy. The recurrence
ablation changes model capacity as well as statefulness; it is not a claim of
parameter-count matching.

## Meta-training and tuning

The outer objective averages query losses at adaptation steps 1 through 16,
divided by the task's fixed scale, then averages over the four training tasks.
Gradients pass through support gradients, feature construction, recurrent state,
and all 16 parameter updates. There is no first-order stop-gradient approximation
in the active meta-training matrix. A finite-difference regression checks the
outer derivative. Sequential task backward passes bound memory while retaining
the same average objective.

Each trial performs ten outer AdamW steps with weight decay 0.01 and global
gradient-norm clipping at one. Twenty log-spaced outer learning rates span
1e-5 through 0.003. Each trial begins from the same controller initialization
within a training seed; optimizer state persists across outer steps. Checkpoints
retain policy, optimizer, counters, and Python/NumPy/PyTorch random states. A
restore test verifies the next outer update exactly. The matrix runner retains
completed trials but does not yet automatically resume an interrupted whole
matrix from those trials.

Reference methods are PyTorch SGD, momentum SGD (momentum 0.9), and AdamW
(weight decay 0.01). Each receives twenty log-spaced learning rates from 1e-4
through 0.2. All methods select hyperparameters using mean normalized query-loss
area under the adaptation-step curve on the selection partition only. The
evaluation partition does not choose a trial. Equal numbers of trials do not
equalize meta-training compute.

## Evaluation and accounting

Each selected method is evaluated at horizons 16, 32, and 64 on both widths.
The full matrix contains 700 tuning trials and 840 evaluation trajectories.
Its maximum support-gradient count is 332,160: 19,200 baseline-selection steps,
256,000 learned-policy training steps, 25,600 learned-policy selection steps,
and 31,360 evaluation steps. Early divergence can reduce the executed count;
that reduction must be reported alongside failed trials, not represented as
completed work. Forward counts and measured trajectory times are also retained.

Evaluation detaches the outer graph while retaining numerically identical
updates. An exact trajectory-equivalence test checks this against the full
differentiable path. This avoids charging evaluation for an unused meta-gradient
graph. CPU float64 and one BLAS/OpenMP thread form the reference environment.

Raw support losses, query losses including initialization, elapsed times,
requested/executed steps, divergence flags, and complete/incomplete indicators
are saved for every attempted trajectory. Gradient-step AUC includes the initial
point and uses trapezoidal integration. Measured-time AUC uses the observed
timestamps. Neither quantity proves an equal wall-time-budget advantage.

Nonfinite query losses or a normalized query loss exceeding 1e6 flag divergence.
Only support/parameter failure can stop adaptation. No failed member is silently
removed from an aggregate: if a group contains an incomplete or divergent row,
its ordinary mean endpoint is left absent and the full denominator is reported.

## Analysis contract

The analysis is developmental and not externally preregistered. The principal
descriptive comparison is the full policy versus tuned AdamW at width 128 and
horizon 64. Report all other methods, widths, horizons, and ablations alongside
it. Positive paired differences mean baseline AUC minus candidate AUC is positive.
First average paired task differences within each training seed; five seed means
are the independent replication units. Do not treat the 20 task rows as twenty
independent trained policies.

Report every seed difference, its mean, and a two-sided exact sign-flip diagnostic
over all 32 sign assignments, conditional on all five complete, finite seed
comparisons. This diagnostic requires sign symmetry under its null. Five seeds
have coarse inferential resolution; even five same-sign nonzero differences
cannot yield a two-sided exact p-value below 0.0625. Exploratory secondary
comparisons cannot support a multiplicity-adjusted superiority claim here.
Any missing required comparison blocks a complete-matrix conclusion.

## Evidence and limitations

The immutable source archive and per-file hashes are stored in
`.portfolio/verification/WS-neural-candidate-20260923-v2` on PRO-BLADE. The original
failed JSON-parser run and its preceding source candidate remain preserved.
The corrected candidate changes parsing only; the numeric configuration file
is byte-identical. Tests, profiling, and research outcomes are separate records.

This implementation and matrix do not close the original World Series program.
Natural-data tasks, additional qualified learned-optimizer and initialization-only
comparators, the later MALIS actions, an independent reproduction, and external
protocol review remain incomplete. Results and all failed tuning trials are now reported in the linked results document.
The completed development matrix does not close these separate obligations.
