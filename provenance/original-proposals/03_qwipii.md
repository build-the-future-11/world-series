# 03 — QWIPII
## Canonical project name
Quantized World Renormalized Invariant Projective Inductive Intelligence.

The first implementation is a verified invariant-guided reasoner. The name is an ambition map, not evidence that quantization, renormalization, projective geometry and Olympiad-level induction have all been solved. Keep exact symbolic objects separate from optional learned representations.

## Related work

G-CNNs formalize equivariance [R09]; LieGAN and later symmetry-discovery methods already learn transformations [R10–R11]; information-based RG work studies coarse-graining [R12]; AlphaGeometry demonstrates neural-symbolic geometry reasoning [R13]. The proposed distinction is a verification gate between discovered transformations and correctness-critical search reductions. Whether the particular implementation is novel requires further comparison, not an acronym.

## Two lanes: proposing versus certifying

A discovery model proposes candidate invariants or transformations from a bounded grammar. A verifier determines the permitted use. Labels are `PROPOSED`, `EMPIRICALLY_SUPPORTED`, `EXACTLY_VERIFIED_WITHIN_DOMAIN`, or `REJECTED`. Only exact verified automorphisms may merge search states. Approximate invariants may rank candidates or suggest lemmas; they cannot erase possibilities.

For a group action `g·x`, invariance means `I(g·x)=I(x)`; equivariance means `E(g·x)=ρ(g)E(x)`. Encode both domain and codomain actions. A constant embedding is invariant but useless, so training also needs non-collapse and task-usefulness checks. Invariant loss alone is not a sufficient objective.

## Exact quotient search

Begin with a finite puzzle domain such as token transformations on a ring. Define full problem states including constraints and goal predicates. Use a finite candidate group (e.g. dihedral permutations) only when it preserves legal transitions, costs and the goal set. If a specific target breaks symmetry, use its stabilizer or transform the entire problem consistently; do not quotient only the board while keeping an incompatible goal fixed.

Canonicalization:

`can(s)=min_{g∈G} serialize(g·s)`.

Store the minimizing witness g. A quotient edge stores a concrete legal transition and witness transformations so the returned solution can be lifted back to the original state. MATH_FOUNDATIONS.md states the assumptions needed to preserve reachability and shortest-path costs. Exhaustively test them on all small instances before introducing a learned ranker.

## Projective slice

Implement one-dimensional projective transformations with exact rational arithmetic:

`T(x)=(a x+b)/(c x+d)`, with `ad−bc≠0` and defined denominators.

For four distinct admissible points, test the cross-ratio

`CR(a,b;c,d)=((a−c)(b−d))/((a−d)(b−c))`.

The same argument names should not be confused with the matrix entries in code; use distinct identifiers. Verify invariance using symbolic/rational arithmetic and explicit pole checks. Either implement the projective point at infinity correctly or reject it; never divide through a zero denominator and report a generic numerical failure. This is a compact proof-backed demo, not a general projective geometry theorem prover.

## Coarse-graining slice

Optional `R_l` maps fine symbolic features to a coarser representation. Test consistency `R_lρ_l(g)≈ρ_{l+1}(g)R_l`. This is an equivariant coarse-graining constraint. Call it that, not a fully established renormalization flow with fixed points/exponents unless those objects are defined and analyzed. Quantization may be added to learned representations but must not alter exact proof certificates silently.

## Code units

| File | Responsibility |
|---|---|
| domains.py | Finite transition systems, legal moves, goals and costs |
| group_actions.py | Exact finite actions, composition, inverses and domain checks |
| invariant_grammar.py | Parity, modular residues, bounded polynomial/permutation candidates |
| discovery.py | Candidate scoring/training on development problems |
| verifier.py | Exhaustive finite-domain checks and rational projective identities |
| canonicalize.py | Orbit representative and witness transforms |
| search.py | Brute BFS, quotient BFS and ranking-only variants |
| certificates.py | Replayable proof/path certificates |
| projective.py | Rational Möbius transforms and cross-ratios |
| adapter.py | `solve_invariant_problem` and `verify_certificate` capabilities |

`Transformation.apply(problem_state) -> state`; `verify_automorphism(domain, transformation) -> certificate`; `Search.solve(problem,budget) -> path_certificate`. A certificate includes domain version, assumptions, checked property, witness and verification method. “Verified” must name the finite domain or theorem actually covered.

## First learning experiment

Generate training problems from several known families and ask a small ranker to choose candidate invariants or group generators. Discovery is selection within a declared grammar, not arbitrary invention of all mathematical concepts. Split by canonical problem orbit and generator family to avoid transformed duplicates crossing the boundary. Compare brute search; exact hand-specified quotient search; learned ranking with no pruning; learned proposal plus verification; and oracle symmetry selection. The oracle is an upper-bound diagnostic with additional information, not a standard fair baseline.

Primary: verified solved fraction under a fixed expansion/time budget. Secondary: expansions including discovery/verification overhead, certificate length, rejected invariant count and performance under held-out admissible transformations. Also run fixed-success comparisons of cost conditional on a common solved subset, clearly labeled to avoid selection bias.

## Tests and adversarial cases

Test group identity/composition/inverses; canonicalization idempotence; exact orbit equivalence; all legal transitions remain legal; goal/cost preservation; path lifting and replay; agreement with exhaustive BFS on every small state; invalid proposed symmetry rejected; constant invariant cannot trigger pruning; rational cross-ratio preservation; singular transform and pole errors; budget abort preserves partial evidence.

A deliberate false transformation that matches a few samples but fails one state is mandatory. The test should show it may remain a heuristic suggestion but cannot enter the quotient verifier's trusted registry. Avoid assigning a theorem-proved label to a neural score.

## Sunday slice and future scope

Show one proof-preserving search reduction and one projective-invariance identity with actual certificates. Neural discovery can be a development add-on after exact infrastructure passes. Broad Olympiad benchmarks, theorem-library mining, Lie-group discovery outside the grammar and formal Lean integration are later versions. A synthetic puzzle result must not be advertised as general Olympiad ability.


---
