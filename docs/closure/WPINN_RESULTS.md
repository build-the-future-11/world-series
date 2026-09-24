# Structured WPINN development results

DRAFT_NOT_AUTHORIZED for confirmation. Same-host audit; finite oscillator scope.

| Method | Failed /120 | Primary mean MSE | Successful-cell mean only | Exact support |
|---|---:|---:|---:|---:|
| raw_derivative | 29 | INCOMPLETE | 1.0813228 | 0.183 |
| raw_weak | 30 | INCOMPLETE | 0.77390266 | 0.383 |
| spline_weak | 26 | INCOMPLETE | 0.86071903 | 0.392 |
| neural_weak | 21 | INCOMPLETE | 0.87795439 | 0.342 |
| neural_derivative | 14 | INCOMPLETE | 0.37413085 | 0.300 |
| neural_weak_odd | 20 | INCOMPLETE | 0.43911999 | 0.342 |
| neural_weak_passive | 3 | INCOMPLETE | 0.11748595 | 0.592 |
| neural_weak_wrong_conservation | 0 | 0.31876872 | 0.31876872 | 0.333 |
| neural_weak_dense | 43 | INCOMPLETE | 0.18446069 | 0.000 |
| known_support | 0 | 545.72848 | 545.72848 | 0.667 |
| official_derivative | 30 | INCOMPLETE | 0.8620971 | 0.225 |
| official_weak | 39 | INCOMPLETE | 0.23177018 | 0.317 |

Audit: 6720 rollout receipts replay exactly; 1440 threshold selections verified; 240 saved fields reproduce predictions; all 600 whole-trajectory IDs are disjoint. One complete 400-update observation fit reproduces its trace and checkpoint exactly.

Physical constraints and known support provide additional information. Neural fields fit observations only; this is not joint physics-informed neural training. No general PDE, novelty, independent replication, or publication-ready claim follows from these results.

Post-study integration diagnostic: all four failed held trajectories in the three passive cells complete under both Radau and BDF at the unchanged 6,000-call cap, with decreasing recorded energy. MSE remains substantial (about 0.94–5.00). This supports stiffness sensitivity, not accurate identification. Original primary failures remain unchanged. See WPINN_PASSIVE_DIAGNOSTIC.json and its separate protocol.
