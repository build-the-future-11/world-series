# World Series current research status

Updated 24 September 2026 from named executed campaigns. This supersedes the September 22 root status snapshot; historical copies remain in docs/history/.

**Verdict:** Runnable and benchmarked within bounded development scopes. No full-project, novelty, independent-replication or publication-readiness certification.

Engineering: 57 tests passed for the development candidate; 80 main run receipts passed the artifact audit. All 64 non-QLearn cells, eight natural-digit cells and eight discrete-action cells completed.

Original full meta-training replay: IN PROGRESS; no completion claim. Same-host replay is not independent replication.

There is one implementation repository, world-series/, with nine namespaces. The nine sibling named directories remain empty placeholders; world_series_cursor_pack is planning material.

| Module | Status | Evidence and limit |
|---|---|---|
| qlearn | BENCHMARKED / INCONCLUSIVE | Eight-seed natural-digit study: 288 tuning trials, 432 trajectories; official pretrained Celo2 adds 48 trajectories. Full mean AUC 13.2809 vs SGD 11.9562, AdamW 6.4145, Celo2 7.7454 at 32 steps. No general optimizer advantage established. Discrete action prototype evaluated separately. |
| qapen | BENCHMARKED / INCONCLUSIVE | New causal context-memory intervention with all/rare/ordinary/return metrics and matched prediction calls. Tradeoffs remain: single-expert memory improves overall mean; fixed ensemble improves rare-regime mean. Legacy candidate memory is write-only. |
| qwipii | BENCHMARKED / INCONCLUSIVE | Canonical keys retain concrete replayable paths. Exhaustive 3/4-token regression tests pass. No quotient savings on tested distinct fixed-goal puzzles; ranking-only control performs better under the limited cap. |
| wcode | BENCHMARKED / INCONCLUSIVE | Eight-seed finite-DSL matrix with honest candidate accounting. Hierarchical, flat and token heuristics tie at the 24-candidate cap. Encoders are untrained structural heuristics. |
| wfim | BENCHMARKED / INCONCLUSIVE | Finite support/degree/cost matrix and an actual top-k associativity counterexample. Truncation/transport identities do not establish learned downstream benefit or new algebra. |
| wft | BENCHMARKED / INCONCLUSIVE | Weighted-path noise/sample/size matrix uses matched Laplacian targets. Unit-weight and true-graph oracle baselines are distinguished. Refit at each size is not transfer. |
| wpinn | BENCHMARKED / INCONCLUSIVE | Three laws and three noise levels; independent held initial conditions. All polynomial terms evaluated with bounded integration. Seventeen failed rollouts remain in denominators; affected means are absent. |
| cwlnn | BENCHMARKED / INCONCLUSIVE | Matched-size trained readouts on fixed sparse representations; graph sizes 24/48/96. Aggressive routing hurts the declared diffusion task. No universal-backbone evidence. |
| ultron | BENCHMARKED / INCONCLUSIVE | Discriminating finite-DSL routing with identical tools/caps and disjoint semantic training/evaluation families. At cap 24: learned 81.94%, cheapest 66.67%, random 58.33%, static 44.44%. Not a general agent or sealed external evaluation. |

## Evidence

- Current protocol, complete tables, CSVs, figures and draft: world-series/docs/execution/development-v2/.
- Raw immutable runs: world-series/runs/; canonical campaign receipts: world-series/campaigns/.
- Initial baseline commit: ae046d1. Numerical development candidate: 429c788. Later analysis/documentation commits are separate.
- UCI source files, attribution and hashes: world-series/data/optdigits/.
- Official Celo2 revision, weights hash and isolated dependency lock: CELO2_PROVENANCE.json and celo2-requirements.txt.

## Remaining work

Independent confirmation is BLOCKED on an external evaluator and privately frozen protocol. The concrete handoff is INDEPENDENT_EVALUATION_HANDOFF.md. Every existing confirmation registry entry remains DRAFT_NOT_AUTHORIZED.

Broader model development remains open: full proposed MALIS/Q-APEN architectures, trained relational synthesis encoders, general PDE/graph/sequence workloads, and stronger cross-dataset validation. These are not completed by the bounded studies. A working manuscript exists; submission and public release have not occurred.

No completion percentage is assigned: software execution, narrow mathematical properties, development results and independent scientific support are separate dimensions.
