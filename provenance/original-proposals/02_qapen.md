# 02 — Q-APEN
## Working research title
Adaptive Quantized World Ensembles with Delayed-Utility Engram Memory.

Use Q-APEN as the World Series successor label, with WAPEN as an optional alias only if the project owner confirms they are the same study. Do not invent a new expansion for APEN that overrides its existing family specification. Preserve PEN as a fixed historical precursor. This project has finite execution and resource caps even when its conceptual model family is extensible.

## Prior work and lineage

VQ representations [R06], probabilistic ensembles/planning [R07] and world-model imagination [R08] are established. The private PEN reconciliation requires preserving mixed/negative memory outcomes and testing adaptive mechanisms against appropriate fixed controls. The research proposal is a jointly measured lifecycle for model capacity and explicit memories under returning regimes, not merely a larger ensemble or a new codebook.

New protocol IDs and fresh synthetic streams are mandatory. Do not tune the historical PEN experiment, change its frozen seeds, or import its outcome numbers into these results. A legacy adapter is optional and blocked until its source identity and read-only use are verified.

## Model definition

Encode observations `h_t=E(o_≤t)` and quantize through a learned codebook `z_t=argmin_j ||h_t−c_j||²`. Keep a continuous residual feature to avoid forcing all dynamics through a lossy discrete index. Pretrain/freeze the codebook for the first lifecycle experiment; joint online codebook drift can otherwise make memory keys incomparable across time.

For active expert set A_t, predict a finite mixture:

`p(y_{t+1}|h_t,a_t)=Σ_{k∈A_t} π_{k,t} N(μ_k(h_t,a_t),Σ_k(h_t,a_t))`.

Use normalized routing weights and positive variance floors. Decompose predictive variance with the total-covariance formula from MATH_FOUNDATIONS.md. Disagreement is a useful feature, not automatically calibrated epistemic uncertainty.

Engrams store a key, compressed value, originating regime/expert ID, write time, access statistics and a delayed-utility estimate. Utility is estimated from subsequent development-stream prediction changes, not only immediate salience or training reconstruction. Each intervention uses a defined ablation/replay protocol so “memory helps” is supported by outcomes, not activation counts.

## Lifecycle and causal order

Use a finite state machine: NEW → WARMUP → ACTIVE → SLEEPING → REVIVED, with separate PRUNED archives. Stable UUIDs identify experts. Spawning requires sustained pre-update surprise and a cooldown, not one noisy point. Warm a candidate using a bounded replay window and assess it on subsequent stream blocks. A newly fitted expert cannot claim success on the same label that triggered its creation.

Crucial evaluation order: predict, log predictive distribution and memory state, observe target, score, then update gates/experts/memory. Future observations and true regime labels are unavailable to the learner. Truth labels may be used only in the evaluator to diagnose shift lag and regime recurrence.

Proposed caps: at most eight active experts, 32 archived identities, 128 engrams, codebook 64, latent width 16, rollout horizon 16 and 64 rollout calls. These are starting limits. Every warmup, routing decision, retrieval, merge check and simulation counts toward cost.

## Contracts

`WorldExpert.predict(features[B,D], action[B,A]) -> mean[B,O], logvar[B,O]`.
`WorldBank.route(features) -> expert_ids[K], weights[B,K]`.
`LifecyclePolicy.observe(scored_event) -> LifecycleDecision`.
`EngramStore.write/retrieve/consolidate -> typed records`.
`StreamEvaluator.step(observation, optional_action) -> prequential receipt`.

Use `nn.ModuleDict` keyed by stable IDs; maintain optimizer groups/state when experts appear or sleep. Do not index mutable experts only by list position. Serialize dormant weights and memory references together. A bounded graph of expert similarities may support transfer later, but is disabled in the first lifecycle comparison to avoid collapsing ensemble diversity.

## Code units

| File | Main responsibility |
|---|---|
| streams.py | Switching linear systems, delayed cues and recurrent regime schedules |
| quantizer.py | Codebook fitting, commitment loss, distortion and code usage |
| expert.py | Small probabilistic predictors with variance floors |
| mixture.py | Routing, predictive moments and scoring |
| engrams.py | Fixed-capacity trace storage, retrieval, forgetting and utility receipts |
| lifecycle.py | Birth/sleep/revive policy with cooldowns and explicit cost |
| bank.py | UUID registry, optimizers and checkpoint round trips |
| baselines.py | Fixed ensembles and memory-write controls |
| evaluate.py | Prequential metrics, calibration and regime diagnostics |
| adapter.py | `predict_worlds` capability, not arbitrary external actions |

## First benchmark

Generate streams from several stable linear state-space systems with noisy observations. Insert delayed cues that help identify a later regime and repeat earlier regimes after long gaps. Vary observation noise independently of regime shifts so spawning on noise is penalized. Keep an easier no-shift negative control: adaptive growth should not be necessary there.

Compare against one probabilistic model, a fixed ensemble, a rolling/replay-only ensemble, dynamic experts without memory, fixed experts with memory, random-write engrams and an attention/recent-history replacement. Match either total measured time or total training/prediction calls as the declared primary resource. Report parameter-matched and active-compute-matched comparisons separately; they answer different questions.

Primary proposal: prequential negative log likelihood at fixed total cost. Secondary: rollout error, calibration, shift recovery delay, expert count, false spawns, memory retrieval precision and measured delayed utility. Finance is not needed for this mechanism test. Any later financial benchmark needs a separate chronological/leakage/cost protocol, not a profitable-trading claim from these synthetic streams.

## Tests

Exact mixture moments for two known Gaussians; weights sum to one; variances positive; no target accessed before prediction; no missing/duplicated optimizer state after spawn; revive preserves archived identity; codebook freeze preserves old keys; memory cap enforced before writes; cooldown prevents repeated spawning; deterministic stream replay; ablations truly disable the named feature.

Behavioral test: a controlled returning regime should produce an observable lifecycle event, even if it does not improve the primary metric. Separate this mechanism activation check from the benchmark claim. Mock lifecycle scripts belong only in unit tests, never in claimed learned results.

## Infinite-model interpretation and scope boundary

A countably infinite mixture or stick-breaking prior may be a later mathematical model, but threshold spawning is not posterior inference under that prior. Do not include an infinite sum in the paper and label a capped heuristic implementation as an exact realization. Sunday needs a truthful finite demonstration: the active expert population changes under a measured budget and its effect is compared to fixed controls. Merge policies, graph knowledge transfer and nonparametric inference are later hypotheses.


---
