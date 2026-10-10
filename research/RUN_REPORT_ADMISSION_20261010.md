# Run report admission contract — 10 October 2026

## Scope and preserved history

This prospective engineering change starts from PR #4 at
`30fb16b21b9563b8390530db8c17ea256ec386de`. Its complete quantizer,
numerical, checkpoint and canonical-state history is retained. PR #1 advanced
separately to `62d6e6cb9aa95bbe16eeb0769c9e3f40b82a2ba0`; its five strict
JSON implementation/test/documentation paths will be combined explicitly,
preserving their provenance instead of presenting those existing fixes as new.
The previous canonical state is copied byte for byte to
`research/state_snapshots/REPORT_ADMISSION_PARENT_30fb16b.json`.

The paper, claim index, frozen protocols, campaign outcomes, dependency lock
and release attestations are unchanged. Historical campaigns require their
recorded source/environment. Confirmation remains `DRAFT_NOT_AUTHORIZED`.
No model equation, optimization rule, metric or scientific hypothesis changes.

## Reproducible engineering failure and hypothesis

The public `load_run` / `report` path accepts conflicting manifest/metric
snapshots, ambiguous or nonfinite JSON, a foreign run identity, and altered or
missing hash-bound raw artifacts. Consequently a report can display an
aggregate whose retained evidence no longer supports its recorded identity.
Run-id traversal can also select evidence outside the configured run root.

The falsifiable engineering prediction is that the same public report path
will reject each independently constructed corruption with a structured
verification error, before writing a derived report, while genuine positive,
negative, failed and interrupted receipts remain readable and byte-unchanged.

## Admission rules and compatibility

- Read strict, unambiguous, finite JSON objects for the manifest, metrics and
  every nonblank event. Validate the run identity and status; preserve the
  distinction between execution success and a negative research outcome.
- Require canonical structural equality of the manifest metric snapshot and
  `metrics.json`. A successful receipt needs the metrics file; a failed or
  interrupted receipt may have no metrics if its manifest snapshot is empty.
- Recheck every embedded `{path, sha256}` or full `ArtifactRef` mapping in
  metrics/events, including producer identity, confined paths and exact bytes.
  These checks do not certify unreferenced files or reconstruct model outputs.
- Expose verification scope in the report, including the number of bound
  artifact files checked and the number of other artifact files for which
  there is no recorded hash. A consistent old receipt remains readable;
  corruption is not silently repaired or reclassified.
- Evidence reads and report publication do not modify raw files. Existing
  report paths are not truncated on a failed read or serialization step.

## Bounded execution and acceptance

Run corruption regressions against the parent, then the combined implementation
and existing full correctness suite on CPU with one numerical thread. At most
one WFT smoke fixture may exercise the real CLI and report boundary. No new
training campaign, protected split, external model, paid compute or scientific
reanalysis is part of this change. Retain all failures and review findings.
Independent source review and exact GitHub source verification precede closure
of the engineering change; scientific completion is not asserted.
