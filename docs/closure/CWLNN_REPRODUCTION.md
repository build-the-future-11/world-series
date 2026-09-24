# CWLNN reproduction receipt

Frozen numerical source:6d81c14. Original .venv Python3.12.14, Torch2.14.0,
NumPy2.5.3, SciPy1.18.1. One CPU worker, float64, deterministic Torch algorithms,
one Torch/OpenBLAS/OpenMP thread. Full suite:95 passed (existing QLearn scalar
conversion warning retained). Seven new tests cover sparse/dense agreement,
actual quotient edges, boundaries, budgets, tied priorities, permutations,
surrogate gradients, empty/single-node cases, attention bounds and a10,000-node
sparse forward. The initial empty-graph test helper was repaired before freezing.

From a checkout of the recorded numerical source, use a fresh output directory:

```sh
rtk proxy env TMPDIR="$PWD/.work-tmp" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  .venv/bin/python scripts/closure/cwlnn_study.py \
  --output campaigns/cwlnn-conditional-replay
```

The profile uses --profile and a separate directory/seed. Source identity hashes
all implementation files, the runner and protocol. Never use a changed source
under an old campaign identity. Analysis lives in scripts/closure/analyze_cwlnn.py
and expects the canonical campaign path; it creates a fresh one-model training
replay directory. The full study retains480 files,128 trained models,256
checkpoints,115,200 timing repeats, and23,040 prediction receipts. Study elapsed
time164.36s; global process peak RSS327,794,688 bytes on macOS. RSS is not a
per-model peak and timings are from an uncontrolled host.

Separate shape-allocation probe: scripts/closure/cwlnn_allocation.py. It records
one instrumented forward at1k/10k/100k nodes and1% refinement, refusing an existing
output directory. Raw campaigns remain immutable; portable collection packaging
and independent replication are still separate requirements.
