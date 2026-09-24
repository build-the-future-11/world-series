# QWIPII complete-domain certificate repair

The previous verifier accepted an empty domain and discovery labeled transforms exact after inspecting a sample of three problems. Historical outputs remain preserved and are not upgraded by this repair.

The verifier now rejects empty, duplicate, inconsistent, or incomplete domains. Domain completeness follows from distinct valid permutations and the exact multiset permutation count. It checks bijectivity, goal preservation, and every directed unit-cost ring transition. Discovery explicitly enumerates the full multiset domain with a 10,000-state allocation cap. The certificate contains the evaluated mapping, domain definition, scope, and deterministic SHA-256 witness digest.

Simultaneously transforming a board and its goal establishes problem equivalence. Fixed-goal pruning requires the additional fixed-goal check. Witnesses describe evaluated mappings, not future behavior of arbitrary mutable Python callables. Existing hand-coded dihedral search remains separate; this change does not introduce learned-action pruning.

Regression cases cover empty and incomplete samples, duplicates, a transform that is identity on the initial sample but fails bijectivity elsewhere, a bijection that fails transition preservation, repeated-label stabilizers, and allocation rejection before enumeration.

Still open: trained grammar ranking, certificate-bound learned quotient search, complete verification/canonicalization/training cost accounting, and held-out whole-family experiments. No checklist item is closed solely by these unit tests.
