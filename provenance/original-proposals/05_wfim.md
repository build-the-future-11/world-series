# 05 — World-FIM∞
## Working research title
Learnable Coordinates in Sparse Completed Word Algebras with Certified Degree Truncation.

This study is separate from the existing Fabric-Induced Memory project. The infinity symbol denotes an underlying extensible mathematical space, not infinitely many stored values. The first useful deliverable is an exact algebra library, an error-aware finite representation and a controlled learning experiment. Do not call a high-dimensional tensor a newly discovered number system without defining operations and proving the claimed properties.

## Related work and positioning

Hypercomplex parameterizations [R17], hyperdimensional computing [R18], graded/signature representations [R19] and noncommutative algebra [R20] make high-dimensional representation a crowded and mathematically mature area. The proposed numerical construction deliberately uses existing algebraic foundations. Its possible contribution is a useful learning/approximation method with explicit guarantees, not the invention of infinite dimension or an isomorphic algebra.

## Chosen algebra, not arbitrary structure constants

Let words over an alphabet Σ index basis vectors. The empty word ε is the multiplicative identity. Define weighted absolutely summable series

`x=Σ_w x_w e_w`, `||x||_r=Σ_w |x_w|r^{|w|}<∞`, `r>0`.

Set `e_u⋆e_v=e_{uv}`. This is associative concatenation and, for at least two alphabet symbols, generally noncommutative. The product obeys `||x⋆y||_r≤||x||_r||y||_r`. MATH_FOUNDATIONS.md provides a short proof and assumptions.

Do not begin with a dense learned `C_ij^k` tensor. It has problematic storage growth and provides no automatic associativity, identity or norm control. A user-defined alternative product can be a later research branch, but must state exactly which axioms it satisfies.

## Finite representation and error guarantees

Use a sparse mapping from tuples of symbol IDs to coefficients. `P_N` removes degrees above N. For concatenation,

`P_N((P_Nx)⋆(P_Ny))=P_N(x⋆y)`.

Consequently the degree-truncated algebra retains associativity. With stronger norm bounds at `r'>r`,

`||x⋆y−P_N(x⋆y)||_r ≤ (r/r')^(N+1)||x||_{r'}||y||_{r'}`.

Return a tail certificate only when the caller supplies an actually justified stronger-norm bound. A finite observed prefix does not identify the unknown infinite tail. Distinguish exact finite polynomial inputs, certified series inputs and uncertified sampled representations.

Top-k coefficient pruning is different from degree truncation and may break associativity. Keep it in a separate approximate API that reports discarded mass and propagates an error bound when enough information exists. Never silently apply it in the exact reference product. Set a maximum output-term budget and estimate it before multiplication; on exhaustion return a typed error rather than silently dropping terms.

## Learned component that preserves the algebra

Use an invertible, degree-preserving coordinate map Sθ, initially a bounded positive diagonal scaling with `Sθ(e_ε)=e_ε`. Define

`x⋆θy=Sθ^{-1}((Sθx)⋆(Sθy))`.

Associativity and the unit are preserved by transport. Enforce nonzero scale bounds to control conditioning. The resulting algebra is isomorphic to the original; this is not a claim of a mathematically new algebra. The empirical question is whether the learned coordinates help a downstream compositional task under finite budgets. Compare to the same algebra with S=I; otherwise any benefit might come entirely from the fixed concatenation representation.

A more expressive block-per-degree Sθ is deferred because inverse conditioning and dense block storage can erase the efficiency objective. Avoid pretending an arbitrary neural encoder is an invertible linear algebra isomorphism.

## Data structures and APIs

`SparseElement`: sorted tuple keys, coefficients, alphabet ID, maximum degree, coefficient type, norm metadata and optional tail certificate.

`AlgebraSpec`: alphabet size, weighting r, product kind, identity, exact/approximate mode and budget.

`multiply_exact(x,y,max_degree,max_terms) -> SparseElement`.
`truncate_degree(x,N) -> SparseElement`.
`multiply_approx(x,y,policy) -> ApproximationResult`.
`transport_product(x,y,scales) -> SparseElement`.
`certify_tail(x,y,r_prime,N) -> TailBound | Unavailable`.

Exact reference coefficients use rational arithmetic on tiny examples. Differentiable finite experiments use tensors aligned with a frozen vocabulary/index map. Never mutate sparse index order between forward and backward. An input's alphabet and algebra version must match before multiplication.

## Code units

| File | Responsibility |
|---|---|
| words.py | Canonical word keys, degree and alphabet checks |
| elements.py | Typed sparse elements and sorted serialization |
| reference.py | Rational associative multiplication and degree truncation |
| norms.py | Weighted norms and justified error certificates |
| transport.py | Bounded invertible coordinate maps and differentiable product |
| approximate.py | Explicit optional pruning with measured discarded mass |
| tasks.py | Order-sensitive compositional sequence/operator benchmarks |
| baselines.py | Fixed same-algebra, vector binding and bilinear controls |
| evaluate.py | Accuracy, stored bytes, error bounds and algebraic diagnostics |
| adapter.py | `compose_algebraic_objects` capability |

## Experiment design

First exhaustively verify algebraic operations for tiny alphabets and degrees. Then train a small classifier/regressor on ordered compositions where order matters. Hold out composition templates and lengths. Keep an identity-insensitive task as a control: a complicated noncommutative representation should not be presumed useful everywhere.

Suggested starting caps: alphabet two to four, degree at most six, at most 4,096 stored terms, reference rational degree at most three. Dense dimension grows exponentially with degree; sparse representation postpones rather than eliminates worst-case growth. Record actual occupied terms and serialized bytes, including indices and metadata—not only coefficient count.

Minimum baselines: the identical fixed concatenation algebra; an ordinary fixed-size vector encoder; a simple bilinear composition model; and an appropriate binding/HDC-inspired control. A PHM-inspired layer can be an additional comparator after a reproduction note. Match downstream decoder capacity and available sequence information. Do not compare a memory-rich representation with a tiny vector and attribute all gains to algebra.

Primary development endpoint: task accuracy/error at a fixed representation-byte cap. Secondary: multiplication time, approximation error, norm growth, generalization to longer compositions and exact algebraic property violations. Mathematical correctness does not require beating a neural baseline.

## Required tests

Unit and associativity tests on exact polynomials; degree-truncation compatibility; zero and identity; alphabet mismatch; noncommutativity witness; coefficient serialization; norm submultiplicativity; valid tail bound on a known finite series; unavailable certificate for an unknown tail; transport/inverse round trip; transported associativity; gradients for finite transport parameters; deliberate top-k associativity counterexample; preallocation budget rejection.

The approximate product must never return `EXACT` merely because its numerical error is small on one sample. Test error propagation across repeated products and record when a bound becomes too loose to be useful.

## Sunday slice and future theory

Demonstrate exact composition, degree expansion and a certificate on a known example, then a measured small task comparison if available. The strongest honest mathematics result is the implemented classical guarantee plus a new computational study. Later work may investigate different completions, task-dependent bases, stable operators or genuinely new products—but each needs its own axioms, proofs and independent usefulness test.


---
