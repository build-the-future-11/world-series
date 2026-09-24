# 01 — Quantum Learning / MALIS
## Working research title
Bounded Meta-Learned Update Policies for Resource-Aware Adaptation.

The project studies classical learning algorithms. “Quantum Learning” is a brand, not a claim about qubits, quantum speedup, subjective awareness or metacognition. The eventual ambition is a controller that adapts optimization, curriculum, memory and computation. The first experiment isolates optimization; adding all those mechanisms at once would obscure attribution.

## Related work and the exact gap to test

Learned optimizers [R01], meta-learned initializations [R02], Celo [R03], Celo2 [R04] and ELO [R05] cover substantial parts of the original idea. In particular transfer and long-horizon stability are already active research targets. Our candidate question is narrower: can a bounded controller conditioned on task progress and remaining budget improve a predeclared compute-normalized objective across held-out optimizee families? This is a hypothesis, not an established novel result. Celo2 and ELO deserve stronger-comparator evaluation beyond the demonstration phase.

## Mathematical definition

For task τ, support data Sτ fits the optimizee and query data Qτ scores adaptation. Let θ_t be functional optimizee parameters, g_t a support gradient and m_t a momentum feature. A shared controller maps per-parameter and per-layer normalized features into positive diagonal gates and a bounded step size:

`(η_t,D_t,h_{t+1}) = π_φ(features(g_t,m_t,loss_progress,budget),h_t)`

`θ_{t+1}=θ_t−η_t D_t g_t`.

Enforce `η_min≤η_t≤η_max` and `a≤diag(D_t)≤b` with smooth parameterizations. Initialize near a stable fixed rule. Controller features never contain query labels or future losses. The outer loss may use query losses because it is the meta-training objective, but that is not information available to the controller at inference.

Proposed outer objective:

`J(φ)=E_τ[Σ_t ω_t normalized_query_loss(θ_t) + λ_cost C(τ) + λ_fail 1[diverged]]`.

Normalize by a fixed task scale or initial loss plus ε, not by the candidate's best outcome. Discrete failure penalties are diagnostics/selection signals unless an explicitly documented gradient estimator handles them. Do not pretend a Boolean divergence penalty supplies useful differentiable gradients.

The conditional descent inequality in MATH_FOUNDATIONS.md applies to known L-smooth objectives with a bounded positive preconditioner. Use it as a theorem-backed quadratic sanity check. It is not a safety proof for arbitrary neural training, momentum, stochastic gradients or unknown curvature.

## Data and first experiment

Generate positive-definite quadratics with controlled condition numbers and task-specific minimizers. Then add small linear regression and two-layer MLP regression tasks. Split entire distributions: hold out condition-number ranges, function families and model widths. Begin with batch four tasks, controller hidden width 32, 16 unrolled steps and optimizee width 64. These are resource caps, not tuned results. Evaluate horizon 32 or 64 only after the 16-step loop is sound.

A task object returns support/query batches independently and a task_id. It exposes analytic curvature only to the oracle baseline and reference tests, never covertly to the learned controller. Use separate result labels for oracle-information controls.

## Contracts and tensors

`OptimizeeSpec.build(seed) -> parameter_dict, buffer_dict`.
`FunctionalOptimizee.loss(params, buffers, batch) -> scalar`.
`FeatureBuilder.build(params, grads, state, budget) -> features[P,F]`.
`UpdatePolicy.forward(features[P,F], state[P,H]) -> gates[P], step_sizes[layer], new_state`.
`InnerLoop.unroll(task, policy, steps) -> Trajectory`.
`MetaTrainer.step(tasks) -> MetaMetrics`.

P is flattened parameter count. A metadata table maps slices back to named shapes; assert exact round trips. No shared controller state across independent tasks. All learned-policy parameters must receive finite gradients in a tiny diagnostic problem. Use `torch.func.functional_call` to evaluate parameter dictionaries [D02].

## Files and implementation units

| File under src/world_series/qlearn | Responsibility |
|---|---|
| tasks.py | Quadratic/regression task generation, family splits and oracle flags |
| functional.py | Parameter flatten/unflatten and functional loss evaluation |
| features.py | Stable gradient/momentum/budget features with explicit detach policy |
| policy.py | Bounded positive gates, controller state and reset |
| unroll.py | Exact short differentiable inner loop; separate named truncated mode |
| meta_train.py | Outer objective, finite-gradient checks and checkpointing |
| baselines.py | Tuned SGD, momentum, AdamW, fixed schedule and small learned control |
| evaluate.py | Loss-versus-compute, divergence and longer-horizon evaluation |
| adapter.py | Capability `adapt_learner` returning checkpoint and evidence |

Implement the exact tiny loop first. Use `autograd.grad(create_graph=True)` for the reference meta-gradient. Do not mutate `.data`, call an ordinary in-place optimizer inside the differentiable loop, or detach the update graph accidentally. Full-gradient finite-difference checks require matching analytic dependencies; a deliberately first-order/stop-gradient mode must have its own name and tests. Truncated backpropagation introduces bias and must not be represented as an exact full-horizon meta-gradient.

## Reference algorithm

```text
for task in independent_meta_batch:
    params, buffers = initialize_optimizee(task.seed)
    policy_state = zeros_for_this_task()
    for step in range(unroll_steps):
        support_loss = functional_loss(params, buffers, task.support(step))
        grads = differentiable_gradient(support_loss, params)
        features = build_features(grads, history, remaining_budget)
        params, policy_state = bounded_update(params, grads, features, policy_state)
        outer_terms.append(query_loss(params, task.query(step)))
    record instability without discarding the task
backpropagate declared outer objective into controller parameters
```

## Baselines and ablations

Minimum controls: tuned fixed-step SGD, momentum SGD, AdamW with a matched tuning budget, and a small learned update policy without task/budget features. An initialization-only meta-learning control is meaningful on the same adaptation task, but do not force it into incomparable optimizer-only settings. Ablate budget features, gate learning, recurrence and task augmentation separately. Later evaluate a faithful Celo2/ELO implementation through a separate runner with its dependency/license records; a simplified substitute must not inherit their names.

Primary development endpoint: area under normalized validation-loss-versus-measured-compute curve, lower is better. Also report final loss, divergence fraction, adaptation time, peak memory and amortized meta-training cost. Select an interpretable practical effect threshold before final confirmation; it is intentionally not fabricated here.

## Required tests and completion gates

Reference tests: analytic quadratic gradient; flatten/unflatten identity; conditional descent when assumptions hold; finite-difference check of one outer parameter in CPU float64. Candidate tests: bounds always respected; task states reset; query labels inaccessible to policy; nonzero finite outer gradients; checkpoint reload matches the same next update; budget exhaustion stops deterministically. Include a deliberately unstable large-step control so the divergence detector is genuinely exercised.

The smoke suite may use two tasks and four steps. Passing means the implementation works, not that MALIS beats AdamW. Mechanism benchmarking requires the same tasks, tuning policy and compute counters for all comparators. An unsuccessful controller remains a valid `NOT_SUPPORTED` result.

## Sunday slice and deferred work

Demonstrate learning-policy adaptation on tiny tasks with a baseline trace and actual run manifest. Present a held-out example only from the authorized demonstration split. Defer curriculum selection, dynamic architecture surgery, optimizer mutation, memory policies, arbitrary LLM training and meta-meta control. These become separately versioned hypotheses after the bounded update-policy study is interpretable.


---
