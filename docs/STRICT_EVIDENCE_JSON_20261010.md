# Reject ambiguous configurations and nonfinite research evidence

## Demonstrated failure

17 of 18 new cases failed against the preceding revision; the valid control passed.

Inspected parent revision: `dbf580acc75a5d5650de74d55fbaab6b023f3374`.

## Implementation

Configuration loading now rejects duplicate JSON/YAML keys, boolean seeds and nonfinite values. Shared artifact, event, manifest and metric serialization encodes strict JSON before touching the destination, so malformed data cannot create or replace evidence. Valid JSON formatting and ordinary config identity remain unchanged.

## Verification

182 passed across the complete local tests collection.

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src python -m pytest -o addopts= -q tests
```

Hosted outcomes are recorded separately in the pull request and the dated execution register after exact-revision verification; local passes alone are not a hosted release gate.

## Preserved scientific boundary

Historical results, model code, budgets and hypotheses remain unchanged. These are execution and evidence contracts; no scientific campaign was run.

