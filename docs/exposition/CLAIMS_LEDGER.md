# Current claims ledger

Every claim is bounded by PROTOCOL.md and the raw run index. Confirmation remains DRAFT_NOT_AUTHORIZED.

## qlearn
Status: BENCHMARKED / INCONCLUSIVE
Eight-seed natural-digit study: 288 tuning trials, 432 trajectories; official pretrained Celo2 adds 48 trajectories. Full mean AUC 13.2809 vs SGD 11.9562, AdamW 6.4145, Celo2 7.7454 at 32 steps. No general optimizer advantage established. Discrete action prototype evaluated separately. Separate eight-seed wider-grid/longer-training follow-up: 432 tuning trials and 432 evaluation trajectories audited. 32-step mean AUC: full INCOMPLETE (failed required trajectories), AdamW 6.4145, momentum 7.9893. Failed tuning trials: 16; diverged/incomplete evaluation trajectories: 4. See SENSITIVITY.md for every method, failed trials and grid boundaries. Original primary results remain unchanged; reused tasks provide development evidence only. Later 2x2 study separates grid width and training duration: full narrow/12 AUC 11.3869, wide/4 14.9199; wide/12 remains incomplete. Strong fixed controls still have lower mean AUC. See docs/closure/GATE_RESULTS.md.

Executed evidence: `runs/20260924T101150_3293b6ce/metrics.json`, `runs/20260924T101337_3dcca138/metrics.json`, `runs/20260924T101408_c64e5cf8/metrics.json`, `runs/20260924T101424_7c1bb9dc/metrics.json`, `runs/20260924T101438_973894fc/metrics.json`, `runs/20260924T101451_a3afb019/metrics.json`, `runs/20260924T101502_a111c875/metrics.json`, `runs/20260924T101513_5c3f6c57/metrics.json`, `runs/20260924T101553_ac358792/metrics.json`, `runs/20260924T101558_f80e0fd7/metrics.json`, `runs/20260924T101601_7a194abc/metrics.json`, `runs/20260924T101604_c919a6e4/metrics.json`, `runs/20260924T101607_715f1f5c/metrics.json`, `runs/20260924T101610_e30b51a5/metrics.json`, `runs/20260924T101612_9f607bbf/metrics.json`, `runs/20260924T101615_67b9ff70/metrics.json`
Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.

## qapen
Status: BENCHMARKED / INCONCLUSIVE
New causal context-memory intervention with all/rare/ordinary/return metrics and matched prediction calls. Tradeoffs remain: single-expert memory improves overall mean; fixed ensemble improves rare-regime mean. Legacy candidate memory is write-only. A new finite linear-Gaussian lifecycle implementation completes 512 stream-method cells with frozen quantization, prospective admission, sleep/revival, delayed utility and exact checkpoints. Mean NLL 0.61727 vs single-memory 0.61225 and rolling ridge 0.55893. No advantage over the strongest simple controls. See docs/closure/QAPEN_RESULTS.md.

Executed evidence: `runs/20260924T100958_fbdd5589/metrics.json`, `runs/20260924T101000_c43111d0/metrics.json`, `runs/20260924T101002_266faeea/metrics.json`, `runs/20260924T101002_a2a2fce6/metrics.json`, `runs/20260924T101003_b15fff76/metrics.json`, `runs/20260924T101004_b7fb230d/metrics.json`, `runs/20260924T101005_23d6fd5d/metrics.json`, `runs/20260924T101006_99d78cd4/metrics.json`
Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.

## qwipii
Status: BENCHMARKED / INCONCLUSIVE
Canonical keys retain concrete replayable paths. Exhaustive 3/4-token regression tests pass. No quotient savings on tested distinct fixed-goal puzzles; ranking-only control performs better under the limited cap. Repeated-label feasibility cases have nontrivial stabilizers and fewer expansions, but higher measured runtime on the tiny cases. Distinct-goal no-savings findings remain.

Executed evidence: `runs/20260924T101006_fe0803e7/metrics.json`, `runs/20260924T101008_9fb915d2/metrics.json`, `runs/20260924T101009_e9b7640a/metrics.json`, `runs/20260924T101010_fb71d64f/metrics.json`, `runs/20260924T101011_f164f7e2/metrics.json`, `runs/20260924T101013_5b560050/metrics.json`, `runs/20260924T101014_77e06898/metrics.json`, `runs/20260924T101015_848b57a0/metrics.json`
Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.

## wcode
Status: BENCHMARKED / INCONCLUSIVE
Eight-seed finite-DSL matrix with honest candidate accounting. Hierarchical, flat and token heuristics tie at the 24-candidate cap. Encoders are untrained structural heuristics.

Executed evidence: `runs/20260924T101017_8bfd1d89/metrics.json`, `runs/20260924T101017_67d8da7c/metrics.json`, `runs/20260924T101018_fae6dd67/metrics.json`, `runs/20260924T101018_bb709535/metrics.json`, `runs/20260924T101019_91f19f67/metrics.json`, `runs/20260924T101019_91b5840d/metrics.json`, `runs/20260924T101020_86183074/metrics.json`, `runs/20260924T101021_fb02dd59/metrics.json`
Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.

