# Ablation plan (development only)

All protocols: DRAFT_NOT_AUTHORIZED. Expected interpretations are **not facts**.

| ID | Project | Hypothesis | Independent var | Controls | Metric | Failure interpretation | Class |
|---|---|---|---|---|---|---|---|
| A-QL1 | qlearn | Budget features help | zero budget channel | same tasks/seeds | held AUC | no gain → features unused/harmful | RUN_NOW |
| A-QL2 | qlearn | Longer horizon hurts untuned meta | eval steps 2× train | fixed η baselines | final loss / diverge | divergence ↑ | RUN_NOW |
| A-QA1 | qapen | Memory helps rare regimes | no-memory vs engrams | matched updates | rare NLL | recent wins → lifecycle not needed | RUN_NOW |
| A-QA2 | qapen | Spawning helps | max_experts=1 vs 8 | same stream | mean NLL | no gain → overcapacity | RUN_NOW |
| A-QW1 | qwipii | Verification required for merge | ranking-only vs quotient | same starts | expansions + lift ok | ranking faster but unsafe if pruned | RUN_NOW |
| A-QW2 | qwipii | Adversarial transforms rejected | sort_suffix proposal | exhaustive verify | label REJECTED | if verified → verifier bug | RUN_NOW |
| A-WC1 | wcode | Hierarchy helps ranking | rank mode | shared pool | candidates_to_solve | uniform equal → encoder useless | RUN_NOW |
| A-WP1 | wpinn | Wrong conservation hurts damped | force c-term=0 | same traj | held rollout | if better → metric broken | RUN_NOW |
| A-WP2 | wpinn | Weak-only ≠ FD leakage | weak vs data-only | noise level | coef error / rollout | identical under noise→suspicious | RUN_NOW |
| A-WF1 | wfim | top-k breaks assoc | prune k=1 | trunc baseline | assoc bool | if assoc holds always → test weak | RUN_NOW |
| A-FT1 | wft | constraints help | constrained vs unconstrained | same X,Y | held MSE | unconstrained always better OK | RUN_NOW |
| A-CW1 | cwlnn | routing changes representation | route_budget on/off | same graph | output norm / receipt | identical → routing inert | RUN_NOW |
| A-UL1 | ultron | policies differ under hard tasks | task difficulty | identical tools | completion & cost | all 1.0 → non-discriminating eval | RUN_NOW |
| A-UL2 | ultron | wrong tool fails | force mismatched op | — | verifier ok | if ok → verifier rubber-stamps | RUN_NOW |

READY_BUT_EXPENSIVE: faithful Celo2/ELO/PETS ports; larger graphs; sealed Ultron eval.
