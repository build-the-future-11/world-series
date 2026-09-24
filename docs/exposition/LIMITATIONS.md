# Limitations and failures

- Planning ZIP was absent; pack reconstructed from the consolidated blueprint (see `../world_series_cursor_pack/PACK_PROVENANCE.md`).
- Module paths are thin slices: not full candidate-vs-baseline development studies with frozen power analysis.
- Q-APEN / qlearn baselines are minimal; Celo2/ELO/PETS faithful ports are deferred with `inspired_by` labeling required later.
- WPINN weak-form path currently uses FD targets in the smoke fit; full noisy-only weak assembly needs stronger quadrature tests before scientific claims.
- Dissipation heuristic on short noisy trajectories is brittle (thresholding).
- Ultron verifier is in-process `PLUMBING_ONLY`, not a sealed external evaluator.
- No remote CI was run; only local pytest/smoke.
- Git commits were not created in this session; manifests may show `git_head=null` with a source `content_hash`.
- Empty placeholder directories `QL/`, `QAPEN/`, … at workspace root were left untouched on purpose.
