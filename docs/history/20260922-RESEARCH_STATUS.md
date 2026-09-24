# RESEARCH_STATUS.md — World Series workspace

**Audit date:** 2026-09-22  
**Scope:** `/Volumes/PRO-BLADE/World-Series` only (this workspace).  
**Integrity rule:** Outcomes below cite on-disk artifacts. Confirmation protocols remain `DRAFT_NOT_AUTHORIZED`. No fabricated wins.

## Workspace inventory

| Path | Kind | Classification | Notes |
|---|---|---|---|
| `world-series/` | Implementation monorepo | **A** (runnable, scientifically testable at toy scale) | Only code with tests + real `runs/` |
| `world_series_cursor_pack/` | Planning pack (reconstructed) | **D** (spec/planning) | Validators ≠ trained models |
| `QL/`, `QAPEN/`, `QWRIPII/`, `WCNNCODE/`, `WFIM/`, `WFT/`, `WPINN/`, `CWLNN/`, `Ultron/` | Empty placeholders | **D** | No source; do not treat as repos |
| `WORLD_SERIES_COMPLETE_BLUEPRINT.md`, `REFERENCES.md` | Planning docs | **D** | Provenance for pack |

There are **not** nine independent research git repositories with separate train/eval histories. There is **one** installable package with nine namespaces.

---

## PROJECT: world-series (monorepo)

### Scientific objective
Test whether nine explicit mechanisms improve separately measurable tasks under explicit budgets, without claiming universal intelligence.

### Core hypotheses (one per namespace)
| NS | Hypothesis (falsifiable) |
|---|---|
| qlearn | Bounded task/budget-aware diagonal update improves held-out AUC loss-vs-step vs tuned fixed optimizers |
| qapen | Adaptive experts+engrams beat fixed/recent/no-memory controls on returning-regime NLL at matched cost |
| qwipii | Verified quotient search preserves liftability and can reduce expansions vs brute; approximate ranking must not prune |
| wcode | Hierarchical relational ranking improves solve@budget vs uniform/token/flat on shared enumerator |
| wfim | Degree truncation preserves associativity; arbitrary top-k need not; transport is isomorphic (efficiency question) |
| wft | Constrained learned operator improves held prediction vs unconstrained/fixed under stated constraints |
| wpinn | Weak-form sparse ID + appropriate dissipation beats wrong-conservation / data-only under held-out rollout |
| cwlnn | Sparse hierarchy/routing competitive accuracy–cost vs flat/budgeted-attention without hidden dense all-pairs |
| ultron | Evidence-aware/learned routing beats static/random/cheapest with **identical** tools+budgets on verified completion |

### Novelty claim
**Not established.** Pack explicitly maps large prior art (learned opts, PINNs, program graphs, etc.). v0.1 asks mechanism isolation questions.

### Status (evidence-based)

| Dimension | Status | Evidence |
|---|---|---|
| Implementation | Thin but real paths exist for all 9 | `src/world_series/*`, pytest green |
| Data | Synthetic generators only | No external datasets |
| Training | Tiny CPU meta/fit only | `configs/*/smoke.yaml`, `dev.yaml` |
| Evaluation | Smoke/dev runners write manifests | `runs/*/metrics.json` |
| Baselines | Present at toy scale | qlearn AdamW/SGD/mom; qapen fixed/recent; etc. |
| Ablations | Partial | See `experiments/ABLATION_PLAN.md` |
| Reproducibility | Local seeds + content_hash; git often dirty/null | manifests |
| Documentation | README + exposition; scientific audit in progress | this file + `docs/` |
| Paper | No manuscript; blueprint only | N/A |
| Known failures | WPINN IBP sign bug fixed; Ultron 100% completion on easy tasks (non-discriminating); qapen recent-memory can beat candidate on mean NLL | runs |
| Scientific risks | Toy domains; PLUMBING_ONLY verifier; DRAFT protocols; underpowered seeds | |
| Engineering risks | Empty sibling dirs confuse inventory; run “latest” must sort by mtime | |
| Compute blockers | None for CPU-TINY; no GPU required for current suite | |
| Immediate next action | Multi-seed falsification harness + aggregate RESULTS_SUMMARY from real runs | |
| Completion % | **~45%** toward publication-ready toy study; **~5%** toward any confirmatory paper claim | Components: core 80%, refs 70%, baselines 50%, multi-seed 20%, paper 0%, confirmation 0% |

### Classification: **A** (runnable & testable) with **E**-like confirmation blocker (no sealed evaluator)

---

## Placeholder directories (QL…Ultron)

| Field | Value |
|---|---|
| Classification | **D** |
| Completion % | **0%** (empty) |
| Immediate next action | Ignore for science; use `world-series/` only |

---

## world_series_cursor_pack

| Field | Value |
|---|---|
| Classification | **D** |
| Status | Planning PASS (`artifacts/planning_validation.txt`) |
| Completion % | **100% as planning**; **0% as software** |
| Risk | Confusing planning validators with implementation tests |

---

## Cross-cutting integrity findings

1. **No confirmation authorized.** `experiments/registry.json` → `DRAFT_NOT_AUTHORIZED`.
2. **Negative / inconvenient signals already present** (must preserve): qapen recent-memory mean NLL can undercut candidate; qwipii solve fraction &lt; 1; Ultron policies not differentiated on easy tasks.
3. **No TODO/FIXME stubs** found in `src/` (grep). Risk is **thin science**, not empty `pass` bodies.
4. **Do not** treat smoke SUCCEEDED as SUPPORTED.
