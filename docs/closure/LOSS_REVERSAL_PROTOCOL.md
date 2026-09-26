# Loss-reversal successor protocols — frozen 26 September 2026

**Confirmation:** `DRAFT_NOT_AUTHORIZED` (development successors; not independent confirmation).  
**Rule:** Historical campaigns stay immutable. New studies use new output directories and this protocol identity. Do not retune after seeing evaluation outcomes while keeping a confirmation label.

These successors address the audit finding that most candidates lose because mechanisms are null, overhead-dominated, or redundant vs strong classical controls. They implement G05–G14 for the next round only.

## Shared decision rules (G05–G14)

| Item | Freeze |
|---|---|
| Independent unit | Physical/stream/family seed — never timestep or within-seed example |
| Failures | Required incomplete cells → primary aggregate **INCOMPLETE** (no survivor-only means) |
| Cost | Report wall time + declared proxy; primary estimand must charge verification/routing/meta-train where that killed the prior study |
| Margin | Descriptive paired-seed bootstrap only unless a predeclared practical margin is stated below |
| Stopping | Profile first; full wall ceilings per study; preserve all receipts |
| Outcome labels | `SUPPORTED` / `ADEQUATELY_TESTED_NEGATIVE` / `INCONCLUSIVE` / `ARCHIVED` |

## Study A — WFT prior misspecification (`wft-misspec-v1`)

**Question:** Do soft symmetry+resolution constraints help when the teacher **violates** the equitable/reflection priors?

| Field | Value |
|---|---|
| Estimand | Mean frozen transfer error on groups 32/64 (cycle+path, both levels), paired within seed |
| Direction | Lower error better |
| Practical margin | None declared — report stratum-wise paired Δ vs unconstrained |
| Strata (IV) | `compatible` (baseline teacher), `sine_perturbed` (nonzero sine modes), `unequal_degree` (independent fine≠coarse teacher fields) |
| Methods | unconstrained, both, wrong_symmetry, fixed_geometry, oracle |
| Seeds | 2203, 2213, 2221, 2237, 2243 (five; profile uses 2203 only) |
| Train | groups=16 cycle; samples∈{4,16}; noise∈{0,0.1} — **pilot profile:** samples=4, noise=0.1 only |
| Failure policy | Retain all cells; incomplete stratum invalidates that stratum mean |
| Decision | `SUPPORTED` only if both-constraints beats unconstrained on **compatible** and remains useful (CI for Δ excludes 0 favoring constraints) on at least one misspec stratum; else precise negative/inconclusive per stratum |

Script: `scripts/closure/wft_misspec_study.py`  
Output: `campaigns/wft-misspec-v1/`

## Study B — QAPEN ridge-hard streams (`qapen-ridgehard-v1`)

**Question:** Does lifecycle+memory beat rolling ridge when the stream is **nonlinear** and delayed cues are long?

| Field | Value |
|---|---|
| Estimand | Mean prequential Gaussian NLL (same scoring as v1) over required 320-step streams |
| Direction | Lower better |
| Schedules | `nonlinear_switch`, `long_delayed_cue` (cue 12 steps ahead) |
| Noise | 0.1 and 0.6 |
| Seeds | 1009, 1103, 1201, 1301 (four for pilot) |
| Methods | lifecycle_memory, single_memory, recent_memory, rolling_ridge |
| Decision | `SUPPORTED` if lifecycle_memory − ridge Δ CI entirely negative (favor lifecycle); else `ADEQUATELY_TESTED_NEGATIVE` / `INCONCLUSIVE` |

Script: `scripts/closure/qapen_ridgehard_study.py`  
Output: `campaigns/qapen-ridgehard-v1/`

## Study C — WFIM null-branch archive (documentation)

**Disposition:** `ARCHIVED` for per-letter multiplicative product-expressivity.  
Identity coordinates remain the reference algebra. Any future coordinate claim requires non-absorbable decoder constraints and exact used-byte matching (WF04) under a **new** protocol — not a silent reopen of the cancelled product.

## Deferred (protocol stubs only this round)

- **CWLNN route-before-coarse + hierarchy-necessary targets** — needs source freeze before campaign; see `docs/closure/CWLNN_PROTOCOL.md` successor note in CURRENT_WORK.
- **QLearn full-cost / new optimizee families** — separate resource plan.
- **WCODE scrubbed families + deeper compositions** — separate enumerator freeze.
- **Ultron independent families + external evaluator** — UL07 still external.

## Non-goals

- Do not weaken failure denominators.
- Do not claim independent replication from these same-host runs.
- Do not replace historical primary tables with successor outcomes.
