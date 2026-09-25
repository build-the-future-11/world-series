# World Series v0.1

Installable research workbench for nine independently testable projects under shared contracts.

## Current status — private review export, 25 September 2026

The repository now includes the original 80-run development matrix plus
causal Q-APEN lifecycle, trained WCODE, constrained WFT, structured WPINN and
conditional CWLNN studies. These remain development evidence, with negative
findings and all failed trials preserved. CWLNN's learned routing shows no net
speed/accuracy benefit; WPINN's incomplete primary aggregates remain incomplete.

See the [finite closure registry](https://github.com/Build-the-future12/world-series-research-records/blob/main/RESEARCH_CLOSURE/REGISTRY.json), [closure report](https://github.com/Build-the-future12/world-series-research-records/blob/main/RESEARCH_CLOSURE/FINAL_REPORT.md), and [claims index](results/claim_index.json). The compiled shared manuscript is in `paper/`.

See the [current paper audit](docs/PAPER_AUDIT.md),
[proposal-to-implementation map](docs/closure/PROPOSAL_IMPLEMENTATION_MAP.md),
[active checklist](docs/closure/CHECKLIST_STATUS.json), and
[working manuscript](paper/preprint.md).
No submission-ready paper or independent confirmation is claimed.
Historical numerical source commits are recorded in each campaign; use those
versions for exact replay instead of running every old audit against latest code.

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

**This repository is an implementation workbench.** Original project proposals are preserved in `provenance/original-proposals/`; the wider planning pack lives in `../world_series_cursor_pack/` (reconstructed from `WORLD_SERIES_COMPLETE_BLUEPRINT.md` because `WORLD_SERIES_CURSOR_PACK.zip` was not present). Planning validators are **not** scientific evidence.

See [the final release report](FINAL_RELEASE_REPORT.md) and [clone, evidence download and reproduction instructions](docs/RELEASE_REPRODUCIBILITY.md). A source-only clone does not include raw campaigns.

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

## Complete local review package

The builder uses only repository-relative inputs, includes all campaigns/runs
(including failed and interrupted receipts), and preserves original external
source evidence under `provenance/`. It excludes environments and external
Celo2 weights; use the pinned fetch provenance for those weights. License and
submission approval remain unresolved, so this is a local review artifact.

```bash
python scripts/build_delivery.py --output deliveries/FRESH_DIRECTORY
python scripts/verify_delivery.py deliveries/FRESH_DIRECTORY --extract FRESH_EXTRACT_DIRECTORY
```

Outputs must be fresh. Archive integrity and extraction do not replace clean
experimental reproduction or scientific review. Historical absolute paths in
immutable receipts are provenance fields, not input requirements of the builder.

## Results and limitations

The current manuscript reports bounded, internally checked development results.
Several methods fail to improve strong controls; failure-affected means remain
incomplete. No general method advantage or independent confirmation is established.
The raw evidence archive retains failed and interrupted outcomes.

## Citation

For private review, identify this workbench by repository URL and exact commit
SHA, and cite the actual primary sources listed in `paper/preprint.md`.
Human authorship and a publication citation have not been finalized, so no
invented author list or publication identifier is supplied.

## License

Distribution terms remain unapproved; see [LICENSE.md](LICENSE.md).
This private export does not grant an open-source license.
