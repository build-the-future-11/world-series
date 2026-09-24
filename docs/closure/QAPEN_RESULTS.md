# Causal lifecycle and delayed-memory results

All 512 stream-method cells completed: 163,840 causal predictions. Artifact hashes, NLL recomputation, resource caps, prospective warmup and memory references passed audit.

| Method | Mean NLL | 95% coverage | Mean operation proxy | Total execution seconds |
|---|---:|---:|---:|---:|
| fixed_memory | 0.782116 | 0.9888 | 91584 | 9.108 |
| fixed_no_memory | 0.78534 | 0.9806 | 38400 | 5.693 |
| lifecycle_memory | 0.617267 | 0.9817 | 80168 | 8.511 |
| lifecycle_no_memory | 0.629536 | 0.9638 | 26984 | 5.162 |
| random_memory | 0.816825 | 0.9812 | 80168 | 5.807 |
| recent_memory | 0.573704 | 0.9799 | 80168 | 5.951 |
| rolling_ridge | 0.558932 | 0.9689 | 96048 | 0.563 |
| single_memory | 0.61225 | 0.9815 | 78144 | 8.213 |

Lower NLL is better. All methods obey the same operation cap, but actual work is unequal. The operation proxy omits hardware-specific constants; elapsed times are not randomized or equal-wall-time comparisons. Checkpoint bytes include state/serialization metadata and are not peak RSS. Codebook pretraining is shared and recorded separately.

| Control | Candidate minus control NLL | Descriptive paired-seed 95% interval |
|---|---:|---|
| fixed_memory | -0.164849 | [-0.204932254183973, -0.12637260218615604] |
| fixed_no_memory | -0.168073 | [-0.2230959220415361, -0.1183384629226131] |
| lifecycle_no_memory | -0.0122688 | [-0.02904149209551496, 0.0035383921999151595] |
| random_memory | -0.199558 | [-0.2227809842577349, -0.17746821265736717] |
| recent_memory | 0.0435629 | [0.037834068889118874, 0.04825427135954439] |
| rolling_ridge | 0.0583348 | [0.027627926162194526, 0.08897013768463968] |
| single_memory | 0.00501639 | [0.0015537469833427214, 0.008698424246779163] |

Intervals are exploratory, unadjusted and based on eight seed units. Do not treat the 163,840 timesteps as independent samples or infer practical equivalence. The complete condition table includes ordinary, rare and recovery metrics; unavailable rare/recovery cells in no-shift streams remain null.

This implements and exercises a finite linear-Gaussian lifecycle and memory candidate. It does not implement neural latent dynamics, imagination/planning or every later PEN-family proposal. All negative outcomes remain part of the evidence.
