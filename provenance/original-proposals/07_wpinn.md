# 07 — World-PINN
## Working research title
Weak-Form Law Identification with Verified Symmetry and Dissipation Constraints.

The project combines observation fitting, sparse law identification and validated structure. Inverse PINNs already address discovery [R27], so “the equations are unknown” is not its novelty claim. The proposal must show exactly which verified structural information improves identification and when it fails.

## Prior work and scientific distinctions

Forward PINNs [R26], inverse discovery [R27], SINDy [R28], structured symbolic regression [R29] and Hamiltonian networks [R30] are necessary context. Known PINN failure modes motivate tests beyond training residuals [R31]. Distinguish three tasks: unknown coefficients in known equations; unknown sparse support within a fixed library; and unknown functional forms outside the library. The first version tackles the first two only. It cannot claim arbitrary physical-law discovery.

## Primary system and identifiability

Start with a damped oscillator:

`q̇=v`, `v̇=−kq−cv`.

Generate multiple initial conditions, k and c values, sampling rates and noise realizations. Use c=0 as a conservative subset and c>0 as a dissipative subset. The observation interface exposes noisy trajectories; generator truth is available only to evaluation/oracle controls. If the signal does not excite relevant modes, coefficients may not be identifiable—record this, rather than assuming every trajectory uniquely determines the equation.

A small neural field `xθ(t,context)` fits observations, or use a simpler smoother as a baseline. Construct a declared candidate library Θ from normalized polynomial terms in q,v and any authorized derivatives. Normalize columns during sparse regression and restore original units afterward. A poorly scaled library can change apparent sparsity without changing the physics.

## Weak residual

For a test function ψ that vanishes at endpoints, use

`r(ξ)=∫ψ'(t)x(t)dt + ∫ψ(t)Θ(x(t))ξ dt`.

Minimize weak residuals plus data fitting and declared structure. This avoids direct finite-difference differentiation of noisy measurements, but smoothing and quadrature errors remain. Test quadrature on known analytic trajectories and vary sampling resolution. Do not secretly calculate derivatives from clean generator trajectories while claiming robustness to noisy-only observations.

A proposed objective is

`L=λ_data L_data+λ_weak ||r(ξ)||²+λ_sparse Penalty(ξ)+λ_structure L_verified`.

For a PINN variant include initial/boundary conditions explicitly. Use sequential thresholded least squares or another documented sparse method to select support, then refit coefficients without a shrinkage bias where appropriate. L1 shrinkage alone does not necessarily produce the exact symbolic support you want to report.

## Physics must be appropriate

For `E=(v²+kq²)/2`, `dE/dt=−cv²`. Conserve E only for c=0; use dissipation when c>0. A candidate symmetry or invariant supplied by QWIPII must be accompanied by a domain/assumption certificate. Its verification cannot use the same held-out outcome you later cite as evidence of successful generalization. Wrong constraints should be rejected when analytically decidable or retained as labeled failure-control experiments.

The first study does not need an autonomous symbolic theorem generator. It can compare verified known-applicable constraints with no constraints, then add learned candidate selection as a separately measured extension. Otherwise success may depend on hidden privileged knowledge of the true law.

## Staged fitting algorithm

```text
split full trajectories and physical parameter draws
fit observation smoother on training trajectories only
build a normalized declared candidate library
assemble weak-form integrals with endpoint-zero test functions
fit sparse support using development-selected hyperparameters
refit coefficients on the selected support
optionally alternate field fitting and law fitting with logged objectives
validate rollouts and structure on development trajectories
freeze code, library, selection thresholds and budget before confirmation
```

Alternation is optional; prove it adds value over the simpler sequential pipeline before making it mandatory. Different stopping points must be selected on development data only.

## Code units

| File | Responsibility |
|---|---|
| systems.py | Oscillator generators, truth separation and complete-trajectory splits |
| field.py | Small neural field and simpler smoothing interface |
| library.py | Typed candidate terms, units and normalization |
| weak_form.py | Test functions, quadrature and residual assembly |
| sparse_fit.py | Support selection, refitting and coefficient serialization |
| constraints.py | Conservation/dissipation and verified symmetry contracts |
| train.py | Sequential and optional alternating fitting |
| baselines.py | Least squares, SINDy-style, inverse PINN and data-only models |
| evaluate.py | Law recovery, rollout and uncertainty summaries |
| adapter.py | `identify_dynamical_law` |

`Trajectory` has times[T], observations[T,D], masks[T,D], trajectory_id and public context. `LibraryMatrix` carries named terms and scaling. `LawResult` contains symbolic terms, coefficients with units/scales, validity domain, support-selection settings, uncertainty method and measured evidence. A printed equation without those fields is not a reproducible result.

## Baselines, endpoints and ablations

Minimum: ordinary linear/sparse regression with the same library; a SINDy-style derivative baseline with its noise assumptions documented; a known-support inverse PINN; a data-only predictor; and the proposed weak/structure method. Known-support methods have extra information and should be labeled accordingly. Match observation access and tuning budget, not just epochs.

Choose one primary: support recovery on identifiable synthetic tasks, or held-out rollout error. The other remains important but cannot rescue a failed preregistered primary. Report coefficient error only after aligning term scaling and support. Include noise, missing samples, sampling rate and out-of-training parameter regimes. A correct fit on a single trajectory is not a general law-identification claim.

Ablate weak form, structural constraints, sparse selection, smoothing and alternating training separately. Include deliberately wrong conservation on damped trajectories as a failure demonstration, not as part of a production method that falsely assumes it is valid.

## Tests and Sunday slice

Analytic residual for a known oscillator; integration-by-parts identity under exact/accurate quadrature; polynomial autodiff including second derivatives where needed; library units/scales; support threshold behavior; coefficient round trip; no clean-target derivative leakage; trajectory-level split integrity; conservative and damped energy tests; held-out rollout integrator accuracy; finite loss and explicit convergence failure.

Sunday should demonstrate oscillator-law identification with transparent assumptions and real residual/rollout evidence. Burgers, KdV, reaction-diffusion, general Lie symmetry discovery and simultaneous unknown boundaries are later modules. Expanding from one ODE to several PDEs before validating identifiability would produce impressive names but uninterpretable evidence.


---
