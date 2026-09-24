# Post-study WFT cost-accounting supplement

This supplements the frozen efficacy protocol without changing its outcomes.
The first study records Laplacian setup but does not separately time public
domain/incidence construction. This supplement measures that work explicitly.

Use all 2,688 recorded model/graph conditions and their unchanged checkpoints.
Randomize case order once with seed 240928. Load inputs/checkpoints before the
timed kernels; report load time separately. For each case warm once, then measure
three repetitions of domain construction, Laplacian construction, matrix
exponential, application to 16 signals and eigendecomposition/projection. Keep
all samples; do not select the minimum. One float64 CPU worker, no accelerators.

Report retained domain tensor bytes, operator/transition/basis/output array
bytes, and global process peak RSS with platform units. Retained bytes are not
peak allocator consumption; cumulative process RSS cannot rank per-model memory.
Training costs remain the original complete training durations. Constraint
forward time is already included in those durations. Timing remains subject to
host contention, library overhead and the chosen 16-signal reuse count; it does
not establish equal-wall-time scientific superiority. Wall ceiling 1,800 seconds.
