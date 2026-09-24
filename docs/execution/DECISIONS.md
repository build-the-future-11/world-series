# Decision log

- 2026-09-22: ZIP pack absent → reconstruct planning pack from blueprint; keep separate from `world-series/` execution.
- 2026-09-22: Use Python 3.12.14 venv (not host 3.14) per pack preference; lock with pip freeze.
- 2026-09-22: Single monorepo package `world_series`; leave empty QL/QAPEN/... dirs untouched.
- 2026-09-22: CPU float64 reference; MPS probed but not required for smoke.
- 2026-09-22: Ultron registers real adapters only; verifier tagged PLUMBING_ONLY.
