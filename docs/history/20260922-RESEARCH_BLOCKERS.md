# RESEARCH_BLOCKERS.md

## P0 — scientific integrity
| ID | Blocker | Repo | Action |
|---|---|---|---|
| B0.1 | Confirmation evaluator absent | world-series | Keep DRAFT_NOT_AUTHORIZED; never seal holdout in-agent |
| B0.2 | Ultron verifier PLUMBING_ONLY; policies all succeed | world-series | Add discriminating tasks / cost metrics; do not claim routing gains |
| B0.3 | Exposition/status cards can lag metrics | workspace | Regenerate only from `runs/` |

## P1 — engineering for testability
| ID | Blocker | Action |
|---|---|---|
| B1.1 | Empty QL/QAPEN/… dirs look like repos | Document as placeholders; no migrate |
| B1.2 | Multi-seed aggregation not canonical | Add `scripts/falsify_and_seeds.sh` + RESULTS_SUMMARY |
| B1.3 | git_head often null | Optional first commit by user; content_hash already recorded |

## P2 — science depth
| ID | Blocker | Action |
|---|---|---|
| B2.1 | Faithful Celo2/ELO/PETS/DreamCoder ports absent | Keep `inspired_by`; do not name-claim |
| B2.2 | External datasets absent | Stay synthetic or document data boundary |
| B2.3 | Ablation matrix partially executed | Run CPU-TINY matrix entries marked RUN_NOW |

## P3
Docs polish, plot polish, CI remote (not run).
