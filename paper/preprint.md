---
title: "Mechanism Verification and Negative Findings in a Structured Learning Workbench"
author: "Ryan"
date: "26 September 2026"
---

# Abstract

We study whether implemented structure produces measurable benefits after accounting for verification, strong controls, and failure cases. Nine related software modules cover optimization, adaptive memory, symmetry-guided search, program synthesis, word-algebra coordinates, constrained graph operators, weak dynamical discovery, conditional graph computation, and tool routing. Their scientific questions remain separate. We combine mechanism checks with bounded development experiments and retain failed runs. Several apparent advantages disappear under stronger controls: the learned optimizer has worse loss-area performance than tuned fixed optimizers; expert lifecycle does not outperform a simple stream predictor; learned symmetry proposals reduce expansions but increase elapsed time; and conditional graph routing is slower and less accurate than full refinement. A graph-operator constraint study exhibits a scoped error reduction, with adverse conditions retained. These results identify concrete mechanisms, computational tradeoffs, and unfinished tests rather than establish a universal architecture. The evidence is internally audited and includes exact same-host replays, but is not independently confirmed.

# 1. Introduction

A working implementation and a favorable benchmark number answer different questions. Structured algorithms may satisfy algebraic contracts yet add computational overhead, preserve valid paths without reducing search, or exploit a task construction that favors a particular representation. We investigate these distinctions in a shared research workbench.

**Contribution and inclusion rule.** This retrospective report includes exactly the nine namespaces already present in the workbench (`qlearn`, `qapen`, `qwipii`, `wcode`, `wfim`, `wft`, `wpinn`, `cwlnn`, `ultron`), with the named campaigns, protocols and failures enumerated in the claim index and closure registry. Inclusion is historical presence in the shared repository through the finite-closure source identity, not a random or representative sample of structured-learning methods. Successor sensitivity studies that reuse already-exposed tasks remain development evidence and do not replace primary tables. We do not pool incomparable endpoints or count random seeds as new datasets. Each module has its own model, domain, controls and limitations. The present contribution is a source-bound computational case study of mechanism verification and negative or inconclusive findings under disclosed information access, evaluation rules and measured work. It does not claim methodological novelty for the nine original proposals, population inference over structured learning as a class, independent replication, or completion of the full proposed architectures.

Controls are not uniformly information- or cost-matched: physical priors and external pretraining differ in the cases identified below. The central methodological question is whether a claimed mechanism survives comparisons that disclose those mismatches.

# Related work and positioning

We locate each module against established primary literature. The overlaps below attribute prior art; they do not establish novelty of the present implementations.

**Learned optimization (QLearn / MALIS).** Learning update rules from optimization trajectories is established (Andrychowicz et al., 2016). Surveys and benchmarks organize model-free and model-based learning-to-optimize (Chen et al., 2022). Practical learned optimizers raise generalization and training-cost issues (Moudgil et al., 2026). QLearn evaluates a particular bounded recurrent controller with progress/budget features against tuned SGD, momentum, AdamW, ablations and an official pretrained Celo2 comparator. It is not a claim to invent learned optimization. Discrete MALIS actions are a separate prototype.

**Adaptive experts and memory (QAPEN).** Mixtures of experts partition tasks via learned gating (Jacobs et al., 1991). QAPEN instantiates a finite linear-Gaussian lifecycle with delayed-utility memory, frozen quantization and prospective admission. Closest work is modular experts and adaptive memory, not a full latent world model. Comparisons emphasize retrieval and rolling ridge, not parameter-matched neural planners.

**Symmetry and quotient search (QWIPII).** Group actions and certificates for state-space reduction are classical in combinatorial search; equitable partitions and quotient graphs organize coarsening (Schaub et al., 2016). QWIPII restricts pruning to exhaustively verified fixed-goal automorphisms on finite token rings and separately tests learned proposal ranking. Ranking is not treated as a correctness certificate.

**Program synthesis ranking (WCODE).** Neural/symbolic synthesis systems such as DreamCoder jointly learn libraries and search policies (Ellis et al., 2021). WCODE instead ranks a fixed finite DSL with trained structural scorers under explicit candidate caps and a finite-domain verifier. Historical semantic overlap with earlier routing studies is disclosed; the study does not claim unrestricted coding or compiler optimization.

**Word-algebra coordinates (WFIM).** Diagonal reparameterizations and binding-style products are standard algebraic devices. The present contribution is the finite identity that multiplicative per-letter transport cancels exactly under concatenation, plus a downstream learning comparison against identity coordinates and simple encoders. No new free algebra is claimed.

