# Current module cards

Generated from executed development-v2 evidence; see complete protocol and result tables.

## qlearn
**BENCHMARKED / INCONCLUSIVE**
Eight-seed natural-digit study: 288 tuning trials, 432 trajectories; official pretrained Celo2 adds 48 trajectories. Full mean AUC 13.2809 vs SGD 11.9562, AdamW 6.4145, Celo2 7.7454 at 32 steps. No general optimizer advantage established. Discrete action prototype evaluated separately. Separate eight-seed wider-grid/longer-training follow-up: 432 tuning trials and 432 evaluation trajectories audited. 32-step mean AUC: full INCOMPLETE (failed required trajectories), AdamW 6.4145, momentum 7.9893. Failed tuning trials: 16; diverged/incomplete evaluation trajectories: 4. See SENSITIVITY.md for every method, failed trials and grid boundaries. Original primary results remain unchanged; reused tasks provide development evidence only. Later 2x2 study separates grid width and training duration: full narrow/12 AUC 11.3869, wide/4 14.9199; wide/12 remains incomplete. Strong fixed controls still have lower mean AUC. See docs/closure/GATE_RESULTS.md.

## qapen
**BENCHMARKED / INCONCLUSIVE**
New causal context-memory intervention with all/rare/ordinary/return metrics and matched prediction calls. Tradeoffs remain: single-expert memory improves overall mean; fixed ensemble improves rare-regime mean. Legacy candidate memory is write-only. A new finite linear-Gaussian lifecycle implementation completes 512 stream-method cells with frozen quantization, prospective admission, sleep/revival, delayed utility and exact checkpoints. Mean NLL 0.61727 vs single-memory 0.61225 and rolling ridge 0.55893. No advantage over the strongest simple controls. See docs/closure/QAPEN_RESULTS.md.

## qwipii
**BENCHMARKED / INCONCLUSIVE**
Canonical keys retain concrete replayable paths. Exhaustive 3/4-token regression tests pass. No quotient savings on tested distinct fixed-goal puzzles; ranking-only control performs better under the limited cap. Repeated-label feasibility cases have nontrivial stabilizers and fewer expansions, but higher measured runtime on the tiny cases. Distinct-goal no-savings findings remain.

## wcode
**BENCHMARKED / INCONCLUSIVE**
Eight-seed finite-DSL matrix with honest candidate accounting. Hierarchical, flat and token heuristics tie at the 24-candidate cap. Encoders are untrained structural heuristics. A later trained study uses 331 semantic functions, six matched-count scorers and two fixed orderings across eight seeds. All 28,416 searches and 144 checkpoint selections were audited. At cap24, relational solves 10.54% of family holdouts versus token 9.80%, and 0% of held compositions. No reliable advantage over trained controls is established. Fifteen functions overlap earlier WCODE/Ultron data, including four current evaluation families; all results remain development evidence. See docs/closure/WCODE_RESULTS.md.

## wfim
**BENCHMARKED / INCONCLUSIVE**
Finite support/degree/cost matrix and an actual top-k associativity counterexample. Truncation/transport identities do not establish learned downstream benefit or new algebra. Per-letter transport cancels exactly by s(uv)=s(u)s(v); its product-expressivity claim is closed as NOT_SUPPORTED. Algebra code is preserved. See WFIM_BRANCH_DECISION.md.

## wft
**BENCHMARKED / INCONCLUSIVE**
Weighted-path noise/sample/size matrix uses matched Laplacian targets. Unit-weight and true-graph oracle baselines are distinguished. Refit at each size is not transfer. A later equitable-graph study completes 160 learned fits and 64 fixed/oracle controls with frozen transfer to new sizes and path topology. Mean transfer error: both constraints 0.00030388 versus identical unconstrained 0.00092856. All 2,688 predictions were checked with NumPy/SciPy; gap-sensitive compression discrepancies are disclosed. This supports the bounded construction, not broad graph or novelty claims. Full graph/setup timing is recorded separately. See docs/closure/WFT_RESULTS.md.

## wpinn
**BENCHMARKED / INCONCLUSIVE**
Three laws and three noise levels; independent held initial conditions. All polynomial terms evaluated with bounded integration. Seventeen failed rollouts remain in denominators; affected means are absent. All 288 saved fits were reconstructed and the 17 failures have conditioning/support diagnostics; causal failure attribution is still open. A later 120-cell, twelve-method study includes learned observation fields, analytic weak quadrature, physical constraints and official PySINDy controls. All 6,720 rollouts and 1,440 threshold selections replay exactly. Unconstrained neural weak fitting fails in 21 cells; passive fitting fails in three. Primary aggregates with failures remain incomplete. Implicit-solver diagnostics resolve the four passive work-cap failures without changing original values. No complete advantage, joint physics-training, held-law or PDE claim. See docs/closure/WPINN_RESULTS.md.

## cwlnn
**BENCHMARKED / INCONCLUSIVE**
Matched-size trained readouts on fixed sparse representations; graph sizes 24/48/96. Aggressive routing hurts the declared residual-propagation task. No universal-backbone evidence. Matched flat4 control achieves about 1.77e-8 MSE at n96 versus hierarchy 1.20174. The constructed target uses four flat propagation steps. Current routing computes all coarse features before masking; no conditional-compute saving is demonstrated. A later genuinely conditional study trains 128 models and audits 23,040 predictions/permutations and 256 checkpoint scores. At half routing, learned hierarchy is slower and less accurate than full hierarchy on both declared tasks despite halving refinement rows. Full hierarchy benefits the aligned task; flat5 is better on nonhierarchical diffusion. All primary configurations meet the local 3ms ceiling. Allocation probing reaches 100,000 sparse nodes. This is a bounded negative routing result, not a universal backbone or independent replication. See docs/closure/CWLNN_DECISION.md.

## ultron
**BENCHMARKED / INCONCLUSIVE**
Discriminating finite-DSL routing with identical tools/caps and disjoint semantic training/evaluation families. At cap 24: learned 81.94%, cheapest 66.67%, random 58.33%, static 44.44%. Not a general agent or sealed external evaluation. Against the training-selected best fixed tool, cap24 difference is 0.15278, with exploratory nine-family bootstrap interval [-0.11111,0.5]. Repeated example seeds are not independent new families.