## wfim
Status: BENCHMARKED / INCONCLUSIVE
Finite support/degree/cost matrix and an actual top-k associativity counterexample. Truncation/transport identities do not establish learned downstream benefit or new algebra. Per-letter transport cancels exactly by s(uv)=s(u)s(v); its product-expressivity claim is closed as NOT_SUPPORTED. Algebra code is preserved. See WFIM_BRANCH_DECISION.md.

Executed evidence: `runs/20260924T101021_eeafc090/metrics.json`, `runs/20260924T101022_de1b36be/metrics.json`, `runs/20260924T101022_e644734a/metrics.json`, `runs/20260924T101022_d00724c2/metrics.json`, `runs/20260924T101022_95423da5/metrics.json`, `runs/20260924T101023_04afa7a3/metrics.json`, `runs/20260924T101023_fe23e07d/metrics.json`, `runs/20260924T101024_53e0cd8e/metrics.json`
Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.

## wft
Status: BENCHMARKED / INCONCLUSIVE
Weighted-path noise/sample/size matrix uses matched Laplacian targets. Unit-weight and true-graph oracle baselines are distinguished. Refit at each size is not transfer.

Executed evidence: `runs/20260924T101024_663f5d4e/metrics.json`, `runs/20260924T101024_367b304a/metrics.json`, `runs/20260924T101025_f0b04e16/metrics.json`, `runs/20260924T101025_4d3306d0/metrics.json`, `runs/20260924T101025_936a73a1/metrics.json`, `runs/20260924T101026_ac7d359e/metrics.json`, `runs/20260924T101026_f4ad9fed/metrics.json`, `runs/20260924T101026_58169e7e/metrics.json`
Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.

## wpinn
Status: BENCHMARKED / INCONCLUSIVE
Three laws and three noise levels; independent held initial conditions. All polynomial terms evaluated with bounded integration. Seventeen failed rollouts remain in denominators; affected means are absent. All 288 saved fits were reconstructed and the 17 failures have conditioning/support diagnostics; causal failure attribution is still open.

Executed evidence: `runs/20260924T101027_1846bd37/metrics.json`, `runs/20260924T101028_9a1baa31/metrics.json`, `runs/20260924T101029_b9086c9a/metrics.json`, `runs/20260924T101030_0bf9211f/metrics.json`, `runs/20260924T101033_ee8a9248/metrics.json`, `runs/20260924T101039_d2868364/metrics.json`, `runs/20260924T101041_eaf6492c/metrics.json`, `runs/20260924T101042_90d9b14a/metrics.json`
Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.

## cwlnn
Status: BENCHMARKED / INCONCLUSIVE
Matched-size trained readouts on fixed sparse representations; graph sizes 24/48/96. Aggressive routing hurts the declared residual-propagation task. No universal-backbone evidence. Matched flat4 control achieves about 1.77e-8 MSE at n96 versus hierarchy 1.20174. The constructed target uses four flat propagation steps. Current routing computes all coarse features before masking; no conditional-compute saving is demonstrated.

Executed evidence: `runs/20260924T101046_497744e7/metrics.json`, `runs/20260924T101047_ae3add90/metrics.json`, `runs/20260924T101048_32d0cd9d/metrics.json`, `runs/20260924T101049_0971ecfa/metrics.json`, `runs/20260924T101050_8392a88e/metrics.json`, `runs/20260924T101050_d959f8e2/metrics.json`, `runs/20260924T101051_0af6f6f1/metrics.json`, `runs/20260924T101052_3fa5d3c3/metrics.json`
Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.

## ultron
Status: BENCHMARKED / INCONCLUSIVE
Discriminating finite-DSL routing with identical tools/caps and disjoint semantic training/evaluation families. At cap 24: learned 81.94%, cheapest 66.67%, random 58.33%, static 44.44%. Not a general agent or sealed external evaluation. Against the training-selected best fixed tool, cap24 difference is 0.15278, with exploratory nine-family bootstrap interval [-0.11111,0.5]. Repeated example seeds are not independent new families.

Executed evidence: `runs/20260924T101052_9e5e6c01/metrics.json`, `runs/20260924T101054_a4980064/metrics.json`, `runs/20260924T101055_61127588/metrics.json`, `runs/20260924T101056_8fcc4055/metrics.json`, `runs/20260924T101057_ab03fbed/metrics.json`, `runs/20260924T101057_f5a877a3/metrics.json`, `runs/20260924T101058_22da8727/metrics.json`, `runs/20260924T101059_0f3f73ea/metrics.json`
Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.

Historical negative evidence remains in `experiments/falsification_results.json` and original runs. Later bounded interventions do not retroactively turn those negatives into wins.
No universal-intelligence, novelty, full-architecture, sealed-evaluator or publication-readiness claim is supported.
