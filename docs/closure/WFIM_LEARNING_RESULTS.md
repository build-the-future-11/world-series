# WFIM downstream coordinate results

Status: NOT_SUPPORTED for an incremental coordinate-learning benefit on the order-sensitive task. Development evidence only; no independent confirmation.

80 models: eight seeds × two tasks × five encoders. Binary words of length 2–8 are exhaustive within the declared finite set. There are 76 training, 18 selection, 30 held-template and 384 held-length sequences. Prefix templates 001 and 110 are held at lengths at most six; lengths seven and eight are separately held. Primary target is frequency of contiguous 001; fraction of ones is the order-insensitive control.

| Task | Encoder | Template MSE | Length MSE | Payload bytes | Mean train seconds |
|---|---|---:|---:|---:|---:|
| order | learned_coordinates | 0.03635235 | 0.00951358 | 54306 | 9.750 |
| order | identity_coordinates | 0.03581564 | 0.00603267 | 54307 | 3.191 |
| order | vector | 0.04092428 | 0.01101983 | 165360 | 2.763 |
| order | bilinear | 0.04281901 | 0.01195418 | 166400 | 3.880 |
| order | binding | 0.10511957 | 0.04226993 | 35247 | 0.647 |
| count | learned_coordinates | 0.00002794 | 0.00037275 | 54306 | 8.563 |
| count | identity_coordinates | 0.00003960 | 0.00029471 | 54307 | 3.899 |
| count | vector | 0.00573345 | 0.00634530 | 165360 | 2.985 |
| count | bilinear | 0.01161519 | 0.01172606 | 166400 | 3.157 |
| count | binding | 0.32366172 | 0.27909827 | 35247 | 0.768 |

Both coordinate methods use identical 127-coefficient representations and 32-unit decoders, initialized identically for each seed. Identity coordinates retain a frozen zero scale vector. Independent positive per-word scales are bounded and differentiable. Algebraic encoding multiplies normalized unit-plus-letter factors with degree-six truncation, producing ordered subsequence coefficients. Longer words therefore undergo the same explicit truncation.

Models share a 1 MiB payload cap, not an exactly equal used-byte budget. Payload includes tensors, product-index buffers, vocabulary and metadata; actual checkpoint container bytes are retained separately. Peak process memory and transient optimizer/activation storage are not included. The vector and bilinear controls consume substantially more payload. This study does not close the full byte-matched benchmark requirement.

All 80 selected checkpoints reload and exactly reproduce 40,640 predictions and coefficient norms. Targets and reported MSEs are independently recomputed from the explicit words. Source hashes match. Training histories are saved; only the chosen selection score/checkpoint is retained, so a full replay is still needed to independently reconstruct every checkpoint choice. Eight seeds characterize training variability over two fixed tasks, not an independent task population.

Learned coordinates do not beat identity coordinates on either held set of the order-sensitive task. The count control is mixed: learned coordinates improve held-template MSE but worsen held-length MSE. No general coordinate advantage follows. Remaining work includes matched-capacity/byte controls, norm-growth and approximation analysis, full training replay, broader justified task coverage, and novelty/branch disposition.

Raw campaign: `campaigns/wfim-coordinate-development-v1`. Audit: `docs/closure/WFIM_LEARNING_AUDIT.json`.
