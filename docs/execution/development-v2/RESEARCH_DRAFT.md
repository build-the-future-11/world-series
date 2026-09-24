# Mechanism checks and negative findings in a bounded research workbench

Working development manuscript, 24 September 2026. Not submitted, independently
replicated, or certified as novel. Numerical tables are generated in RESULTS.md;
this narrative must be read with the complete cells and failure denominators.

## Abstract

We evaluate nine bounded research mechanisms in a shared local workbench. Before
expanding evaluation, we repair defects involving coordinate-preserving search,
uncharged synthesis scoring, operator-target mismatch, and unsupported algebraic
counterexample reporting. Eight non-optimizer modules receive eight-seed
development studies. A learned optimizer receives a natural handwritten-digit
study with 288 tuning trials and 432 evaluation trajectories, alongside 48
trajectories from the official pretrained Celo2 implementation. A separate
discrete action prototype exercises optimizer selection, replay, loss selection
and full-state rollback. All 80 main run receipts pass artifact contract checks;
17 failed polynomial rollouts remain visible. The learned optimizer does not
establish superiority over tuned fixed optimizers. Other mechanisms show scoped
tradeoffs rather than a common positive result. These findings support further
mechanism isolation and independent evaluation, not full-architecture or general
intelligence claims.

## Research questions and implementation scope

The workbench separates algorithm execution from scientific support. The
optimizer asks whether bounded, context-dependent updates improve adaptation.
The stream model asks whether past-context retrieval helps returning regimes.
The search module asks whether verified equivalence reduces search while
preserving valid paths. The remaining modules test structural synthesis ordering,
finite algebra operations, constrained graph operators, weak-form oscillator
identification, sparse multiscale features and restricted tool selection.

These are distinct questions with distinct estimands. We do not aggregate their
metrics into a single score or treat one mechanism's success as evidence for
another. The implementation does not instantiate every part of the original
World Series blueprint. In particular, fixed structural encoders are not learned
universal models, and a finite solver router is not a general research agent.

## Methods

The full protocol, seeds, parameter settings, controls and interpretation limits
are in PROTOCOL.md. The natural optimizees are width-24 tanh networks on binary
digit-pair tasks from the UCI Optical Recognition of Handwritten Digits dataset
by Alpaydin and Kaynak (1998), DOI 10.24432/C50P49, licensed CC BY 4.0. Original
training and test writers are separated. Digit pairs 0/1 and 2/3 train the
controller, 4/5 selects trials, and 6/7 and 8/9 evaluate it. Eight seed units
share this one underlying dataset; they are not eight independent datasets.

All internal methods receive four tuning trials. The full policy is compared
with SGD, momentum, AdamW, a feedforward policy, no-budget and no-gate variants,
an identical-parameter GRU whose state resets each step, and an initialization-only
exact meta-learning control. The latter is a MAML-style internal control with
fixed inner SGD, not a faithful reproduction of a published benchmark. Support
gradients drive updates. Query labels evaluate outer objectives during training
and score held adaptation trajectories, but do not select held actions or stop
held adaptation.

Celo2 uses the official source and released pretrained weights, with the matrix
update and AdamW bias branch described by its authors. The commit, file hashes,
checkpoint revision and dependency versions are recorded separately. It receives
the same four-rate local selection budget; its prior meta-training compute is
not matched. Potential overlap between external pretraining and NIST-derived
digit sources has not been ruled out; this is not certified as an unseen-data
test of Celo2. The PyTorch/JAX bridge is compatibility-tested. Wall times include
implementation overhead, compilation and host contention, so these data do not
establish equal-wall-time superiority.

The paired diagnostic first averages task differences within each seed. Exact
sign-flip tests require sign symmetry under the null. Secondary comparisons use
Holm adjustment. These development diagnostics are not externally preregistered;
nonsignificance cannot establish equivalence.

## Results

At 32 adaptation steps, mean normalized loss AUC is 13.2809 for the full
controller, 11.9562 for SGD, 7.9893 for momentum, 6.4145 for AdamW and 7.7454 for
official pretrained Celo2. Lower is better. The full policy's endpoint accuracy
is approximately 97.01%, compared with 97.53% for AdamW, 98.57% for momentum and
98.05% for Celo2. The full policy outperforms the reset-state variant descriptively
on AUC in all eight seeds, but that isolated observation does not overturn the
stronger-baseline result or establish a multiplicity-adjusted general benefit.
Every horizon and comparator appears in the generated tables.