**Constrained graph operators (WFT).** Equitable coarsening links fine and coarse diffusion generators when degrees and masses match (Schaub et al., 2016). WFT learns positive Laplacians with reflection and cross-resolution soft constraints on a generator deliberately compatible with those priors, then freezes weights for size/topology transfer. Closest work is constrained operator learning and graph reduction; the positive result is scoped to that generator.

**Weak dynamical discovery (WPINN).** Sparse identification of nonlinear dynamics (Brunton et al., 2016) and weak-form SINDy (Messenger and Bortz, 2020) are the parent methods. Official PySINDy provides package controls. WPINN adds observation-field smoothing and structured sparsity on oscillators; joint physics-trained PINNs and PDEs are out of first-stage scope.

**Conditional graph computation (CWLNN).** Early-exit and conditional computation reduce inference cost when confident samples skip layers (Teerapittayanon et al., 2016). CWLNN tests hard pre-refinement routing on small graphs with matched-reach flat and full-hierarchy controls. The measured result is a local negative: half routing is slower and less accurate than full hierarchy under the declared latency ceiling.

**Tool routing (Ultron).** Routing among tools under shared caps relates to mixture-of-experts scheduling and agent tool use, but the study uses a finite DSL tool set with family-disjoint train/eval splits. It does not establish general research-agent capability or sealed external evaluation.

These citations establish background and attribution for all nine modules. Exact-combination novelty versus every related system is not claimed.

# 2. Experimental organization

All studies use bounded local CPU reference paths. Configurations, source identities, raw outputs and failures are retained in immutable campaign directories. Selection data choose hyperparameters or checkpoints; held observations are used for reporting. Tasks inspected during development are not subsequently described as secret holdouts. Most studies use eight seeds, but the independent population unit remains the dataset or generator family. Seed-level variability does not establish broad generalization.

We distinguish exact finite-domain contracts, numerical regression checks, development comparisons, and independent replication. Algebraic identities refer to the stated mathematical objects under exact real arithmetic on the declared supports; floating-point implementations use documented tolerances and do not provide library-wide exact arithmetic. Seed-paired bootstrap intervals are exploratory and conditional on the fixed tasks; most comparisons are unadjusted and there is no collection-wide significance test. A certificate establishes only its explicit domain and assumptions. A successful program exit does not establish the scientific hypothesis. Failed required cells remain in denominators or make an aggregate unavailable; survivor-only means are not substituted. Exploratory interventions on a failed model are labeled retrospective rather than treated as new primary outcomes.

## 2.1 Study inventory and primary estimands

| Module | Primary protocol / campaign | Aggregation unit | Primary descriptive endpoint | Failures policy |
|---|---|---|---|---|
| qlearn | natural-digits-v1 (+ sensitivity follow-ups) | seed means over digit-pair tasks | 32-step normalized query-loss AUC; lower better | incomplete required trajectories invalidate that aggregate |
| qapen | qapen-lifecycle-v1 | seed means over stream conditions | prequential Gaussian NLL (moment-matched) | exhausted compute caps → incomplete |
| qwipii | qwipii-learned-development-v1 | seed/start cells within fixed goals | expansions and wall time vs random order; path validity | retain invalid/longer greedy paths |
| wcode | wcode-trained-v1 | semantic family after seed pooling | verified completion at candidate cap 24 | exhausted caps and false public fits are failures |
| wfim | wfim-coordinate-development-v1 | training seed on fixed tasks | held-template and held-length MSE | all required cells retained |
| wft | wft-constraints-v1 | physical-instance seed | mean normalized prediction error on held sizes 32/64 | report adverse cells; gap-sensitive spectral tolerance |
| wpinn | wpinn-structured-v1 | seed after averaging law/condition cells | held-IC rollout MSE among successful integrations + failure counts | null primary mean if method has failures |
| cwlnn | cwlnn-conditional-v1 | seed/task | MSE at 3 ms/graph ceiling; primary route fraction 0.5 | infeasible if ceiling miss rate exceeds policy |
| ultron | development-v2 routing cells | semantic family | verified completion vs best fixed tool | bootstrap interval may span zero |

Full equations, grids, seeds and stopping rules live in the per-study protocols under `docs/closure/` and `docs/execution/development-v2/`. Headline reconstruction commands are listed in `docs/HEADLINE_REPRODUCTION.md`.

# 3. Mechanisms

