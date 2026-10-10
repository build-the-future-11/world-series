# QAPEN transition budget admission — development record

The actual `CausalLifecycle` now admits the full operation cost of a prediction
or observation before changing retained state. A caller can raise an exhausted
budget and retry the same transition without duplicating partial optimizer,
memory or lifecycle effects.

## Failure and repair

Previously, `_charge` checked cost incrementally after earlier work had already
changed the model. A refused prediction could revive an expert, consume retrieval
randomness or update memory access counts. A refused observation could update
memory utility, train selected or warmup experts, promote/prune identities, or
partly train a new identity on replay. Invalid contexts also consumed budget
before rejection.

Prediction now validates context first, computes its exact complete cost, and
reuses the already chosen closest expert and memory-candidate list. Admission
precedes revival, retrieval RNG and access changes. Observation precomputes the
surviving warmup updates, selected-expert update, possible birth and replay cost
after deque eviction, and memory consolidation cost. Admission precedes model,
Adam, replay, memory-utility and lifecycle mutations. The existing actual charge
sites remain in place; this is not a production clone/rollback implementation.

The contract covers refusal because the operation budget is insufficient and
invalid-context admission. It does not claim arbitrary numerical exceptions
after successful admission are transactional.

## Evidence

All 12 new regression cases fail against the original causal source and pass
with the repair. They place a cap one unit below a reference transition's actual
cost, check complete retained state after rejection, then add exactly one unit
and compare the retry to uninterrupted execution. Full state includes model
tensors, Adam state, counters, pending prediction, replay, memory and events.

A separate old/new execution comparison covers 12 configurations and 192
artificial observations. Successful predictions, scores and complete state are
exactly equal, with nearest/random/recent retrieval, lifecycle and memory on/off.
The independent reviewer additionally instrumented actual charge calls over
three 48-observation traces: **288 successful transitions and 288 refused
retries**. Admission cost exactly matched actual charges, refusal changed no
NumPy/Torch RNG or retained state, and exact-budget retries matched the reference.
Those witnesses include births after the 32-record replay deque is full.

The proposal targets current PR 4 at
`b89d5709b6b43a41d89f88e3c0fa686c809596bf`, preserving its integrated strict
writers and full mass WFT implementation. The final causal source SHA-256 is
`1f3eff15b9a6e3baedf4ebd150c47d6fc4e938f2658e053e2d1fd9b0cfa26846`.
The full current-parent local suite passes **259 tests** with the existing
qlearn tensor-to-scalar warning retained. Critical static checks and the new
test's Ruff checks pass. Existing hosted CI is a separate integration gate.

The first repaired test attempt passed all nine direct admission cases, but
three trace fixtures incorrectly required a birth after only two consecutive
surprises. The fixture was corrected to three consecutive shocks; all 12 pass,
and all final fixtures also fail against the old implementation. A first parent
materialization used the wrong relative staging path; its 226-test run is old
parent evidence only. The corrected absolute-path materialization and 259-test
run are the accepted current-parent result. Failed attempts are retained.

## Research boundary

These are bounded artificial engineering tests on CPU. The nine architectures'
negative/incomplete findings and frozen campaigns are unchanged. Confirmation
remains `DRAFT_NOT_AUTHORIZED`; no protected evaluation, external dataset,
scientific training campaign, paid job, or model-promotion evidence was created.
The independent review expanded its artificial trace to 48 observations solely
to cover replay saturation; the original prospective local bound and this
separate reviewer scope are both recorded.

Reproduce from the repository root:

```bash
PYTHONPATH=src OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
python -m pytest -o addopts= -q tests
```

`research/ENGINEERING_BUDGET_ADMISSION_20261010.json` indexes before/after logs,
source identities, exact-equivalence results and the independent review receipt.
