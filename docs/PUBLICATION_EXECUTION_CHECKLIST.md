# Publication execution checklist

Date: 2026-09-24. Status: INCONCLUSIVE / NOT SUBMISSION READY.

This is the execution order for the user's request for rigorous benchmarks, experiments, ablations, a fully written paper, and concrete implementation. It supplements, and does not replace or shrink, the 145 requirements in `results/requirement_map.json`. Current ledger: 33 scoped resolutions, 112 open. A completed negative or archive disposition is not a submission-ready method paper. No benchmark is “perfect”; rigor requires declared scope, discriminating controls, uncertainty, and reproducibility.

## 1. Paper scope and claims — G03–G04, Z10–Z11

- [ ] Write a contribution decision for every module: distinct method paper, combined paper, negative-results study, supporting library, or archive. Justify with original proposal and observed evidence.
- [ ] Resolve WCODE/Ultron shared tasks and duplicated claims before choosing paper boundaries.
- [ ] Read and compare the closest primary papers and official implementations; record known results, exact proposed differences, licensing, data overlap, and falsifying experiments.
- [ ] Create a claim-to-evidence index linking every abstract/conclusion claim to a table, raw artifact, frozen source and qualified scope.

## 2. Freeze each new study before evaluation — G05–G14

- [ ] Declare target population, independent sampling unit, primary estimand, endpoint, direction, meaningful effect margin and finite decision rule.
- [ ] Determine sample size from development variance and the desired confidence-interval width at the actual independent unit; training seeds cannot substitute for new families.
- [ ] Freeze train/selection/evaluation families, data identities, canonical equivalence/overlap checks, seeds and every factorial cell.
- [ ] Qualify comparator versions, tuning budget, information access, parameter/storage budgets and oracle privileges.
- [ ] Freeze failure, divergence, missing-cell, stopping and multiplicity policies; preserve all attempts.
- [ ] Measure resource projections, enforce allocation limits, and freeze code/config/environment/data/protocol hashes.
- [ ] Separate exploratory development, internal frozen evaluation and independently authorized confirmation. Current confirmation remains DRAFT_NOT_AUTHORIZED.

## 3. Implement and execute the discriminating experiments

| Module | Required benchmark coverage | Required controls / ablations | Remaining concrete work |
|---|---|---|---|
| QLearn | New optimizee families, datasets, widths and long horizons | Tuned SGD/momentum/AdamW, qualified official learned optimizer; gate, recurrent state/reset, feedforward, initialization-only, budget | Full-cost objective, held-family study, stability/failure accounting; preserve current negative step-AUC |
| QAPEN | Independent shift schedules, no shift, rare return, long gaps, delayed cues, independent noise variation | Lifecycle × memory factorial; single memory, fixed ensemble, random/recent/replay retrieval and qualified expansion control | Audit original mechanism coverage, add missing conditions and call-matched/full-cost comparisons |
| QWIPII | Whole new puzzle families, larger finite domains, repeated-label and symmetry-breaking goals | Brute, hand quotient, ranking without pruning, learned proposals plus exact verification, oracle; invalid transforms | Train grammar ranker, bind pruning to certificates, charge complete setup/verification/search cost and replay every path |
| WCODE | Held program families, compositions, depth and list operations within original DSL scope | Token/length/random baselines, no relation, no hierarchy, no task conditioning, identical enumeration | Extend required domain coverage, full-cost endpoint and cross-use disclosure |
| WFIM | Order-sensitive held templates and lengths; appropriate negative controls | Identity/learned coordinates, identical decoder/algebra, total-byte-matched vectors and binding/bilinear controls | Implement original bounded per-word coordinate mechanism; prove contracts and condition bounds; decide downstream contribution |
| WFT | Held graph/weight distributions, transfer sizes and constraint violations | Neither/equivariance/coarsening/both factorial; invalid symmetry, fixed/oracle controls | Broaden justified distribution coverage and full-cost comparison; retain observed regressions |
| WPINN | Complete held trajectories, initial conditions, physical parameters/laws, noise/sparsity/missingness and low excitation | Qualified SINDy/weak methods, known-support inverse PINN, data-only predictor, physical-structure and smoother ablations | Add missing baselines/held parameters, identifiability/support attribution; preserve all failed rollouts. Joint training optional; PDEs deferred by original proposal |
| CWLNN | Held sizes/topologies, aligned and nonhierarchical tasks, routing fractions | Flat/unrouted/attention matched in information, depth, width and receptive field | Resolve arbitrary-tree receptive-field matching; retain negative learned-routing result |
| Ultron | New heterogeneous DSL/law/invariant families, multiple caps and sequential tasks | Best fixed, static, cheapest, random, learned; evidence/sequential-policy ablations | Implement heterogeneous evidence-aware routing, full failed-action costs and independent verifier dependency |