## 3.1 Learned optimization and adaptive memory

QLearn produces bounded context-dependent updates and compares them with tuned SGD, momentum, AdamW, architecture ablations and the official pretrained Celo2 implementation. Its natural-data study uses binary digit-pair tasks, with distinct pairs for controller training, selection and held adaptation. The one dataset and unmatched external pretraining limit the interpretation. MALIS separately implements discrete action selection and rollback; its results are not evidence for the continuous controller.

QAPEN combines frozen learned quantization, continuous residuals, persistent expert identities, prospective activation, bounded replay, and delayed memory utility. Predictions precede observations. Checkpoint tests restore expert and optimizer state and reproduce continuation predictions. Single-expert memory and rolling predictors isolate whether retrieval or lifecycle management supplies any benefit.

## 3.2 Verified search and program synthesis

QWIPII searches finite token rings with rotations and adjacent swaps. A proposed map is eligible for fixed-goal pruning only after exhaustive verification of a complete multiset domain, bijectivity, preservation of the goal and every unit-cost transition. A map that transforms both board and goal can establish equivalence between problems without preserving the goal of a single search. Empty or incomplete samples cannot establish a certificate.

Serialized mappings are revalidated before use. Generator orbits are closed and search stores concrete representatives, so returned actions replay in the original coordinates. A trained ridge ranker predicts single-generator orbit reduction from public goal and sampled action features. Ranking does not authorize pruning; rejected proposals consume the verification budget. A separate greedy state ranker never merges approximate equivalence classes and does not guarantee shortest paths.

WCODE ranks a finite, typed program grammar using trained structural, token and task-conditioned controls. Candidate enumeration and available examples are held fixed. The benchmark measures verified completion in a finite DSL, not general software engineering. Shared semantic functions with earlier routing studies are explicitly disclosed.

## 3.3 Algebra, graph operators and physical discovery

WFIM uses word concatenation with degree truncation. Positive diagonal coordinates transport multiplication by applying the coordinate map, multiplying, and applying its inverse. Multiplicative per-letter scales cancel exactly; independent bounded per-word scales need not. Both products remain isomorphic to concatenation. An unrestricted decoder may absorb fixed diagonal feature reweighting, so downstream benefit must be established under stated optimization, regularization and storage constraints. A downstream coordinate study compares this mechanism to the identical fixed algebra and to vector, bilinear and binding controls.

WFT fits independent fine and coarse graph fields with equivariance and coarsening constraints. The actual teacher applies softplus to a constant-plus-cosine preactivation, not an exponential log-weight field; the older protocol wording is corrected here without changing its frozen data. The experiment uses explicitly verified equitable coarsening and distinguishes valid reflection constraints from deliberately invalid shifts. WPINN fits an observation-only neural field or spline and then performs sparse weak-form identification, with physical-structure constraints and derivative/weak baselines. Sequential fitting is part of the original first scope; joint physics training is optional and PDE extensions are deferred.

CWLNN selects nodes before expensive refinement. Router, local, coarse and refinement computations are measured rather than masking already computed outputs. Full refinement, flat networks and dense attention provide controls. Ultron routes among bounded capabilities and verifies outputs; the existing DSL results do not establish heterogeneous scientific orchestration or independent verification.

# 4. Results

## 4.1 Optimization and memory

At 32 adaptation steps, mean normalized loss area is 13.2809 for the full learned controller, 11.9562 for SGD, 7.9893 for momentum, 6.4145 for AdamW and 7.7454 for official pretrained Celo2; lower is better. These data do not support optimizer superiority. Wider tuning and longer meta-training retain failures and divergence instead of supplying complete favorable aggregates. Same-host replay of 400 original meta-training trials matches saved states and failure status.

The causal memory study contains 512 stream-method cells and 163,840 predictions. Mean negative log likelihood is 0.61727 for the candidate, 0.61225 for single-expert memory and 0.55893 for rolling ridge. Mechanism activation and checkpoint recovery therefore do not establish incremental lifecycle benefit. Broader delayed-cue, noise and cost-matched requirements remain open.

## 4.2 Search and synthesis

The learned QWIPII study uses five training goals of size three or four, three selection goals of size five, and four held goal patterns of size six. Eight seeds and four starts per held goal produce 128 cells per method and 896 total paths. All paths replay. Learned ordering averages 21.3047 expansions and 16.9859 ms per query, compared with 23.9453 expansions and 9.0092 ms for random ordering. Brute search averages 25.1719 expansions and 1.2703 ms. Query times include discovery and verification where used; training and selection costs are saved separately.

