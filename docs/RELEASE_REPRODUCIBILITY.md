# Clone, evidence download and reproduction

The source clone contains implementation, tests, protocols, manuscript and
selected reports. Raw campaigns, checkpoints and run receipts are deliberately
kept out of ordinary Git history. Obtain the hashed review archive from the
GitHub Release assets (historically `review-20260925`: `world-series-review.tar.gz`,
`manifest.json`, `receipt.json`). The archive is an engineering evidence bundle;
scientific claims remain bounded development findings.

**License:** Apache-2.0 for original source (`LICENSE`, `NOTICE`). Third-party
terms: `THIRD_PARTY.md`.

## Source and evidence

```sh
gh repo clone build-the-future-11/world-series
cd world-series
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m pip check
.venv/bin/python -m pytest tests -q
.venv/bin/python -m world_series doctor
.venv/bin/python scripts/verify_headline_claims.py
gh release download review-20260925 --dir deliveries/download
.venv/bin/python scripts/verify_delivery.py deliveries/download --extract .work-tmp/download-extracted
.venv/bin/python scripts/restore_delivery.py .work-tmp/download-extracted --output .work-tmp/restored
```

Output directories must not already exist. `restore_delivery.py` preserves the
archive source and Git history. Run historical audits with their recorded source
revision; latest code is not a substitute for a frozen historical environment.
Collection audit material lives in
`build-the-future-11/world-series-research-records` (clone as parent and place
this repo at `world-series/` when running collection-wide checks).

## Safe same-host review

From a restored checkout with the locked dependency environment available:

```sh
PYTHON=/absolute/path/to/world-series/.venv/bin/python ./reproduce.sh --output .work-tmp/FRESH_REVIEW
```

This builds/extracts a fresh archive, runs the full test suite and original
analysis/artifact checks, and reloads WFIM predictions. It uses the caller's
installed dependencies. It is not independent-person reproduction and does not
retrain all nine studies. Add `--full-wfim` only for the recorded finite training
replay. Per-headline commands: `docs/HEADLINE_REPRODUCTION.md`.

Celo2 weights and upstream checkout are not redistributed. Fetch the exact
revision and weight URL/hash in `CELO2_PROVENANCE.json` under the development
record. UCI optdigits attribution and hashes remain in `data/optdigits/`.
No API key or `.env` file is required for CPU reference use.

## Paper build

Install Pandoc and Tectonic, then run from `paper/`:

```sh
pandoc preprint.md --standalone -V geometry:margin=0.85in -V fontsize=11pt -V papersize=a4 -o preprint.tex
tectonic preprint.tex
```

Human authorship attestation: `docs/AUTHORSHIP.md`. Open-source go-live:
`docs/OPEN_SOURCE_GO_LIVE.md`.

## Static analysis scope

The repository has no configured type checker. Existing Ruff findings are
retained in release receipts rather than applying mass formatting to frozen
source files. CI checks fatal syntax/undefined-name rules plus all tests; it
does not claim full lint cleanliness or scientific validation.

## QAPEN codebook replay

`FrozenQuantizer.centers` exposes a fresh, read-only float64 array view for each
access. Changing an exposed view's shape or dtype cannot change the retained
codebook or route a context to a different code. The retained representation is
immutable bytes plus shape, so both data and array metadata remain isolated.

Pickle loading validates and freezes the codebook again, including the earlier
`centers` and `_centers` array-state layouts. Protocols 4 and 5, pending-prediction
checkpoint continuation, optimizer parameter identity, memory and RNG receipts
are covered with constructed regression fixtures. This verifies compatibility
of those state layouts, not a new replay of historical outcome checkpoints.
Historical campaigns still require their recorded source and environment.

The source-bound engineering record is
`research/ENGINEERING_CODEBOOK_REPLAY_20261010.json`. Existing scientific
dispositions and confirmation boundaries remain in force.
