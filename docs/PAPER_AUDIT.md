# PAPER_AUDIT.md — World Series

There is **no manuscript**. This audit covers blueprint/README/exposition claims vs code+runs.

## SUPPORTED CLAIMS (narrow, evidence-backed)
- Installable package with nine namespaces exists and imports.
- CPU smoke/dev runners write immutable manifests under `runs/`.
- Planning pack validators pass (planning consistency only).
- Exact finite checks: mixture moments; Laplacian PSD/recon; word-algebra truncation assoc; DSL fuel; quotient path lift on small rings; Möbius pole rejection.
- Ultron rejects mismatched operation for `law_id` when `selected_op` is checked (`falsify` control).
- Wrong conservation on damped oscillator worsens held-out rollout vs weak-only (falsify + metrics).

## PARTIALLY SUPPORTED CLAIMS
- “Matched baselines exist” — yes at **toy** scale; not faithful paper reproductions.
- “Ablations exist” — plan + some executed controls; matrix not fully swept.
- “Ultron integrates real adapters” — yes; verification is **PLUMBING_ONLY**.

## UNSUPPORTED CLAIMS (must not appear as results)
- Any confirmation / preregistered win (`DRAFT_NOT_AUTHORIZED`).
- Olympiad reasoning, P=NP, ASI, infinite computation, quantum advantage.
- Superiority to Celo2/ELO/PETS/DreamCoder/AlphaGeometry.
- Ultron learned routing benefits (all policies hit ~1.0 completion on easy tasks).
- Q-APEN lifecycle superiority vs recent memory at toy scale (**falsify: NOT_SUPPORTED_AT_TOY_SCALE_vs_recent_memory**).

## MISSING EXPERIMENTS
- Multi-seed parameter-matched high-power studies
- Faithful external baseline ports
- Sealed external Ultron evaluation
- OOD / larger domains

## MISSING BASELINES
- Faithful Celo2/ELO; PETS; SINDy reference package; DreamCoder-style library learning

## MISSING ABLATIONS
- See remaining READY_BUT_EXPENSIVE rows in `experiments/ABLATION_PLAN.md`

## POTENTIAL OVERCLAIMS
- Status cards previously saying readiness without citing `research_outcome`
- Treating smoke SUCCEEDED as scientific SUPPORT
- Empty `QL/`… folders mistaken for repos

## REPRODUCIBILITY GAPS
- Often `git_head=null` (uncommitted tree); rely on `content_hash`
- No remote CI evidence
- Synthetic data only
- n=3 seeds: underpowered (qlearn primary std ≫ mean scale)
