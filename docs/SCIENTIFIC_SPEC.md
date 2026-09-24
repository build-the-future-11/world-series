# Scientific specification — World Series v0.1

Historical v0.1 scope below. The executed September 24 extensions and repaired
evaluation contracts are specified in `execution/development-v2/PROTOCOL.md`.
Natural binary-digit adaptation and bounded graph/stream/search studies are now
executed; the earlier wording describing all neural transfer as unimplemented
is superseded for those explicit scopes. Full architecture and independent
confirmation claims remain open.

Status tags: **DEFINED** / **IMPLEMENTED** / **TESTED** / **VALIDATED** / **SPECULATIVE**

## Shared contracts (DEFINED, IMPLEMENTED, TESTED)
Typed `TaskSpec`, `Budget`, `ModuleRequest/Result`, immutable run manifests with config hash + source content hash.
Confirmation remains **SPECULATIVE/unauthorized** (`DRAFT_NOT_AUTHORIZED`).

## qlearn — bounded diagonal meta-update
**DEFINED:** θ ← θ − η D g with η∈[ηmin,ηmax], diag(D)∈[a,b]>0; features exclude query labels.
**IMPLEMENTED:** quadratic tasks, BoundedDiagonalPolicy, unroll with create_graph, AdamW/SGD/momentum tuned baselines.
**TESTED:** finite-diff meta-grad smoke; bound rejection; family split.
**VALIDATED:** conditional descent inequality only on known-L quadratics (math pack) — **not** general NN training.
**SPECULATIVE:** transfer to neural optimizees; superiority vs Celo2/ELO.

## qapen — finite expert lifecycle
**DEFINED:** predict→record→observe→score→update; finite capacity; mixture moments.
**IMPLEMENTED:** ExpertBank lifecycle, EngramStore, fixed/recent/no-memory controls.
**TESTED:** mixture moments; capacity refuse.
**VALIDATED:** none at scientific claim level.
**SPECULATIVE:** “infinite” worlds; Bayesian nonparametric equivalence (**rejected by design**).

## qwipii — verified quotient search
**DEFINED:** only EXACTLY_VERIFIED automorphisms may merge; ranking-only may reorder not prune; Möbius/cross-ratio exact rationals.
**IMPLEMENTED:** ring domain, dihedral canonicalize, BFS/quotient/ranking, discovery grammar + adversarial reject.
**TESTED:** lift replay; pole/singular; adversarial REJECTED.
**VALIDATED:** small finite domains only.
**SPECULATIVE:** Olympiad geometry.

## wcode — bounded DSL synthesis
**DEFINED:** typed AST, fuel interpreter (no eval/exec); shared enumerator; rankers compared at equal candidate budget.
**IMPLEMENTED:** DSL+interpreter+graphs+rank modes.
**TESTED:** fuel; div0; ranker compare smoke.
**VALIDATED:** tiny grammar.
**SPECULATIVE:** P=NP implications (**forbidden claim**).

## wfim — word algebra
**DEFINED:** A_r completed free algebra; P_N truncation associative on deg≤N; top-k need not be.
**IMPLEMENTED:** sparse multiply/project/transport.
**TESTED:** identity/distributivity/trunc assoc; top-k counterexample flag.
**VALIDATED:** algebraic identities on finite supports.
**SPECULATIVE:** infinite coefficient storage claims (**forbidden**).

## wft — weighted spectral transform
**DEFINED:** L PSD; ΦᵀMΦ=I reconstruction; compare projectors not eigenvector signs.
**IMPLEMENTED:** path Laplacian, encode/decode, operator fits.
**TESTED:** PSD; recon; sign-flip projector invariance.
**VALIDATED:** tiny graphs.
**SPECULATIVE:** FFT-speed (**forbidden**).

## wpinn — weak-form oscillator ID
**DEFINED:** weak residual via IBP; conservation only if c=0; primary = held-out rollout MSE (declared).
**IMPLEMENTED:** weak-only LS, data-only & known-support controls, wrong-conservation ablation.
**TESTED:** energy structure; weak-only path; IBP sign corrected 2026-09-22.
**VALIDATED:** synthetic oscillators.
**SPECULATIVE:** general PDE discovery.

## cwlnn — sparse multiscale
**DEFINED:** parent maps; sparse≡dense on small; routing receipts; no hidden all-pairs.
**IMPLEMENTED:** coarsen, flat/hier/routed, budgeted attention control.
**TESTED:** sparse/dense equality; attention budget.
**VALIDATED:** path graphs only.
**SPECULATIVE:** universal backbone.

## ultron — budgeted orchestration
**DEFINED:** R = verified_completion − λ cost − κ invalid; external verifier; identical tools across policies.
**IMPLEMENTED:** static/cheapest/random/learned; evidence DAG; adapters.
**TESTED:** unsupported reject; path hash plumbing.
**VALIDATED:** **PLUMBING_ONLY** — not sealed eval.
**SPECULATIVE:** ASI / self-modification (**out of scope**).
