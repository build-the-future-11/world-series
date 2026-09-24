# Experimental protocol and claim policy

## Three separate questions

1. Does the implementation match the proposed mechanism?
2. Does that mechanism improve the preregistered task under matched resources?
3. How broadly does the result generalize?

A passing test addresses the first question. A benchmark addresses a specified part of the second. Neither automatically answers the third. No statement of universal learning, quantum advantage, infinite execution, P=NP or ASI is an admissible v0.1 result.

## Preserve study identities

The archived `PEN_SOURCE_IDENTITY_RECONCILIATION_2026-09-18.md` defines APEN as the family and PEN as a fixed precursor. It preserves mixed/negative memory evidence and prohibits rescue tuning under the historical identity. Keep that identity immutable. World Series uses `WS-{PROJECT}-20260922-v0.1-dev` for development proposals and a separately frozen confirmation protocol. Do not reuse visible historical outcome packets as blind confirmation. The new World-FIM algebra study is distinct from Fabric-Induced Memory.

## Split unit and leakage control

Split by generative task family or source object, not by adjacent rows. MALIS: separate whole optimizee/task distributions. Q-APEN: separate complete streams, regime schedules and parameter draws. QWIPII: split canonical problem orbits so equivalent transforms cannot straddle train and test. WCode: split source program families after normalization, not examples from one program. WFIM: split compositional templates and lengths. WFT/CWLNN: split graph instances, generator parameters and selected graph sizes. WPINN: split initial conditions, trajectories and physical parameters. Ultron: split full research tasks and templates.

Training data fits parameters. Development data chooses architecture and hyperparameters. A protected confirmation set is generated/committed by an evaluator outside the development agent after the protocol is frozen; its seed/answers are not in agent prompts. Record its manifest hash. Evaluate a frozen candidate and baselines once per declared protocol. Any post-confirmation revision is a new study version, not a silent retry. Do not promise secrecy if the same agent can read the evaluator's filesystem.

## What is frozen before confirmation

Record the exact code/config/environment hashes, task generator, inclusion/exclusion criteria, primary metric, effect direction, practical effect threshold, seeds, sample size, failure handling, compute accounting, baseline tuning budget, stopping rule, uncertainty procedure and claim wording. Do not select a practical threshold after viewing confirmation effects. Until these are specified the registry status is `DRAFT_NOT_AUTHORIZED`, not preregistered.

Initial development plan: three paired seeds for debugging, then five or more paired runs over multiple independent task instances if resources permit. These are planning defaults, not a promise that five seeds yields adequate power. Use development variance to design a feasible confirmation sample size. Report noisy or underpowered outcomes as inconclusive. Family diversity often matters more than many seeds of one task.

## Comparators and resources

Use one matched simple baseline, one nearest mechanism baseline and one ablation as the minimum. Share input information, data splits, stopping budgets and tuning opportunities. Include all candidate overhead: graph construction, search, gating, simulator birth/warmup, verification and preprocessing. Separate one-time meta-training/pretraining from per-task inference or adaptation. Report amortization assumptions and break-even task count rather than pretending pretraining was free.

Resource equality can mean different things. Predefine the primary comparison: wall-clock on identical hardware, simulator calls, candidate evaluations, or training FLOPs estimated by a stated method. Report secondary comparisons rather than choosing whichever budget makes the candidate look best. Equal parameters alone is not equal compute. Timeout/divergence counts must remain in the denominator.

## Statistics

Use paired differences on the same tasks/seeds. For heterogeneous families report family-level effects and an aggregate with a documented weighting. Bootstrap at the independent task/trajectory level, nesting seed resampling only where justified; do not treat 1,000 correlated timesteps as 1,000 independent trials. Report intervals, all raw trial summaries, medians and failures. For suites, robust aggregate summaries can supplement—not replace—per-family outcomes [R40]. Avoid a single best-seed chart.

A proposed development promotion rule is: no correctness regression; practical improvement over the strongest eligible matched baseline; and an uncertainty interval consistent with the declared effect. This is a policy to freeze before confirmation, not a universal significance recipe. Nine projects and many endpoints create multiplicity: identify nine primaries in advance, distinguish exploratory results, and use an explicitly chosen correction or avoid joint significance claims.

## Mechanism ablations

Remove only the claimed mechanism while keeping information access and reasonable model capacity comparable. Replace learned memory writes with random/recent writes; replace adaptive worlds with fixed ensembles; replace verified quotienting with ranking-only; compare learned algebra transport to the identical fixed algebra; remove spectral constraints individually; compare learned routing with fixed routing. Do not compare the full model against an intentionally crippled straw man.

## Evidence states

`SPECIFIED`: design and tests written, no implementation implied.
`IMPLEMENTED`: code path exists and has been reviewed.
`SMOKE_PASSED`: tiny correctness/plumbing checks actually executed.
`BENCHMARKED`: matched declared comparisons actually executed.
`SUPPORTED`, `NOT_SUPPORTED`, `INCONCLUSIVE`: bounded interpretation of a frozen primary result.
`BLOCKED`, `NOT_RUN`, `INVALIDATED`: explicit absence/failure/protocol violation.

Each claim links to immutable raw evidence and a specific scope. A software build may pass with `NOT_SUPPORTED`. Never make CI demand a positive research finding. Publication readiness also needs independent review, literature coverage, reproducibility, licenses and truthful reporting; a Sunday demo does not establish all of these.


---
