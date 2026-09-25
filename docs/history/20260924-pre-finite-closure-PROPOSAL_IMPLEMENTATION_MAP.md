# Original proposal to implementation and evidence

Scope audit at c893c19 plus the packaging reconciliation. Original proposal files
are preserved byte-for-byte in provenance/original-proposals/ and indexed by
provenance/IMPORT_MANIFEST.json. File names in this table are implementation
locations, not claims that mere file existence proves a mechanism. Evidence is
limited to the named discriminating tests/studies. A shared technical draft is
not nine completed papers.

| Project / original mechanism | Implementation | Discriminating evidence | Remaining original-scope gap |
|---|---|---|---|
| QLearn bounded positive gates, layer steps, recurrent budget/progress features | qlearn/policy.py, features.py, unroll.py | tests/qlearn; natural-digits-v1 and development-v2 | Broader held optimizee distributions/widths/horizons and compute-normalized objective |
| Exact tiny meta-gradient, functional parameters, reset and checkpoint | qlearn/functional.py, meta_train.py, regression.py | finite-difference/unit checks; all 400 original training trials replay | Exact vs stop-gradient modes must remain separately labeled; full-cost inference not established |
| Fixed, learned, budget/gate/reset/feedforward/init controls | qlearn/natural_study.py, regression_study.py | original digit study, official Celo2 and complete 2x2 sensitivity | Faithful compatible ELO qualification and amortized cost; Celo2 pretraining overlap unresolved |
| Discrete MALIS actions | qlearn/malis.py | discrete-malis-v1, eight seeds | Separate action-engine claim, not evidence for continuous optimizer generalization |
| Q-APEN frozen learned quantizer plus continuous residual | qapen/causal.py | QAPEN_PROTOCOL/RESULTS; deterministic checkpoints | Finite k-means/linear-Gaussian scope; broader learned observation encoder/rollout claims not established |
| Stable expert UUIDs and optimizer state, prospective warmup, sleep/revival/prune/caps | qapen/causal.py | 512 cells and 1,024 exact checkpoint continuation predictions | First experiment mechanisms activate; generalized lifecycle efficacy not supported |
| Causal prequential mixture and delayed-utility memory read/write/consolidation | qapen/causal.py | full predictions, delayed intervention receipts, recent/random/no-memory controls | Full-cost/calibration/recovery synthesis; explicitly audit independently varied noise and delayed-cue coverage before QA completion |
| Finite lifecycle vs fixed/single/replay controls | scripts/closure/qapen_study.py | QAPEN_RESULTS.json | No incremental gain over strongest simple control; qualified expansion comparison remains to be adjudicated |
| QWIPII exact finite group actions, goal-compatible quotient and lifted paths | qwipii/group_actions.py, canonicalize.py, search.py, certificates.py | tests/qwipii; GATE_RESULTS repeated-label and fixed-goal cases | Exhaustive complete-domain/cost certification and full overhead accounting need strengthening |
| Bounded candidate discovery, rank-only suggestions, verified-only pruning | qwipii/discovery.py, verifier.py | Existing grammar heuristic and rejection tests | No trained discovery policy; verifier input-domain completeness must be made explicit, not inferred from passing sampled states |
| Rational projective transformations and pole rejection | qwipii/projective.py | rational cross-ratio and invalid-transform tests | Classical identity is support code, not a novel reasoning result |
| Optional equivariant coarse-graining/quantized learned representations | No discriminating trained implementation | NOT_RUN | Explicit original optional extension; no renormalization-flow or Olympiad claim retained |
| WCODE bounded typed DSL/fuel/resource contract | wcode/dsl.py, interpreter.py | runtime/adversarial tests and trained finite search audit | Trained study uses scalar integer functions; list/multivariable semantic coverage remains incomplete |
| Learned directed relations, ordered AST/root hierarchy, public-task-conditioned scorer | wcode/learned.py | six matched 15,336-parameter scorers; 28,416 replayed searches | Defined AST relations only, not a complete compiler data/control-flow graph |
| Common enumeration/verifier, semantic splits, failed traces, token/flat/ablation controls | scripts/closure/wcode_study.py | 331 canonical functions, 144 checkpoint scores, one full training replay | Full construction/scoring/interpreter cost analysis; broader depths/compositions; no unrestricted coding claim |
| WCODE/Ultron shared task lineage | WCODE_ULTRON_OVERLAP.json | 15 overlapping functions, four WCODE evaluation families | Separate-vs-consolidated paper decision and fresh heterogeneous Ultron families |
| WFIM exact word algebra, degree truncation, norm/tail conditions | wfim/algebra.py | exact algebra tests and top-k counterexample | Typed metadata/storage/error propagation and all original guarantees need full proof-to-code audit |
| Bounded invertible diagonal coordinates and transported product | wfim/transport.py | WFIM_BRANCH_DECISION, exact multiplicative scale cancellation | Current per-letter parameterization cannot change product; broader originally proposed per-word coordinates/decoder not executed |
| Byte-matched learned/identity coordinates, vector/bilinear/binding controls | No trained matching experiment | NOT_RUN | Determine the original nontrivial representation effect, then execute or close it with evidence; do not invent a new algebra |
| WFT PSD incidence weights, mass geometry and identifiable operator prediction | wft/constraints.py and earlier operator modules | WFT_PROTOCOL/RESULTS, 160 learned fits/64 controls | Current parametric physical field and equitable graphs do not cover arbitrary graph-weight distributions |
| Verified symmetry and cross-resolution constraints with independent fine/coarse parameters | wft/constraints.py | all four ablations, invalid-shift control, 2,688 independent numerical checks | Positive bounded transition effect is not yet a novel full-cost contribution |
| Frozen spectra, compression, repeated eigenspaces and setup cost | wft/constraints.py, analyze_wft.py, time_wft.py | gap-sensitive numerical audit; full timing supplement | Near-degenerate tolerance exception disclosed; no scalable FFT or arbitrary-operator claim |
| WPINN observed-only neural field/smoother, normalized sparse weak fit | wpinn/structured.py | 120 cells, 240 fields, 6,720 exact rollout receipts | Known-support inverse-PINN and data-only predictor baselines from original proposal are not replaced by known-support derivative regression |
| Analytic weak tests, valid odd/passive constraints, wrong conservation | wpinn/structured.py | analytic/convergence/unit tests; twelve-method ablations | Identifiability and physical-parameter holdouts remain incomplete; no complete advantage |
| Whole-trajectory splits, full polynomial rollouts, explicit failures | wpinn_study.py, diagnostic scripts | 600 disjoint IDs; original 17 failures preserved; solver/intervention diagnostics | Exclusive conditioning/support attribution is not proved; held parameter regimes still required |
| Optional alternating/joint field-law fitting and later PDEs | Not run | Original 07_wpinn.md explicitly makes alternation optional and PDEs later modules | Not required for the retained first sequential ODE study. This is an original-scope reading, not a post-result replacement |
| CWLNN trained sparse local/quotient/broadcast hierarchy | cwlnn/conditional.py | 128 models, matched parameter ranges, path/cycle/tree transfer | Arbitrary-tree receptive-field matching remains open |
| Learned pre-refinement top-k routing, declared surrogate, fixed controls | cwlnn/conditional.py | exact selected-row hooks/receipts; all four budgets | Half routing slower and less accurate than full hierarchy in this study; no universal routing advantage |
| Full cost, batch/parent boundaries, permutation and large sparse behavior | cwlnn_study.py, analyze_cwlnn.py, cwlnn_allocation.py | 23,040 predictions/permutations; 100,000-node shape probe | Local CPU/instrumented timing and largest-tensor evidence, not per-method peak RSS or universal scaling |
| Ultron typed capabilities, budgets, execution state and evidence DAG | ultron/capabilities.py, executor.py, state.py, evidence.py | existing contract/failure tests and finite DSL routing study | Full schema/path/hash/actual evaluator isolation audit required; no heterogeneous study yet |
| Development learned contextual routing vs identical-capability policies | ultron/router.py, train_router.py | UL01 nine-family reanalysis, all three budgets | Fresh DSL/law/invariant families, counterfactual training cost and full-cost endpoint |
| Evidence-aware or sequential orchestration | Present plumbing, no isolated scientific comparison | NOT_SUPPORTED as a contribution | First one-step ranker is allowed by proposal, but must not be called sequential reasoning; evidence-aware contribution needs an ablation |
| Independently controlled verifier | ultron/verifier_client.py is an interface only | External receipt absent | UL07 is a real external dependency; local fixtures remain PLUMBING_ONLY |

All implementation paths above are beneath src/world_series/ unless scripts or
artifact names are stated. Confirmation remains DRAFT_NOT_AUTHORIZED. Original
deferred ambitions (unrestricted code, arbitrary LLM optimization, infinite
expert inference, universal transforms and open-ended ASI) are not quietly
converted into completed results. Conversely, original required baseline and
generalization work remains open even when bounded studies pass software checks.
