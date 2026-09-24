# QWIPII complete-domain certificate repair

The previous verifier accepted an empty domain and discovery labeled transforms exact after inspecting a sample of three problems. Historical outputs remain preserved and are not upgraded by this repair.

The verifier now rejects empty, duplicate, inconsistent, or incomplete domains. Domain completeness follows from distinct valid permutations and the exact multiset permutation count. It checks bijectivity, goal preservation, and every directed unit-cost ring transition. Discovery explicitly enumerates the full multiset domain with a 10,000-state allocation cap. The certificate contains the evaluated mapping, domain definition, scope, and deterministic SHA-256 witness digest.

Simultaneously transforming a board and its goal establishes problem equivalence. Fixed-goal pruning requires the additional fixed-goal check. Witnesses describe evaluated mappings, not future behavior of arbitrary mutable Python callables. Existing hand-coded dihedral search remains separate; this change does not introduce learned-action pruning.

Regression cases cover empty and incomplete samples, duplicates, a transform that is identity on the initial sample but fails bijectivity elsewhere, a bijection that fails transition preservation, repeated-label stabilizers, and allocation rejection before enumeration.

Still open: trained grammar ranking, certificate-bound learned quotient search, complete verification/canonicalization/training cost accounting, and held-out whole-family experiments. No checklist item is closed solely by these unit tests.

## Trained proposal mechanism

`learned_discovery.py` implements a seven-feature ridge ranker trained against exact single-generator orbit reduction. Features use public goal structure and sampled action behavior; proof labels are training targets only. At inference the grammar is scored, the declared number of top proposals is exhaustively checked, and only passing fixed-goal witnesses are returned. Rejected proposals consume the verification budget. Identity has zero orbit-reduction utility. The existing heuristic discovery function remains explicitly separate.

Twelve QWIPII tests now pass, covering changed learned weights and training error, bounded verification calls, zero budget, adversarial scores that cannot bypass verification, complete-domain contracts, and certified path replay/optimality. These are mechanism tests, not held-family research results. The next campaign must preserve separate training, selection and held goal families, charge sampled feature work and training-label verification, compare random and hand proposals under the same verification budget, and report end-to-end search costs including certificate revalidation.
