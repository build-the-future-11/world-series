> Update, 24 September 2026: this historical report is superseded for current completion status by development-v2/CURRENT_STATUS.md. All 400 original learned-policy meta-training trials now replay exactly, including optimizer state, counters, histories and expected failures; see development-v2/META_TRAINING_REPLAY.json. Natural-digit studies, additional comparators, bounded discrete actions and hash-verified campaign resume are now executed. Independent confirmation remains outstanding. Historical findings below are preserved.

# Neural development v1: results and evidence

Run `20260923T231444_deaee7ec`; completed 23 September 2026. Scientific outcome: **INCONCLUSIVE**. This is a completed constructed-task development matrix, not confirmation or completion of Quantum Learning/MALIS or the World Series portfolio.

The full learned update policy does not establish an advantage over tuned SGD. At width 128 and 64 steps, its mean gradient-step AUC is 3.607499 versus 3.776738 for SGD, with a paired five-seed sign-flip diagnostic p=1.0. Removing recurrence gives a lower descriptive AUC of 3.200437. These findings do not support attributing a demonstrated benefit to the full architecture. The full policy also takes about 6.59 times SGD's mean adaptation time on this host. Neither the small difference nor nonsignificance establishes equivalence.

## Completed denominator and failures

All five seeds, 700 tuning trials (400 learned-policy and 300 baseline trials), and 840 evaluation trajectories completed. Sixteen tuning trials failed or diverged and remain in the artifacts. Evaluation contains zero divergent rows. Executed support-gradient steps total 332,132 versus the declared maximum 332,160; early tuning failure explains the difference. No failed tuning trial was silently removed or counted as successful.

The supervised matrix took 1,708.63 seconds and peaked at 415.4 MiB process-tree RSS. Referenced artifacts occupy 340,959,505 bytes including the final summary; the runner's earlier 340,797,380-byte snapshot omitted final-summary serialization. These are separate from subsequent replay/analysis storage and resource use.

## Width 128, horizon 64

Twenty task rows per method are grouped into five independent training-seed units, four tasks each. All methods share task data and initializations within paired cells. Means below describe the declared matrix. Equal tuning-trial counts and support-gradient budgets do not equalize total compute.

| Method | Step AUC ↓ | Final normalized loss ↓ | Adaptation seconds |
|---|---:|---:|---:|
| full | 3.607499 | 0.030342 | 0.664364 |
| sgd | 3.776738 | 0.030003 | 0.100759 |
| momentum | 6.463706 | 0.013052 | 0.072696 |
| adamw | 37.056467 | 0.047444 | 0.085694 |
| no_budget | 3.656137 | 0.030631 | 0.631926 |
| no_recurrence | 3.200437 | 0.034438 | 0.629456 |
| no_gates | 3.388651 | 0.033409 | 0.129835 |


The predeclared principal descriptive contrast was full versus AdamW. AdamW has substantially worse AUC here, but that alone does not establish superiority against qualified strong comparators. Every comparator and ablation is included. Momentum ends with the lowest mean final normalized loss in this cell, illustrating why an AUC statement must not be substituted for a final-loss statement.

| Comparator | Comparator minus full AUC | Exact two-sided p |
|---|---:|---:|
| sgd | 0.169238 | 1.0000 |
| momentum | 2.856207 | 0.0625 |
| adamw | 33.448968 | 0.0625 |
| no_budget | 0.048638 | 0.0625 |
| no_recurrence | -0.407063 | 0.0625 |
| no_gates | -0.218848 | 0.4375 |


Five independent seeds yield a minimum attainable two-sided exact sign-flip p of 0.0625. The test also assumes sign symmetry under its null. These exploratory comparisons do not establish a multiplicity-adjusted superiority claim. The no-recurrence comparison changes parameter count as well as recurrence; it cannot isolate statefulness at matched capacity.

All 42 method/width/horizon cells are retained in [all_cells.csv](/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-analysis-20260923/all_cells.csv); all paired per-seed contrasts are in [comparisons.csv](/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-analysis-20260923/comparisons.csv). Methods and formal formulation are in [QLEARN_NEURAL_DEVELOPMENT_V1.md](QLEARN_NEURAL_DEVELOPMENT_V1.md).

## Verification and reproducibility

The source candidate is content-hashed `6a0fa8d2eff817671edba7a1fc806928f46fadb2a2c10a72e7ffc39f1659b924`. The repository has no Git commit; a source digest must not be described as a commit. The frozen archive and manifest live in [candidate v2](/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-candidate-20260923-v2/manifest.json).

The artifact auditor verified 1,222 artifact hashes, 80 dataset-task records, task splits and fixed scales, raw trajectories, trial selection, resource counters, and every evaluation cell. [Analysis receipt](/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-analysis-20260923/analysis.json).

A separate evaluation pass reloaded stored task arrays and selected checkpoints and reproduced all 840 full query-loss curves bit for bit. It replayed 31,360 support-gradient steps in 95.94 seconds, retaining final predictions. [Replay receipt](/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-analysis-20260923/replay/receipt.json), [prediction index](/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-analysis-20260923/replay/prediction_index.json), [predictions](/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-analysis-20260923/replay/final_predictions.npz). This is same-host evaluation replay; it does not replay meta-training or constitute independent replication.

The complete local suite passed 46 tests. Behavioral checks cover poisoned-query isolation, exact meta-gradients, persistent optimizer state and next-update checkpoint restoration, reference baselines, inactive ablation modules, and evaluation/full-graph trajectory equivalence. Three separate analysis contract tests passed. The earlier JSON parsing failure remains preserved as run `20260923T231110_84d466ae`.

Machine-generated [figure PDF](/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-analysis-20260923/figures/development-comparison.pdf) and [SVG](/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-analysis-20260923/figures/development-comparison.svg) accompany the raw CSVs. The figure's linear curve scale makes AdamW's instability prominent; numerical comparisons must use the full table, not visual compression of other methods.

## Remaining accepted work

Natural-data optimizees, qualified learned-optimizer and initialization-only comparators, the discrete MALIS actions, automatic whole-matrix resume, confirmatory protocol review, full meta-training replay, and independent verification remain incomplete. No paper submission, public upload, positive generalization claim, or full-project certification follows from these results. Original quadratic runs and protocols remain unchanged.

## Claim-to-evidence map

| Claim | Evidence | Status |
|---|---|---|
| All declared development cells executed and were audited | frozen config, analysis.json, raw run artifacts | SUPPORTED within this development matrix |
| Selected evaluation trajectories replay exactly on the same host | replay/receipt.json, prediction_index.json | SUPPORTED within same-host replay |
| Full controller improves on strong SGD | five seed contrasts, all_cells.csv | INCONCLUSIVE |
| Full architecture has a demonstrated advantage over its ablations | all ablation cells and paired contrasts | NOT_SUPPORTED within this development evidence |
| Benefits transfer to natural datasets or discrete MALIS | required studies unrun | INCONCLUSIVE; requirement remains open |
