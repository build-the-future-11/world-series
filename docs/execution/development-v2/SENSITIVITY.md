# Selection and training-budget sensitivity

This separately declared follow-up keeps the original result unchanged. All methods receive six selection trials; meta-learning uses twelve rather than four outer steps. Tasks and seeds are reused development data, not a new holdout.

Completed: eight seed runs, 432 tuning trials and 432 evaluation trajectories. Failed tuning trials retained: 16.

Diverged or incomplete evaluation trajectories: 4. Required-cell aggregates are INCOMPLETE wherever a trajectory fails; no survivor-only mean is reported.

| Method | Original 32-step AUC | Follow-up AUC | Follow-up accuracy | Seeds choosing upper grid edge |
|---|---:|---:|---:|---:|
| adamw | 6.41449 | 6.414486150844294 | 0.9752604166666667 | 0 |
| feedforward | 13.1239 | 16.399609326791307 | 0.9270833333333333 | 7 |
| full | 13.2809 | INCOMPLETE | INCOMPLETE | 5 |
| initialization_only | 17.2602 | 13.85077006859699 | 0.9348958333333334 | 1 |
| momentum | 7.98933 | 7.989325295824565 | 0.9856770833333333 | 0 |
| no_budget | 13.2616 | INCOMPLETE | INCOMPLETE | 5 |
| no_gates | 14.016 | 12.015569439270772 | 0.9388020833333333 | 8 |
| reset_state | 13.5928 | INCOMPLETE | INCOMPLETE | 6 |
| sgd | 11.9562 | 11.956158316504986 | 0.94140625 | 0 |

Lower AUC is better. Celo2 retains its original four-rate external evaluation and is excluded from this matched-six-trial table. Grid-boundary selections remain a limitation wherever shown. The follow-up simultaneously changes trial range and meta-training duration, so it cannot isolate their individual effects.

Per-seed values, failed trials and source-bound run IDs are in sensitivity.json. A favorable development contrast must not be promoted to a confirmatory claim.