- [ ] For every row above, write a source-bound protocol, execute all required cells, save checkpoints/predictions/timings/failures, and independently rederive the reported metrics from raw outputs.
- [ ] Report training, tuning, preprocessing, adaptation, routing/scoring, execution, verification, peak memory and storage; show amortization assumptions explicitly.
- [ ] Compare quality at matched total work and work at matched quality when scientifically meaningful; disclose infeasible configurations and never silently drop failures.

## 4. Analysis and falsification — S01–S10

- [ ] Reconcile planned, attempted, completed, failed and excluded units with receipts.
- [ ] Report paired effect sizes and uncertainty at family/dataset level; separate within-family seeds from across-family generalization.
- [ ] Apply frozen multiplicity policy and label retrospective/sensitivity analyses separately.
- [ ] Run leakage, canonical-overlap, invalid-input, invariance, budget-exhaustion and negative-control checks.
- [ ] Plot full distributions and cost/quality curves; retain adverse subgroups and incomplete aggregates.
- [ ] Assign supported, adequately tested negative, inconclusive, or archive dispositions without changing the endpoint after seeing outcomes.

## 5. Fully written paper and supplement — M01–M12

- [ ] Write a complete evidence-grounded manuscript: title, abstract, introduction, related work, mathematical definitions, methods, experimental design, results, discussion, limitations, conclusion and references.
- [ ] Include precise algorithms, assumptions, proof domains, verifier contracts and counterexamples; do not present empirical checks as general proofs.
- [ ] Generate every table/figure from retained outputs; link every number to its script and artifact. Include all failures and scoped negative results.
- [ ] Write supplement with all protocols, hyperparameters, selection rules, baseline deviations, environment/hardware, data provenance, licenses and reproduction commands.
- [ ] Resolve authors, contributions, funding/conflicts, permissions and acknowledgments with actual owners.
- [ ] Render the manuscript and supplement; inspect equations, references, floats, figures, page layout and consistency. Remove placeholders only with real content.

## 6. Reproduction and submission gate — R01–R11, P01–P08, Z01–Z12

- [ ] Finish fresh-environment artifact audit; preserve the interrupted CWLNN attempt and use fresh output for retry.
- [ ] Run source-restored reproduction from the new final archive; verify hashes and all headline tables/figures. Same-host replay remains labeled as such.
- [ ] Obtain required external evaluator/reviewer evidence. A local agent or client interface cannot supply independence.
- [ ] Build and verify a new immutable archive containing final source, history, protocols, raw results, analyses, manuscript, figures and instructions. Preserve previous packages.
- [ ] Check current chosen venue requirements once venue is known; resolve authorship, licensing and author approval.
- [ ] Audit every one of the 145 original requirements against current evidence, then reconcile README, registry, paper and release claims.
- [ ] Record arXiv readiness and peer-review submission readiness separately. Publish only after explicit authorization and all applicable gates pass.

## Current concrete increment

Certificate-backed QWIPII search revalidates complete fixed-goal mappings, closes generator orbits and keeps replayable concrete representatives. `campaigns/qwipii-certificate-audit-v1` exhausts 48 starts across five declared domains: every returned path replays and matches brute BFS shortest length. Expansions are 306 brute versus 183 certified, but measured search time is 10.58 ms versus 176.11 ms, including certificate revalidation for certified search and excluding separately recorded proposal verification. This supports finite correctness and an overhead limitation, not a speed advantage or learned-discovery claim.

Immediate execution order: finish QWIPII learned discovery and its frozen experiment; complete WFIM original coordinate mechanism; address remaining module-specific gaps; run claim/novelty review and write the complete development manuscript alongside results; finish portable reproduction and final gate review. These dependencies do not postpone writing until a positive result appears.