All non-greedy methods match brute shortest-path lengths. Greedy ranking returns longer paths in 16 of 128 cases. Removing the goal feature increases learned-search expansions; removing the sampled transition feature leaves the reported average unchanged. These are descriptive results within four fixed ring patterns, not new puzzle families. One timing observation per cell does not establish a hardware-general efficiency claim.

WCODE evaluates 331 canonical finite functions with 28,416 audited searches. Relational scoring at candidate cap 24 completes 10.54 percent of held-family cases, compared with 9.80 percent for token scoring. Held-composition completion is zero. Fifteen functions overlap older WCODE/Ultron data, including four current evaluation families. The evidence does not establish robust structural-ranking superiority.

## 4.3 Graphs and dynamics

WFT contains 160 learned fits, 64 fixed or oracle controls and 2,688 evaluation rows, of which 1,792 are transfer rows at previously unseen group counts 32 and 64. Both constraints yield mean error 0.000303878 versus 0.000928561 without either constraint within the declared generator. Across all evaluation sizes, both constraints are worse in 12 of 48 conditions; that denominator includes the training graph size and is not a transfer-only count. This is a bounded benefit, not a claim over arbitrary graph distributions. Numerical verification at nearly repeated spectral boundaries requires a disclosed gap-sensitive tolerance.

WPINN contains 120 condition cells, twelve methods, 240 learned observation fields and 6,720 replayed rollouts. Primary aggregates remain incomplete when required integrations fail: unconstrained neural weak fitting has 21 failed cells and the passive variant has three. Alternative stiff solvers complete four passive held trajectories but retain substantial prediction error. All 17 original failed polynomial rollouts remain preserved. Retrospective support interventions do not prove an exclusive failure cause.

CWLNN trains 128 models and reports 23,040 held predictions and 115,200 timing repeats. At half routing, learned routing has mean squared error 0.011939 versus 0.011412 for full hierarchy on the aligned task, and 0.032721 versus 0.029831 on diffusion. It is slower in both comparisons. Flat depth-five processing is strongest on the diffusion condition. Permutation audits agree to approximately 4.45e-16, supporting implementation consistency rather than routing benefit.

## 4.4 Learned word-algebra coordinates

The WFIM study trains 80 models across eight seeds, two fixed tasks and five encoders. All 40,640 saved predictions replay exactly after checkpoint reload. On ordered-pattern frequency, learned coordinates have held-template MSE 0.036352 versus 0.035816 for identity coordinates, and held-length MSE 0.009514 versus 0.006033. Mean training time is 9.75 versus 3.19 seconds. Thus the learned coordinates do not improve the primary task over the identical algebra. The order-insensitive count control is mixed. Encoders share a one-MiB payload cap and the same decoder/output dimensions, but use unequal bytes; this is not an exactly byte-matched capacity comparison.

![WFIM ordered-pattern prediction. Each line pairs one training seed on the same fixed finite task; lower MSE is better. Eight seeds do not represent eight independent task families.](figures/wfim-paired-seeds.png){width=95%}

# 5. Discussion

Three recurring distinctions organize the observations; the experiments do not identify an exclusive causal explanation for every outcome. First, algebraic validity does not imply useful parameterization: per-letter transport cancels, and per-word transport remains an isomorphism. Second, less nominal work does not imply less elapsed work: exact proposal verification can dominate saved search expansions, and conditional routing can cost more than full refinement. Third, a mechanism-specific improvement does not establish the full architecture: retrieval can help while expert lifecycle loses to a simpler control.

These observations motivate finite branch decisions. The implemented per-letter product-expressivity claim is unsupported. Learned routing benefit is unsupported in the measured graph study. Learned proposal runtime benefit is unsupported in the ring study. The constrained graph-field result remains a scoped empirical benefit requiring broader comparisons. None of these dispositions is converted into independent confirmation.

# 6. Limitations

The evidence includes small synthetic distributions, a single natural digit dataset, repeated seeds within fixed families, incomplete failure-affected aggregates and several unmatched total-cost components. Current finite rings do not cover whole new puzzle families. WFIM requires stronger byte-matched controls. Full selection replay now reconstructs all 80 models, 12,000 updates and 240 candidate checkpoint scores exactly; this closes replay bookkeeping, not the capacity-matching requirement. WPINN still needs held physical parameter regimes and inverse-PINN/data-only comparators. CWLNN arbitrary-tree receptive-field matching remains unresolved. Heterogeneous Ultron capability evaluation and independent external verification remain unfinished. These gaps prevent a submission-ready verdict for the full proposal collection, while remaining compatible with a bounded negative-results preprint.

