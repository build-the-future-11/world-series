# QWIPII learned proposal development results

Status: NOT_SUPPORTED for a runtime advantage in this bounded study. Confirmation: DRAFT_NOT_AUTHORIZED.

Eight seeds, five training goals of size 3–4, three selection goals of size 5, and four held goal patterns of size 6. Each seed evaluates four sampled starts per held goal. These are dependent repeated observations within four fixed ring patterns, not 128 independent families. No population significance or broad puzzle generalization claim is made.

| Method | Solved / cells | Mean expansions | Mean query ms |
|---|---:|---:|---:|
| brute | 128/128 | 25.1719 | 1.2703 |
| hand_quotient | 128/128 | 21.3047 | 18.5893 |
| learned | 128/128 | 21.3047 | 16.9859 |
| no_goal_feature | 128/128 | 23.8438 | 9.8558 |
| no_transition_feature | 128/128 | 21.3047 | 16.4099 |
| random | 128/128 | 23.9453 | 9.0092 |
| ranking_only | 128/128 | 4.0703 | 0.4242 |

Learned ordering uses four verification attempts, as does random ordering. Verification rejection consumes an attempt. Training uses exact orbit-reduction targets; a ridge coefficient is selected from four fixed choices on selection goals. Goal and transition feature removals are separately trained and selected. The hand quotient uses its known dihedral construction; it is not charged learned discovery costs.

Query timing includes sampled probe construction, proposal scoring, exact verification, certificate revalidation, orbit construction and search where applicable. Training/selection label verification and fitting times are stored separately per seed; the table is therefore not an amortized training-inclusive comparison. Timing is one observation per cell with shuffled method order, not a stable hardware performance guarantee. Peak memory and operation-level attribution remain open.

All 896 paths were separately replayed. Every nonranking method matches brute shortest-path length; greedy ranking returns longer paths in 16/128 cases despite its lower average expansion count. All 24 fitted models and selected model losses were exactly recomputed from saved training/selection arrays. The audit verifies source and artifact hashes.

Raw evidence: `campaigns/qwipii-learned-development-v1/{protocol.json,rows.jsonl,training-*.json,summary.json}`. Audit: `docs/closure/QWIPII_LEARNED_AUDIT.json`. Campaigns are preserved local artifacts included by the delivery builder; they are ignored by Git.

Remaining original requirements: whole new puzzle/generator families beyond the ring grammar, larger cases, stronger learned ranking controls, group-level uncertainty and precision planning, peak memory and full amortized costs, broader falsification and novelty comparison. This development study does not close those requirements.
