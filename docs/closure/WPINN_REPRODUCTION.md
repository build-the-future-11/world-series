# WPINN local reproduction

Original numerical environment: .venv, Python3.12.14. The official comparator is
installed separately in .venv-wpinn, pinned by WPINN_PYSINDY_REQUIREMENTS.txt.
Its package source/license hashes were checked during qualification. The
campaign uses the original interpreter with the comparator site-packages first
on PYTHONPATH; NumPy2.5.3 and SciPy1.18.1 match the original environment versions.
The separate environment does not inherit the original venv's Torch, so running
the whole study directly with .venv-wpinn/bin/python is not the recorded setup.

From the repository root (replace output directories with fresh paths; scripts
refuse existing campaign directories):

```sh
rtk proxy env PYTHONPATH=src:.venv-wpinn/lib/python3.12/site-packages \
  TMPDIR="$PWD/.work-tmp" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  .venv/bin/python scripts/closure/wpinn_study.py \
  --output campaigns/wpinn-structured-replay
```

The recorded candidate is de5df5e. Restore that source in a separate checkout
before exact replay; later project development changes the whole-source hash.
The source identity includes every implementation Python file, the runner, and
the protocol. Neural observation checkpoints are local trusted artifacts and
loaded with weights_only=True. Every loss, input array, smoothed array, design,
threshold candidate, selection score and held rollout receipt is retained.

The official package emits an AxesWarning for one-dimensional target labeling.
Qualification and campaign complete despite that warning; no warning is treated
as successful scientific evidence. Original code source and dependency pins are
recorded separately from the claim of compatibility.

Audit command uses the same environment prefix and
scripts/closure/analyze_wpinn.py. It currently targets the canonical campaign
directory; copying results to other locations requires adapting only that path,
not the numerical implementation. Portable final packaging remains a separate
collection requirement. This local receipt is not a clean-room replication.
