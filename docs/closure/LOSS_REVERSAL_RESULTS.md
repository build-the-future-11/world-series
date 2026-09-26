# Loss-reversal successor results — 26 September 2026

Historical primaries unchanged. New campaigns: `campaigns/wft-misspec-v1/` (local),
`campaigns/qapen-ridgehard-v1/` (local). Machine summary:
`LOSS_REVERSAL_RESULTS.json`.

## WFT misspecification (`wft-misspec-v1`)

300 complete cells (5 seeds × 3 strata × 2 sample counts × 2 noises × 5 methods).
Seed-level paired Δ = mean(both − unconstrained) over samples/noise within seed.

| Stratum | Δ (both − unconstrained) | 95% seed bootstrap CI | Label |
|---|---:|---|---|
| compatible | **−6.87e-4** | [−8.36e-4, −4.68e-4] | **CONSTRAINTS_HELP** |
| sine_perturbed | **+8.46e-4** | [+2.94e-4, +1.43e-3] | **CONSTRAINTS_HURT** |
| unequal_degree | −4.26e-4 | [−9.55e-4, +3.46e-5] | **INCONCLUSIVE** (CI spans 0) |

**Interpretation:** Soft constraints help when the teacher matches the prior
(replicates the scoped historical win). When sine modes break reflection, the
**same constraints hurt** transfer — falsifying “always add these penalties.”
Unequal fine/coarse teacher fields are inconclusive at n=5.

**Disposition:** Historical WFT positive remains **scoped**. New claim:
constraint benefit is **prior-conditional**, not unconditional.

## QAPEN ridge-hard (`qapen-ridgehard-v1`)

64 complete streams (4 seeds × 2 hard schedules × 2 noises × 4 methods).

| Method | Mean NLL (all cells) |
|---|---:|
| single_memory | **0.6497** |
| recent_memory | 0.6571 |
| rolling_ridge | 0.6680 |
| lifecycle_memory | 0.6688 |

Paired seed mean (lifecycle − ridge) = **+7.1e-4** → label **RIDGE_STILL_WINS_OR_TIE**.
On nonlinear + long-delay streams, lifecycle still does **not** beat ridge; simple
memory variants are stronger than both.

**Disposition:** Precise negative extended: lifecycle ≯ ridge even outside the
original linear-Gaussian regime (this pilot). Stronger QAPEN claims need a
different mechanism or a prospectively harder population — not retuning v1.

## WFIM

Per-letter product-expressivity **ARCHIVED** (`WFIM_ARCHIVE.md`). No new training.

## Deferred this round

CWLNN route-before-coarse / hierarchy-necessary targets; QLearn full-cost families;
WCODE scrubbed compositions; Ultron external evaluator.
