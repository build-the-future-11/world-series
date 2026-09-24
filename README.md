# World Series v0.1

Installable research workbench for nine independently testable projects under shared contracts.

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

## Evidence policy

Software readiness ≠ research outcome. Smoke success does **not** mean `SUPPORTED`. Confirmation stays `DRAFT_NOT_AUTHORIZED` until an external frozen protocol exists. See `docs/EXPERIMENT_PROTOCOL.md` in the planning pack.