# 7. Reproducibility

The repository retains campaign protocols, source hashes, selected checkpoints, predictions, failures and analysis receipts when the review archive is restored. A source-only Git clone omits ignored raw campaigns; obtain the hashed delivery archive described in `docs/RELEASE_REPRODUCIBILITY.md`. Fresh-environment checks cover installation, tests and selected artifact audits. Isolated-source CWLNN and WFIM prediction/training replays match saved receipts on the recorded hosts. Same-host exact replays are useful diagnostics but do not establish independent reproduction. Per-headline commands and expected artifact digests are listed in `docs/HEADLINE_REPRODUCTION.md`.

Software is released under Apache-2.0 (`LICENSE`, `NOTICE`). UCI digits remain CC BY 4.0. Celo2 source and weights are external and not redistributed.

# 8. Conclusion

The workbench establishes several functioning mechanisms and documents where their claimed advantages fail under stronger controls or explicit cost accounting. Its present results justify scoped negative findings and further discriminating experiments. They do not establish a unified superior model, nine novel methods, or conference readiness. The bounded contribution is the verified case study itself, with the limits above preserved.

# AI Use Statement

Automated assistants (including Codex and Cursor agents) were used extensively for implementation, experiment design, synthetic-data generators, mathematical analysis, testing, execution, result interpretation, literature search and manuscript drafting. Automated checks and same-host replay are described in the evidence record. The named author retains responsibility for the published claims and for approving release under Apache-2.0. A dated human attestation is recorded in `docs/AUTHORSHIP.md` (Ryan, 26 September 2026).

# Evidence index

Protocols and result reports: `docs/closure/` and `docs/execution/development-v2/`. Claim index: `results/claim_index.json`. Headline reconstruction: `docs/HEADLINE_REPRODUCTION.md`. Reproduction entry: `docs/RELEASE_REPRODUCIBILITY.md`. Collection registry (sibling records repo): `RESEARCH_CLOSURE/REGISTRY.json`.

# References

Andrychowicz, M., Denil, M., Gomez, S., Hoffman, M. W., Pfau, D., Schaul, T., Shillingford, B., and de Freitas, N. (2016). Learning to learn by gradient descent by gradient descent. https://arxiv.org/abs/1606.04474.

Brunton, S. L., Proctor, J. L., and Kutz, J. N. (2016). Discovering governing equations from data by sparse identification of nonlinear dynamical systems. Proceedings of the National Academy of Sciences. https://doi.org/10.1073/pnas.1517384113.

Chen, T., Chen, X., Chen, W., Heaton, H., Liu, J., Wang, Z., and Yin, W. (2022). Learning to Optimize: A Primer and A Benchmark. Journal of Machine Learning Research, 23(189). https://jmlr.org/papers/v23/21-0308.html.

Ellis, K., Wong, L., Nye, M., Sablé-Meyer, M., Morales, L., Hewitt, L., Cary, L., Solar-Lezama, A., and Tenenbaum, J. B. (2021). DreamCoder: Bootstrapping inductive program synthesis with wake-sleep library learning. Proceedings of PLDI. https://arxiv.org/abs/2006.08381.

Jacobs, R. A., Jordan, M. I., Nowlan, S. J., and Hinton, G. E. (1991). Adaptive mixtures of local experts. Neural Computation, 3(1), 79–87. https://doi.org/10.1162/neco.1991.3.1.79.

Messenger, D. A., and Bortz, D. M. (2020). Weak SINDy: Galerkin-Based Data-Driven Model Selection. https://arxiv.org/abs/2005.04339.

Moudgil, A., Knyazev, B., and Belilovsky, E. (2026). Celo2: Towards Learned Optimization Free Lunch. https://arxiv.org/abs/2602.19142.

Schaub, M. T., O’Clery, N., Billeh, Y. N., Delvenne, J.-C., Lambiotte, R., and Barahona, M. (2016). Graph partitions and cluster synchronization in networks of oscillators. Chaos, 26(9), 094821. https://doi.org/10.1063/1.4961065.

Teerapittayanon, S., McDanel, B., and Kung, H. T. (2016). BranchyNet: Fast inference via early exiting from deep neural networks. https://arxiv.org/abs/1709.01686.
