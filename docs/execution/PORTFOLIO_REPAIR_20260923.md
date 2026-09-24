# World Series integrity repair — September 23, 2026

The existing development implementation is a small workbench, not the full accepted World Series models. Confirmation remains DRAFT_NOT_AUTHORIZED. This repair does not complete any whole project.

Fixed recorded seed application at run dispatch, decoupled AdamW decay, and train/dev-family fallback leakage. Added all-method AUC diagnostics, per-task raw trajectories and divergence denominators. Retained the legacy primary metric with its normalization limitations explicitly disclosed. The dimensionally invalid AUC-minus-final-loss proxy is now null and marked invalid; no historical run was overwritten.

Two new regressions failed against the original source: stochastic replay differed for the same recorded seed, and AdamW differed from the independent torch optimizer with nonzero decay. The repaired full suite passes. A fresh diagnostic run completed, including a SHA256-bound raw trajectory artifact. It is neither full model evaluation nor scientific confirmation.

New run: runs/20260923T224419_dd13a0eb. Prior raw runs and summary files remain retained. Full MALIS controller, full-state rollback, natural data, complete search/seed/ablation matrices, external evaluator and qualified comparison protocol remain outstanding.

Exact command receipts:

- WS-shared-engineering-tests: COMPLETE, exit 0; /Volumes/PRO-BLADE/.portfolio/logs/WS-shared-engineering-tests-20260923T170920.220286Z.log
- WS-after-repair-tests: COMPLETE, exit 0; /Volumes/PRO-BLADE/.portfolio/logs/WS-after-repair-tests-20260923T171255.472849Z.log
- WS-regressions-before-repair: FAILED, exit 1; /Volumes/PRO-BLADE/.portfolio/logs/WS-regressions-before-repair-20260923T171123.485375Z.log
- WS-qlearn-diagnostics: COMPLETE, exit 0; /Volumes/PRO-BLADE/.portfolio/logs/WS-qlearn-diagnostics-20260923T171417.752874Z.log
