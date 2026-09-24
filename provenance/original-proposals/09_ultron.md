# 09 — Ultron
## Working research title
Verified Budgeted Orchestration of Heterogeneous Research Capabilities.

ASI is a long-term motivation, not a v0.1 capability claim. Ultron initially coordinates a few real, tested modules under transparent budgets. It need not invoke all eight for every task, and an absent module must not be replaced with a fake successful adapter.

## Related work

The AI Scientist [R36], ADAS [R37], Darwin Gödel Machine [R38] and Co-Scientist [R39] already study research automation, agent design, agent modification and scientific hypothesis generation. The proposed question is whether a particular evidence-aware routing policy improves verified task completion over simpler policies with identical capabilities and resource budgets. “Multiple agents” or “self-improvement” alone is insufficient novelty.

## Typed state and actions

Represent a state as `(goal, task_type, evidence_DAG, capabilities, remaining_budget, failure_history)`. An action is a registered operation with typed inputs, expected artifact types, maximum cost and a verifier. The registry enumerates allowed actions; the model cannot invent a tool name and pretend it executed.

Examples: identify an oscillator law; solve a verified invariant puzzle; synthesize a bounded DSL program; fit a graph operator. Different tasks select different modules. A capability can be `AVAILABLE`, `UNAVAILABLE`, or `BLOCKED_BY_CONTRACT`; only available operations may run.

A full sequential research controller can be modeled as a finite-horizon constrained decision process. Start with a static router and a transparent state machine. The first learned extension is a contextual bandit or supervised ranker for choosing an applicable operation from development task features. Do not call this one-step selection a solved general meta-MDP. A sequential policy can follow after there is enough trustworthy trajectory data.

## Grounded objective

Use an externally computed objective such as

`R=verified_completion−λ measured_cost−κ invalid_actions`.

The completion score is computed by the task's verifier, not by the agent's prose, confidence or a self-written report. Separate partial engineering progress from final scientific correctness. A plot, paper draft or confident explanation does not count as successful law recovery unless the declared verifier checks it.

Evidence artifacts form a DAG: each result refers to input artifact hashes, producer version, config, cost receipt and verifier decision. Paths must resolve within the artifact root and hashes must match. Missing evidence is a hard failure for the corresponding claim, not an invitation to infer what probably happened.

## Execution state machine

```text
VALIDATE_TASK -> SELECT_AVAILABLE_ACTION -> RESERVE_BUDGET
  -> EXECUTE_REGISTERED_CAPABILITY -> VALIDATE_OUTPUT_SCHEMA
  -> VERIFY_RESULT -> APPEND_EVIDENCE -> STOP_OR_SELECT_NEXT
```

Errors release only the unused reserved budget, record the actual spent portion, and create an immutable failure receipt. Retries are bounded and counted. A module cannot change the task specification, success threshold or verifier while working on the task. Token/LLM costs are included if an optional language-model planner is added.

## Code units

| File | Responsibility |
|---|---|
| tasks.py | Research mini-task contracts and development task features |
| capabilities.py | Explicit operation registry and adapter availability |
| state.py | Immutable episode state and evidence references |
| router.py | Static, cheapest-valid, random-valid and learned policies |
| executor.py | Budget reservations and bounded capability execution |
| evidence.py | Hash-checked artifact DAG and claim provenance |
| verifier_client.py | Restricted interface to an independently controlled verifier |
| train_router.py | Development-only routing traces and policy fitting |
| evaluate.py | Matched-capability completion/cost comparisons |
| report.py | Structured evidence summary, never invented metrics |

The actual final verifier runs outside the development workspace. A client interface does not make a mutable in-process function independent. For tests, a toy verifier may live in fixtures, but fixture success is tagged `PLUMBING_ONLY` and cannot populate a research result table.

## Module adapters and integration boundaries

Start with QWIPII, WCode and World-PINN because they have clear verifiable outputs. Each adapter must pass standalone contract tests before registration. Remaining modules can register later when their real capability is useful: MALIS for adaptation, Q-APEN for prediction, WFIM for composition, WFT for transforms, CWLNN for encoding. No dependency requires all eight to be implemented before Ultron's state machine can be tested.

Avoid a forced linear pipeline through every module; it creates artificial dependencies and obscures attribution. If an exhibition includes a scripted all-module walkthrough, label it an architectural demonstration rather than evidence that the combined system outperforms simpler alternatives.

## Learning and baseline protocol

Collect development task outcomes for valid candidate modules under common budgets. Features must be available before the routing decision. Train a contextual bandit/ranker or imitate a development oracle that enumerates bounded choices. Counterfactual labels derived from running all modules cost real compute and belong in the training-cost ledger. Do not infer an untried route's outcome from the selected route's result.

Compare fixed task-type routing, cheapest valid routing, random valid routing, the learned policy and optionally a small monolithic planner with the same underlying tools/model access. Hold all capabilities and their checkpoints fixed during the routing comparison. Otherwise improvement could come from a stronger tool rather than better orchestration.

Primary: verified completion rate at a fixed per-task cost budget. Secondary: mean total cost, invalid action fraction, evidence completeness, latency, repeated-work overhead and ability to reject unsupported tasks. Report outcomes by task family and not only a pooled average dominated by the easiest task.

## Self-modification boundary

No automatic self-modification in v0.1. A later proposal system may generate patches in isolated worktrees, but changes to evaluators, protected tests, resource policy or approved claim thresholds are forbidden. Candidate changes are selected on development validation, reviewed and frozen before a separate confirmation evaluation. Reusing final holdout scores repeatedly to choose modifications would invalidate the “held-out” claim. An agent's own success declaration cannot approve its patch.

Darwin Gödel Machine uses an archive that can preserve useful stepping stones [R38]; do not mischaracterize that prior work as only monotonic hill climbing. Our safer scoped first experiment is routing, not an attempted replication of the entire self-improving-agent literature.

## Tests and Sunday slice

Unavailable capability rejection; typed input/output validation; path traversal rejection; artifact hash tampering; cycle detection in evidence DAG; verifier refusal; budget reservation/release; bounded retries; deterministic static routing; checkpoints fixed during evaluation; mock receipts excluded from scientific summaries; unsupported tasks reported truthfully; attempted evaluator modification blocked by actual environment controls.

Sunday demonstration: one task routed through one or more real modules with visible evidence and cost, plus a simpler-routing comparison where run. This can be useful research without pretending to be autonomous general science or ASI. Defer open-ended internet actions, external deployment, unrestricted code execution and recursive model rewrites.


---
