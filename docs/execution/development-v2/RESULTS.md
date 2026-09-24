# Executed development results

Development evidence only; no confirmatory or independent-replication claim. All tables are regenerated from hash-verified runs.

Completed run receipts: 80. Natural tuning failures: 0. Module cells with integration/nonfinite failures: 17.

## Natural digit tasks at 32 adaptation steps

| Method | Mean step AUC | Mean final loss | Accuracy | Adaptation seconds |
|---|---:|---:|---:|---:|
| adamw | 6.41449 | 0.0813013 | 0.97526 | 0.166728 |
| feedforward | 13.1239 | 0.138194 | 0.972656 | 0.205859 |
| full | 13.2809 | 0.137048 | 0.970052 | 0.206814 |
| initialization_only | 17.2602 | 0.235879 | 0.959635 | 0.0567169 |
| momentum | 7.98933 | 0.0733278 | 0.985677 | 0.103525 |
| no_budget | 13.2616 | 0.137254 | 0.970052 | 0.322318 |
| no_gates | 14.016 | 0.142948 | 0.967448 | 0.122473 |
| official_celo2 | 7.74535 | 0.116044 | 0.980469 | 0.128526 |
| reset_state | 13.5928 | 0.140007 | 0.96875 | 0.18923 |
| sgd | 11.9562 | 0.325522 | 0.941406 | 0.134103 |

Step counts do not equalize training compute. Celo2 uses external pretrained weights and a PyTorch/JAX bridge; its time includes compilation/transfers.

## Paired seed diagnostics

| Comparator | Comparator minus full AUC | Exact p | Holm p |
|---|---:|---:|---:|
| adamw | -6.86646 | 0.0078125 | 0.0703125 |
| feedforward | -0.157085 | 0.820312 | 1 |
| initialization_only | 3.97923 | 0.0078125 | 0.0703125 |
| momentum | -5.29162 | 0.0078125 | 0.0703125 |
| no_budget | -0.019386 | 0.789062 | 1 |
| no_gates | 0.735041 | 0.015625 | 0.0703125 |
| official_celo2 | -5.53559 | 0.0078125 | 0.0703125 |
| reset_state | 0.311814 | 0.0078125 | 0.0703125 |
| sgd | -1.32479 | 0.203125 | 0.609375 |

Positive differences favor the full controller. Eight seed units share the same underlying dataset. Sign-flip diagnostics assume sign symmetry; these exploratory values do not authorize a superiority claim.

## Other modules

