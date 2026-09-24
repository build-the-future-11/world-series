# CWLNN conditional routing development results

DRAFT_NOT_AUTHORIZED for confirmation. CPU reference, finite synthetic graph tasks.

| Task | Model | Route fraction | MSE | Median ms | Feasible seeds /8 |
|---|---|---:|---:|---:|---:|
| multiscale | hierarchy_full | 1.0 | 0.01141182 | 0.7133 | 8 |
| multiscale | flat5_full | 1.0 | 0.01277588 | 0.6396 | 8 |
| multiscale | local_full | 1.0 | 0.01371251 | 0.5660 | 8 |
| multiscale | attention_full | 1.0 | 0.01339096 | 0.8114 | 8 |
| multiscale | hierarchy_learned | 0.5 | 0.01193894 | 0.7673 | 8 |
| multiscale | hierarchy_norm | 0.5 | 0.01186852 | 0.6854 | 8 |
| multiscale | hierarchy_hash | 0.5 | 0.0120162 | 0.6844 | 8 |
| multiscale | flat5_learned | 0.5 | 0.01276936 | 0.6927 | 8 |
| diffusion | hierarchy_full | 1.0 | 0.02983086 | 0.7125 | 8 |
| diffusion | flat5_full | 1.0 | 0.02738658 | 0.6389 | 8 |
| diffusion | local_full | 1.0 | 0.02913366 | 0.5674 | 8 |
| diffusion | attention_full | 1.0 | 0.02906956 | 0.8134 | 8 |
| diffusion | hierarchy_learned | 0.5 | 0.03272091 | 0.7595 | 8 |
| diffusion | hierarchy_norm | 0.5 | 0.03285116 | 0.6848 | 8 |
| diffusion | hierarchy_hash | 0.5 | 0.03272892 | 0.6804 | 8 |
| diffusion | flat5_learned | 0.5 | 0.02828503 | 0.6909 | 8 |

All four budget curves, paired seed differences, raw timing lists and source hashes are retained. The routed primary point is fixed at 0.5; no held-error budget selection. Feasibility requires at least95% of72 graphs below3ms within each seed/task. Median latency alone does not establish feasibility.

Audit: 23040 predictions and permutations, 256 selection scores, 1792 disjoint graph IDs. Maximum permutation discrepancy 4.44e-16. One full160-update learned-router fit replays exactly.

Timing includes instrumented receipts, input conversion, validation, public hierarchy construction, routing and decoding. Training compute differs because full controls process all nodes. Learned routing adds49 parameters. The multiscale task is hierarchy-aligned; diffusion is not. Flat receptive-field matching is limited to training paths, not arbitrary tree groupings. No universal sparse-backbone, novelty or independent-replication claim.
