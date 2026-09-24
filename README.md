# World Series v0.1

Installable research workbench for nine independently testable projects under shared contracts.

## Current status — 24 September 2026

The bounded development execution now includes 80 main run receipts across all
nine modules, natural binary-digit tasks, an official pretrained Celo2 comparison,
and a discrete action prototype. The artifact audit passes; results remain
developmental and include negative findings and 17 failed polynomial rollouts.
See [current status](docs/execution/development-v2/CURRENT_STATUS.md),
[complete results](docs/execution/development-v2/RESULTS.md),
[protocol](docs/execution/development-v2/PROTOCOL.md), and
[working manuscript](docs/execution/development-v2/RESEARCH_DRAFT.md).
The original September 22 reports are historical, not the current evidence view.

Run the declared matrices serially from this directory, using a spacious local
temporary directory and a fresh output path for changed source or configs:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/run_development.py --plan configs/development-v2.json --output campaigns/development-v2
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/run_development.py --plan configs/natural-digits-v1.json --output campaigns/natural-digits-v1
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/run_development.py --plan configs/discrete-malis-v1.json --output campaigns/discrete-malis-v1
.venv/bin/python scripts/analyze_development.py
.venv/bin/python scripts/audit_development.py
.venv/bin/python scripts/refresh_status.py
```

Completed-cell resume verifies hashes; it does not resume halfway through a
meta-training trial. Celo2 uses a separate environment and pinned external files:
see [provenance](docs/execution/development-v2/CELO2_PROVENANCE.json).
Independent confirmation requires the prepared
[external evaluation handoff](docs/execution/development-v2/INDEPENDENT_EVALUATION_HANDOFF.md).

**This repository is an implementation workbench.** Planning provenance lives in `../world_series_cursor_pack/` (reconstructed from `WORLD_SERIES_COMPLETE_BLUEPRINT.md` because `WORLD_SERIES_CURSOR_PACK.zip` was not present). Planning validators are **not** scientific evidence.

## Environment (locked)

- Python **3.12.14** via `.venv`
- See `requirements.lock.txt` and `docs/execution/CORE01_INVENTORY.md`
- CPU float64 is the reference path; MPS is available but optional

```bash
cd world-series
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock.txt
pip install -e ".[dev]"
```

## Tested commands

```bash
python -m world_series doctor
python -m world_series validate-config configs/qlearn/smoke.yaml
python -m world_series run --config configs/qlearn/smoke.yaml
python -m world_series compare --protocol experiments/registry.json --split dev
python -m world_series report --run-id REAL_RUN_ID
python -m world_series smoke-all
python -m world_series demo --project qwipii
python -m pytest tests -q
```

Invalid config rejection:

```bash
python -m world_series validate-config configs/qlearn/invalid.yaml   # exits non-zero
```

## Layout

- `src/world_series/` — package (`core`, `data`, `evaluation`, nine namespaces)
- `configs/{project}/smoke.yaml` — tiny CPU smoke configs
- `runs/{run_id}/` — immutable manifests, events, metrics, artifacts
- `experiments/registry.json` — protocols remain `DRAFT_NOT_AUTHORIZED`
- `docs/exposition/` — status table, claims ledger, limitations, demos
- `docs/execution/development-v2/` — current protocol, tables, figures, audits and draft
- `campaigns/` — local per-cell receipts, source/config identities and replay outputs
- `data/optdigits/` — attributed UCI data and file hashes

## Evidence policy

Software readiness ≠ research outcome. Smoke success does **not** mean `SUPPORTED`. Confirmation stays `DRAFT_NOT_AUTHORIZED` until an external frozen protocol exists. See `docs/EXPERIMENT_PROTOCOL.md` in the planning pack.
