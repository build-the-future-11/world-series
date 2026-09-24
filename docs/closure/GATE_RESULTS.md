# Closure diagnostics and recovered factorial

All original studies remain unchanged. The two missing corners were completed using the same numerical source; resume verified completed cell hashes. These are exposed development tasks.

## QLearn: separate grid width from training duration

| Method | Narrow/4 | Wide/4 | Narrow/12 | Wide/12 |
|---|---:|---:|---:|---:|
| adamw | 6.41449 | 6.41449 | 6.41449 | 6.41449 |
| feedforward | 13.1239 | 12.575 | 11.5376 | 16.3996 |
| full | 13.2809 | 14.9199 | 11.3869 | INCOMPLETE |
| initialization_only | 17.2602 | 14.5633 | 12.6938 | 13.8508 |
| momentum | 7.98933 | 7.98933 | 7.98933 | 7.98933 |
| no_budget | 13.2616 | 14.7359 | 11.6172 | INCOMPLETE |
| no_gates | 14.016 | 10.8972 | 12.7496 | 12.0156 |
| reset_state | 13.5928 | 11.5262 | 12.3748 | INCOMPLETE |
| sgd | 11.9562 | 11.9562 | 11.9562 | 11.9562 |

Lower 32-step AUC is better. All failures, measured tuning times and paired seed differences are retained in GATE_RESULTS.json. Missing required cells prevent a complete contrast; no survivor-only aggregate is substituted. Times are descriptive, not randomized equal-wall-time comparisons.

## Other decision gates

- WFIM: per-letter multiplicative transport cancels exactly. See WFIM_BRANCH_DECISION.md. No parameter search can improve this product.
- QWIPII: distinct fixed goals have no nontrivial stabilizer. Alternating repeated-label goals admit reduction, but canonicalization overhead exceeds the brute-search timing on these small cases. This establishes finite feasibility, not a novel general reasoning result.
- Ultron: learned minus training-selected best-fixed completion is 0 at cap 8, 0.15278 at cap 24, and 0 at cap 53. The cap-24 nine-family descriptive bootstrap interval is [-0.11111, 0.5]. The finite-family evidence is uncertain; 72 repeated example cases are not 72 independent task families.
- CWLNN: receptive-field-matched flat4 reaches approximately 1.77e-8 MSE at size 96 versus hierarchy 1.20174. The target itself uses four flat propagation steps, which explains this control advantage. The original hierarchy advantage over flat2 does not establish a hierarchy benefit. Current routing masks after coarse computation, so it does not save that computation.
- WPINN: all 288 fits reconstructed and all 17 failed rows retained with weak-design singular values, ranks, conditions and spurious-term energy. These diagnostics alone do not isolate a causal reason for failure.

Independent confirmation and full architectural claims remain open. Exact gate artifact hashes are listed in GATE_RESULTS.json.
