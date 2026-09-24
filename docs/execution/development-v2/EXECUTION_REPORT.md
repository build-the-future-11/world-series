# Executed work, 24 September 2026

The bounded development work is executed and reviewed locally. This is not a
completion claim for the full World Series research blueprint.

- Preserved the initial repository in ae046d1 and committed numerical repairs
  and new studies in 429c788. Later commits contain analysis and documentation.
- Executed 80 main study runs across all nine namespaces, plus eight separately
  declared sensitivity runs. Every required campaign cell has an immutable run
  directory and artifact hashes. Completed-cell resume was exercised.
- Audited 288 primary digit tuning trials and 432 primary evaluation trajectories;
  the official pretrained Celo2 comparator adds 32 trials and 48 trajectories.
  The sensitivity study adds 432 trials and 432 trajectories.
- Replayed all 400 original learned-policy training trials exactly using the
  original archived source and stored arrays. This is same-host reproduction.
- Final regression suite: 57 passed, with one existing tensor-conversion warning.
  Eight falsification sanity checks passed; historical falsification evidence
  remained byte-for-byte unchanged. These checks do not validate the hypotheses.
- Produced complete method/condition tables, seed-level contrasts, a figure,
  a working manuscript, current status views and an independent-review handoff.

## Findings retained

The primary learned optimizer does not outperform tuned strong controls: at
32 steps its mean normalized loss AUC is 13.2809 versus AdamW's 6.4145 and
momentum's 7.9893 (lower is better). Official pretrained Celo2 yields 7.7454,
with unmatched pretraining and framework overhead explicitly disclosed.

The wider-grid/longer-training sensitivity retained 16 failed tuning trials and
four diverged evaluation trajectories. Two failures involve the full controller,
so its required aggregate is absent. This is instability evidence, not a
successful optimizer result. Original results remain unchanged.

All 17 failed polynomial rollouts remain in the WPINN denominators. Other
modules show scoped tradeoffs: causal memory helps against no-memory, but does
not dominate every control; quotient search has no measured savings in the
tested fixed-goal setting; hierarchy does not uniquely improve synthesis;
restricted learned tool selection helps on the declared finite DSL.

## Evidence and reproduction

- Primary artifact audit: AUDIT_RECEIPT.json and analysis.json.
- Sensitivity counts, selection checks, recomputed AUC and failures: sensitivity.json.
- Exact training replay: META_TRAINING_REPLAY.json.
- Final tests and sanity checks: FINAL_TEST_OUTPUT.txt and FINAL_CHECKS.json.
- Main tables: RESULTS.md; follow-up: SENSITIVITY.md; manuscript: RESEARCH_DRAFT.md.
- Review archive: deliveries/20260924-development/world-series-review.tar.gz.
  Its sibling receipt.json and verification.json bind the exact archive and
  source; scripts/verify_delivery.py checks all members without extracting them.

All commands use the repository Python environment, one numerical worker and
the workspace temporary directory. External dependencies and data sources have
separate provenance and locks. The archive does not redistribute Celo2 weights;
the pinned fetch source is recorded. No remote push or publication was performed.

## Outstanding scope

An independent evaluator and privately frozen protocol are still required for
confirmation. The prepared handoff specifies inputs and required receipts;
this development environment cannot supply the evaluator's identity or verdict.
Full MALIS/Q-APEN architectures, broad cross-dataset and PDE/sequence studies,
and publication-level novelty review remain open. Existing confirmation entries
remain DRAFT_NOT_AUTHORIZED.