| Project | Method | Condition | Mean | Seeds |
|---|---|---|---:|---:|
| cwlnn | budget_attention | n24 | 37.6618 | 8 |
| cwlnn | budget_attention | n48 | 33.2129 | 8 |
| cwlnn | budget_attention | n96 | 33.4272 | 8 |
| cwlnn | flat | n24 | 2.26612 | 8 |
| cwlnn | flat | n48 | 2.11407 | 8 |
| cwlnn | flat | n96 | 2.11086 | 8 |
| cwlnn | hierarchy | n24 | 1.40685 | 8 |
| cwlnn | hierarchy | n48 | 1.21277 | 8 |
| cwlnn | hierarchy | n96 | 1.20434 | 8 |
| cwlnn | routed | n24 | 11.0952 | 8 |
| cwlnn | routed | n48 | 11.9123 | 8 |
| cwlnn | routed | n96 | 13.6939 | 8 |
| qapen | context_memory | all | 1.14129 | 8 |
| qapen | context_memory | ordinary | 1.02184 | 8 |
| qapen | context_memory | rare | 1.6191 | 8 |
| qapen | context_memory | return_first5 | 2.28526 | 8 |
| qapen | cumulative | all | 1.40313 | 8 |
| qapen | cumulative | ordinary | 0.97872 | 8 |
| qapen | cumulative | rare | 3.10079 | 8 |
| qapen | cumulative | return_first5 | 3.935 | 8 |
| qapen | fixed | all | 1.58173 | 8 |
| qapen | fixed | ordinary | 1.58538 | 8 |
| qapen | fixed | rare | 1.56712 | 8 |
| qapen | fixed | return_first5 | 1.55239 | 8 |
| qapen | no_memory | all | 1.34936 | 8 |
| qapen | no_memory | ordinary | 1.19216 | 8 |
| qapen | no_memory | rare | 1.97814 | 8 |
| qapen | no_memory | return_first5 | 2.26352 | 8 |
| qapen | random_memory | all | 1.3624 | 8 |
| qapen | random_memory | ordinary | 1.11324 | 8 |
| qapen | random_memory | rare | 2.35906 | 8 |
| qapen | random_memory | return_first5 | 2.8899 | 8 |
| qapen | recent | all | 1.51737 | 8 |
| qapen | recent | ordinary | 1.36018 | 8 |
| qapen | recent | rare | 2.14612 | 8 |
| qapen | recent | return_first5 | 4.80843 | 8 |
| qapen | single_expert_memory | all | 1.10035 | 8 |
| qapen | single_expert_memory | ordinary | 0.892972 | 8 |
| qapen | single_expert_memory | rare | 1.92988 | 8 |
| qapen | single_expert_memory | return_first5 | 3.15636 | 8 |
| qwipii | brute | n4/budget12 | 0.625 | 8 |
| qwipii | brute | n4/budget120 | 1 | 8 |
| qwipii | brute | n5/budget12 | 0.0833333 | 8 |
| qwipii | brute | n5/budget120 | 1 | 8 |
| qwipii | brute | n6/budget12 | 0.0416667 | 8 |
| qwipii | brute | n6/budget120 | 0.104167 | 8 |
| qwipii | quotient | n4/budget12 | 0.625 | 8 |
| qwipii | quotient | n4/budget120 | 1 | 8 |
| qwipii | quotient | n5/budget12 | 0.0833333 | 8 |
| qwipii | quotient | n5/budget120 | 1 | 8 |
| qwipii | quotient | n6/budget12 | 0.0416667 | 8 |
| qwipii | quotient | n6/budget120 | 0.104167 | 8 |
| qwipii | ranking_only | n4/budget12 | 1 | 8 |
| qwipii | ranking_only | n4/budget120 | 1 | 8 |
| qwipii | ranking_only | n5/budget12 | 1 | 8 |
| qwipii | ranking_only | n5/budget120 | 1 | 8 |
| qwipii | ranking_only | n6/budget12 | 0.604167 | 8 |
| qwipii | ranking_only | n6/budget120 | 1 | 8 |
| ultron | cheapest | budget24 | 0.666667 | 8 |
| ultron | cheapest | budget53 | 1 | 8 |
| ultron | cheapest | budget8 | 0.222222 | 8 |
| ultron | learned | budget24 | 0.819444 | 8 |
| ultron | learned | budget53 | 1 | 8 |
| ultron | learned | budget8 | 0.222222 | 8 |
| ultron | random | budget24 | 0.583333 | 8 |
| ultron | random | budget53 | 1 | 8 |
| ultron | random | budget8 | 0.222222 | 8 |
| ultron | static | budget24 | 0.444444 | 8 |
| ultron | static | budget53 | 1 | 8 |
| ultron | static | budget8 | 0.222222 | 8 |
| wcode | flat | budget24 | 0.666667 | 8 |
| wcode | flat | budget53 | 1 | 8 |
| wcode | flat | budget8 | 0.333333 | 8 |
| wcode | hierarchical | budget24 | 0.666667 | 8 |
| wcode | hierarchical | budget53 | 1 | 8 |
| wcode | hierarchical | budget8 | 0.333333 | 8 |
| wcode | length | budget24 | 0.444444 | 8 |
| wcode | length | budget53 | 1 | 8 |
| wcode | length | budget8 | 0.222222 | 8 |
| wcode | token | budget24 | 0.666667 | 8 |
| wcode | token | budget53 | 1 | 8 |
| wcode | token | budget8 | 0.333333 | 8 |
| wcode | uniform | budget24 | 0.444444 | 8 |
| wcode | uniform | budget53 | 1 | 8 |
| wcode | uniform | budget8 | 0.222222 | 8 |
| wfim | topk | degree2 | 24.0937 | 8 |
| wfim | topk | degree3 | 19.7167 | 8 |
| wfim | topk | degree4 | 10.4059 | 8 |
| wfim | transported | degree2 | 1.40413e-31 | 8 |
| wfim | transported | degree3 | 4.23935e-31 | 8 |
| wfim | transported | degree4 | 8.004e-31 | 8 |
| wfim | truncated | degree2 | 0 | 8 |
| wfim | truncated | degree3 | 0 | 8 |
| wfim | truncated | degree4 | 0 | 8 |
| wft | constrained_laplacian | n12/noise0.0/samples32 | 9.79168e-07 | 8 |
| wft | constrained_laplacian | n12/noise0.0/samples8 | 1.06672 | 8 |
| wft | constrained_laplacian | n12/noise0.1/samples32 | 0.00621551 | 8 |
| wft | constrained_laplacian | n12/noise0.1/samples8 | 0.936957 | 8 |
| wft | constrained_laplacian | n12/noise0.5/samples32 | 0.16494 | 8 |
| wft | constrained_laplacian | n12/noise0.5/samples8 | 1.40947 | 8 |
| wft | constrained_laplacian | n24/noise0.0/samples32 | 5.61575e-05 | 8 |
| wft | constrained_laplacian | n24/noise0.0/samples8 | 1.75382 | 8 |
| wft | constrained_laplacian | n24/noise0.1/samples32 | 0.0564387 | 8 |
| wft | constrained_laplacian | n24/noise0.1/samples8 | 1.64809 | 8 |
| wft | constrained_laplacian | n24/noise0.5/samples32 | 1.52973 | 8 |
| wft | constrained_laplacian | n24/noise0.5/samples8 | 1.86932 | 8 |
| wft | fixed_unit_weights | n12/noise0.0/samples32 | 0.481537 | 8 |
| wft | fixed_unit_weights | n12/noise0.0/samples8 | 0.42091 | 8 |
| wft | fixed_unit_weights | n12/noise0.1/samples32 | 0.417016 | 8 |
| wft | fixed_unit_weights | n12/noise0.1/samples8 | 0.534791 | 8 |
| wft | fixed_unit_weights | n12/noise0.5/samples32 | 0.59467 | 8 |
| wft | fixed_unit_weights | n12/noise0.5/samples8 | 0.44112 | 8 |
| wft | fixed_unit_weights | n24/noise0.0/samples32 | 0.517903 | 8 |
| wft | fixed_unit_weights | n24/noise0.0/samples8 | 0.54457 | 8 |
| wft | fixed_unit_weights | n24/noise0.1/samples32 | 0.512812 | 8 |
| wft | fixed_unit_weights | n24/noise0.1/samples8 | 0.574068 | 8 |
| wft | fixed_unit_weights | n24/noise0.5/samples32 | 0.42746 | 8 |
| wft | fixed_unit_weights | n24/noise0.5/samples8 | 0.479264 | 8 |
| wft | oracle_true_graph | n12/noise0.0/samples32 | 0 | 8 |
| wft | oracle_true_graph | n12/noise0.0/samples8 | 0 | 8 |
| wft | oracle_true_graph | n12/noise0.1/samples32 | 0 | 8 |
| wft | oracle_true_graph | n12/noise0.1/samples8 | 0 | 8 |
| wft | oracle_true_graph | n12/noise0.5/samples32 | 0 | 8 |
| wft | oracle_true_graph | n12/noise0.5/samples8 | 0 | 8 |
| wft | oracle_true_graph | n24/noise0.0/samples32 | 0 | 8 |
| wft | oracle_true_graph | n24/noise0.0/samples8 | 0 | 8 |
| wft | oracle_true_graph | n24/noise0.1/samples32 | 0 | 8 |
| wft | oracle_true_graph | n24/noise0.1/samples8 | 0 | 8 |
| wft | oracle_true_graph | n24/noise0.5/samples32 | 0 | 8 |
| wft | oracle_true_graph | n24/noise0.5/samples8 | 0 | 8 |
| wft | ridge | n12/noise0.0/samples32 | 1.91502e-06 | 8 |
| wft | ridge | n12/noise0.0/samples8 | 1.83356 | 8 |
| wft | ridge | n12/noise0.1/samples32 | 0.00553742 | 8 |
| wft | ridge | n12/noise0.1/samples8 | 1.64063 | 8 |
| wft | ridge | n12/noise0.5/samples32 | 0.149861 | 8 |
| wft | ridge | n12/noise0.5/samples8 | 2.4421 | 8 |
| wft | ridge | n24/noise0.0/samples32 | 4.21878e-05 | 8 |
| wft | ridge | n24/noise0.0/samples8 | 3.53452 | 8 |
| wft | ridge | n24/noise0.1/samples32 | 0.0316954 | 8 |
| wft | ridge | n24/noise0.1/samples8 | 3.32704 | 8 |
| wft | ridge | n24/noise0.5/samples32 | 0.919063 | 8 |
| wft | ridge | n24/noise0.5/samples8 | 3.7535 | 8 |
| wpinn | data_only | k1.0/c0.0/noise0.0 | 2.30427e-07 | 8 |
| wpinn | data_only | k1.0/c0.0/noise0.02 | INCOMPLETE | 8 |
| wpinn | data_only | k1.0/c0.0/noise0.1 | INCOMPLETE | 8 |
| wpinn | data_only | k2.0/c0.3/noise0.0 | 1.86878e-06 | 8 |
| wpinn | data_only | k2.0/c0.3/noise0.02 | INCOMPLETE | 8 |
| wpinn | data_only | k2.0/c0.3/noise0.1 | INCOMPLETE | 8 |
| wpinn | data_only | k4.0/c0.8/noise0.0 | 4.93386e-06 | 8 |
| wpinn | data_only | k4.0/c0.8/noise0.02 | INCOMPLETE | 8 |
| wpinn | data_only | k4.0/c0.8/noise0.1 | INCOMPLETE | 8 |
| wpinn | known_support | k1.0/c0.0/noise0.0 | 7.28149e-07 | 8 |
| wpinn | known_support | k1.0/c0.0/noise0.02 | 0.0276726 | 8 |
| wpinn | known_support | k1.0/c0.0/noise0.1 | 32.1948 | 8 |
| wpinn | known_support | k2.0/c0.3/noise0.0 | 1.86878e-06 | 8 |
| wpinn | known_support | k2.0/c0.3/noise0.02 | 0.0390983 | 8 |
| wpinn | known_support | k2.0/c0.3/noise0.1 | 70.1638 | 8 |
| wpinn | known_support | k4.0/c0.8/noise0.0 | 4.93386e-06 | 8 |
| wpinn | known_support | k4.0/c0.8/noise0.02 | 0.0738058 | 8 |
| wpinn | known_support | k4.0/c0.8/noise0.1 | 100.353 | 8 |
| wpinn | weak | k1.0/c0.0/noise0.0 | 7.35095e-07 | 8 |
| wpinn | weak | k1.0/c0.0/noise0.02 | 0.092705 | 8 |
| wpinn | weak | k1.0/c0.0/noise0.1 | INCOMPLETE | 8 |
| wpinn | weak | k2.0/c0.3/noise0.0 | 1.95371e-06 | 8 |
| wpinn | weak | k2.0/c0.3/noise0.02 | INCOMPLETE | 8 |
| wpinn | weak | k2.0/c0.3/noise0.1 | 1.05049 | 8 |
| wpinn | weak | k4.0/c0.8/noise0.0 | 3.72396e-06 | 8 |
| wpinn | weak | k4.0/c0.8/noise0.02 | 0.0142762 | 8 |
| wpinn | weak | k4.0/c0.8/noise0.1 | INCOMPLETE | 8 |
| wpinn | wrong_conservation | k1.0/c0.0/noise0.0 | 7.35095e-07 | 8 |
| wpinn | wrong_conservation | k1.0/c0.0/noise0.02 | 0.0846918 | 8 |
| wpinn | wrong_conservation | k1.0/c0.0/noise0.1 | INCOMPLETE | 8 |
| wpinn | wrong_conservation | k2.0/c0.3/noise0.0 | 0.101261 | 8 |
| wpinn | wrong_conservation | k2.0/c0.3/noise0.02 | INCOMPLETE | 8 |
| wpinn | wrong_conservation | k2.0/c0.3/noise0.1 | 0.236313 | 8 |
| wpinn | wrong_conservation | k4.0/c0.8/noise0.0 | 0.386302 | 8 |
| wpinn | wrong_conservation | k4.0/c0.8/noise0.02 | 0.392751 | 8 |
| wpinn | wrong_conservation | k4.0/c0.8/noise0.1 | INCOMPLETE | 8 |

All method/condition cells, missing values and denominators are retained in the adjacent CSV and JSON files. INCOMPLETE means at least one required seed contains a failed/nonfinite row; no finite-only mean is substituted.

Discrete MALIS results are in malis_per_seed.csv. They concern a phase-conditioned support-progress controller and full-state action engine, not completion of the full proposed architecture.
