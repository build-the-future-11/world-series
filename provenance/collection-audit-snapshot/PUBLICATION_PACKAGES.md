# Required final publication packages

There are **zero submission-ready packages** today. The existing `world-series/deliveries/20260924-development/` archive is a verified local review package, with 3,749 members and a valid Git bundle. It is valuable reproducibility infrastructure, not a completed submission. Its manifest matches the current source content hash and commit. Celo2 weights are deliberately not redistributed.

Use one package for each scientifically justified retained paper. Do not create nine papers merely because nine namespaces exist. WCODE and Ultron may share a package if their eventual contributions are inseparable; disclose overlapping datasets and results explicitly. The existing cross-module draft can serve as a technical report, but a list of unrelated pilots is not by itself a coherent research contribution.

```text
paper/                 complete editable manuscript, bibliography, rendered PDF
source/                exact source snapshot + commit/content hash
figures/               generated figures + source data references
tables/                generated complete tables + denominators
supplement/            protocol, proof details, ablations, failures, deviations
configs/               frozen development and final-evaluation configurations
results/               immutable raw outputs, hashes, claim_index.json
scripts/               reproduce_paper.py and full experiment commands
README                 exact scope, quick verification, full reproduction
LICENSE                chosen project license + third-party/data notices
environment/           runtime/OS/hardware manifest and resolved dependency locks
REPRODUCTION.md        clean setup, data/weight fetch, time/storage, tolerances
```

Each `claim_index.json` record must contain: claim identifier and wording; estimand and direction; source commit/content hash; config/protocol hash; dataset/version/split hash; all attempted units and failures; raw run references; estimator script/version; table/figure identifier; and allowed interpretation. A theorem maps to assumptions, proof and code checks rather than an invented experiment. A failed required cell must invalidate the relevant aggregate unless the frozen estimand defines a different failure-aware statistic.

| Existing project | Required paper focus, if it survives closure | Required project-specific package contents | Current missing pieces |
|---|---|---|---|
| QLearn | Resource-aware adaptation or a rigorous bounded optimizer limitation | Full trials/checkpoints, selection and meta-training costs, all horizons, instability, Celo2/ELO qualification and data-overlap statement | Matched-cost cross-family decision, complete focused manuscript, novelty and fresh evaluation |
| Q-APEN | Attribution of capacity lifecycle and delayed memory | Quantizer/lifecycle events, prequential distributions, memory intervention receipts, rare/ordinary/recovery tables, equal-cost controls | Core mechanism, factorial schedule study and focused manuscript |
| QWIPII | Correct verified reductions with useful search effect, or a substantive scoped limitation | Domain/group/goal definitions, orbit proof, certificate and lifted-path traces, full search/canonicalization cost | Nontrivial useful symmetry/discovery contribution, wider evaluation, novelty |
| WCODE | Trained relational hierarchy in bounded synthesis | Semantic split ledger, training traces/checkpoints, candidate pool/verifier hashes, per-family solve/cost and learned ablations | Trained encoders, transfer study and contribution beyond heuristics |
| WFIM | Nontrivial byte-budget representation result, if any; otherwise supporting library | Algebra proofs, exact/approximate API distinction, tail assumptions, cancellation note, full index/metadata bytes and identity-coordinate control | Nontrivial parameter effect and downstream evidence; current separate-paper case is weak |
| WFT | Incremental benefit of verified operator constraints | Identifiable operator objective, symmetry/coarsening certificates, matched Laplacian ablation, held resolution and amortized cost | Implemented/evaluated claimed constraints, frozen-transfer study and novelty |
| WPINN | Verified-structure contribution or distinctive failure/identifiability finding | Full coefficients/support, conditioning/quadrature diagnostics, all rollout failures, whole-trajectory splits, qualified WSINDy | Valid beneficial structure, strong controls, complete failure-aware inference |
| CWLNN | Sparse routing accuracy/cost frontier or meaningful routing limitation | Preprocessing and inference timers, all routing budgets, receptive-field controls, permutation/topology tests | Fair cost frontier, trained scope if claimed, broader workloads |
| Ultron | Verified capability selection with an actual routing contribution | Tool checkpoints, shared-access proof, family-level completion/cost, rejected/failed tasks, verifier separation receipt | New task families/types, full costs, trustworthy external verification and focused novelty |

Existing materials map to these folders but do not satisfy all gates: shared draft in `docs/execution/development-v2/RESEARCH_DRAFT.md`; source under `src/`; generated figure and CSV tables in `docs/execution/development-v2/`; configs and raw runs already present; dependency locks available. There is no project LICENSE file in the audited authored repository; `pyproject.toml` names Apache-2.0 while the license inventory calls that a placeholder. Record the owner's actual licensing choice before distribution. This is an observed package gap, not a legal opinion.

Independent replication and confirmation are different package claims. Do not fill in an external person's identity/signature or certify a private holdout from this workspace. arXiv readiness is a manuscript-and-evidence judgment; peer-review readiness additionally depends on a sufficiently strong contribution and the chosen venue. Neither follows from passing tests or producing a tarball.