A separately declared sensitivity study widens selection from four to six
trials and increases meta-training from four to twelve outer steps on the same
development tasks. All eight runs and 432 evaluation trajectories are recorded,
including 16 failed tuning trials and four diverged evaluation trajectories.
Two full-policy trajectories diverge, as do one no-budget and one reset-state
trajectory. Their complete required-cell aggregates are therefore absent.
AdamW and momentum retain their original selections and mean AUCs. This
follow-up exposes selection/horizon instability; it supplies no optimizer win.
SENSITIVITY.md preserves every method and remaining grid-edge selection. Since
both search range and training duration changed, their effects are not isolated.

The causal context-memory stream intervention lowers mean NLL relative to its
otherwise similar no-memory control in the declared returning-regime stream.
However, the one-expert memory control has a lower overall mean than the
multi-expert candidate, and the fixed ensemble has a lower rare-regime mean.
This is a useful decomposition of tradeoffs, not proof of the full Q-APEN
lifecycle architecture. The legacy model's write-only memory cannot substantiate
a memory-use claim.

Coordinate-preserving QWIPII search returns replayable paths in exhaustive
small-permutation tests. On the six-token/120-expansion development condition,
brute and quotient search both solve approximately 10.42% of sampled instances,
while the disclosed Hamming-ranking heuristic solves all sampled instances.
This is evidence against claiming quotient savings for that fixed-goal setup;
it is not a general search-complexity result.

The finite-DSL tool-routing study is now discriminating. At 24 candidate
evaluations, learned selection completes approximately 81.94% of held tasks,
measured-cheapest 66.67%, random 58.33% and static 44.44%. These are descriptive
results over a small, public grammar. Training and evaluation use disjoint
semantic program families; the router remains a nearest-neighbor prototype.

The other modules retain full method/condition tables. WCODE's hierarchical,
flat and token structural heuristics tie in the 24-candidate condition; there is
no evidence there for a uniquely hierarchical benefit. WFT's correct true-graph
oracle has zero error by construction and is labeled as such. Finite WFIM
truncation and transport agree numerically with their references, while top-k
can lose the required algebraic property. CWLNN's unrouted hierarchy performs
better than its aggressively routed variant on the declared residual-propagation task.
WPINN has 17 failed rollouts; affected required-cell means are absent rather
than computed from survivors.

## Reproducibility and limitations

Source commits, immutable run directories, per-file hashes, dataset rows,
raw trajectories, tuning failures, seed-level tables and replay receipts form
the evidence trail. A successful run is not a supported hypothesis. Same-host
training or evaluation replay is not independent replication. The independent
evaluation handoff specifies what an outside reviewer must freeze and return.
All 400 original learned-policy meta-training trials have now been replayed from
the archived source and stored task arrays: policy and optimizer state, counters,
histories and failure status match exactly. META_TRAINING_REPLAY.json records
this same-host check, separately from the natural-data development studies.

This study is limited by small public task distributions, eight seed units,
unmatched external pretraining, unrandomized method timing, narrow neural
architectures, linear oscillator families and finite graph/DSL domains. The
source-visible development tasks cannot subsequently be called a secret holdout.
We make no novelty, broad transfer, full-architecture completion or publication-
readiness claim. Negative and inconclusive results are retained as outcomes.

## Primary references and evidence

- Alpaydin, E. and Kaynak, C. Optical Recognition of Handwritten Digits (1998).
  https://doi.org/10.24432/C50P49
- Andrychowicz et al. Learning to learn by gradient descent by gradient descent
  (2016). https://arxiv.org/abs/1606.04474
- Moudgil, Knyazev and Belilovsky. Celo2: Towards Learned Optimization Free Lunch
  (2026). https://arxiv.org/abs/2602.19142
- Official Celo2 implementation: https://github.com/amoudgl/celo2
- Local executable evidence: PROTOCOL.md, RESULTS.md, AUDIT_RECEIPT.json,
  analysis.json and the CSVs in this directory. Historical constructed-neural
  results remain in ../QLEARN_NEURAL_DEVELOPMENT_V1_RESULTS.md.
