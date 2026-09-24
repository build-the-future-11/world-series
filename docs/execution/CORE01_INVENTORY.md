# CORE-01 Inventory — 2026-09-22

## Workspace
- Opened path: `/Volumes/PRO-BLADE/World-Series`
- Planning pack: `world_series_cursor_pack/` (reconstructed from `WORLD_SERIES_COMPLETE_BLUEPRINT.md`; ZIP absent)
- Implementation workbench: `world-series/` (this directory)
- Empty placeholder dirs left untouched: QL, QAPEN, QWRIPII, WCNNCODE, WFIM, WFT, WPINN, CWLNN, Ultron
- Protected provenance: no APEN/PEN/FIM repos migrated or modified

## Environment
- Python: 3.12.14 (`/opt/homebrew/bin/python3.12`) via `.venv`
- Host default python3 was 3.14.7; selected 3.12 per pack preference
- Locked deps: see `requirements.lock.txt` (numpy 2.5.3, scipy 1.18.1, torch 2.14.0, PyYAML, pytest, hypothesis, ruff)
- Devices: Apple M4 arm64; MPS available=True; **CPU float64 is the reference path**
- RAM: 16 GiB; Disk free on PRO-BLADE: ~648 GiB
- Git: newly initialized in `world-series/` only; planning pack not a git submodule

## Planning checks (not implementation tests)
- `python3.12 tools/validate_pack.py` → PASS
- `python3.12 tools/check_math_reference.py` → PASS
- Evidence: `../world_series_cursor_pack/artifacts/planning_validation.txt`

## Decision
Least-disruptive path: new monorepo package `world_series` under `world-series/`; keep planning provenance separate; do not overwrite empty named folders or external research repos.
