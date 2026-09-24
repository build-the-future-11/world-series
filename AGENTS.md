# AGENTS.md — World Series immutable guardrails

These rules apply to every coding agent working in this program.

## Identity and honesty
- The planning pack is not an implemented model repository.
- Do not fabricate metrics, citations, charts, or “passing” scientific outcomes.
- Keep software readiness separate from research outcome (`NOT_SUPPORTED` / `INCONCLUSIVE` are valid).
- Do not mark a task complete because intended files exist; require tests and real evidence.
- Confirmation remains `DRAFT_NOT_AUTHORIZED` until a frozen protocol exists outside the development agent.

## Provenance and safety
- Treat existing APEN/PEN, Fabric-Induced Memory, and other research repositories as protected.
- Reuse only reviewed code with recorded revision/hash, license, and compatibility test.
- Do not delete duplicates, run destructive cleanup, reset user changes, migrate repos, or overwrite lockfiles without reconciliation.
- Keep planning provenance separate from execution evidence.
- Do not push remotely, deploy, publish, purchase compute, send outreach, or launch live trading.

## Execution policy
- Default to one numerical worker; nine projects ≠ nine simultaneous training jobs.
- CPU reference paths first; accelerator paths must declare device, dtype, and fallback.
- Set explicit conservative limits before allocation; memory monitors are advisory.
- No Python `eval`/`exec` for the synthesis DSL; no shell/filesystem/network in the DSL.
- Unimplemented capabilities return explicit unsupported/not-run states — never mock successes as research evidence.
- Preserve interrupted/failed runs; do not overwrite failure receipts with a later success under the same run ID.

## Evidence vocabulary
Use only: SPECIFIED, IMPLEMENTED, SMOKE_PASSED, BENCHMARKED, SUPPORTED, NOT_SUPPORTED,
INCONCLUSIVE, BLOCKED, NOT_RUN, INVALIDATED. Link claims to raw artifacts and scope.
