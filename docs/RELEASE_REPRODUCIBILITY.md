# Private export and reproduction

The source clone contains implementation, tests, protocols, manuscript and
selected reports. Raw campaigns, checkpoints and run receipts are deliberately
kept out of ordinary Git history. The private `review-20260925` prerelease holds
`world-series-review.tar.gz`, `manifest.json` and `receipt.json`, including all
preserved campaigns, all runs and a Git bundle for historical replay. It is an
engineering review archive, not a scientific publication or open-source release.

## Source and evidence

```sh
gh repo clone Build-the-future12/world-series
cd world-series
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m pip check
.venv/bin/python -m pytest tests -q
.venv/bin/python -m world_series doctor
gh release download review-20260925 --dir deliveries/download
.venv/bin/python scripts/verify_delivery.py deliveries/download --extract .work-tmp/download-extracted
.venv/bin/python scripts/restore_delivery.py .work-tmp/download-extracted --output .work-tmp/restored
```

Output directories must not already exist. `restore_delivery.py` preserves the
archive source and Git history. Run historical audits with their recorded source
revision; latest code is not a substitute for a frozen historical environment.
The collection audit and planning material is a separate private repository:
`Build-the-future12/world-series-research-records`. Clone it as the parent
folder and place the implementation clone at `world-series/` when running its
collection-wide checks.

## Safe same-host review

From a restored checkout with the locked dependency environment available:

```sh
PYTHON=/absolute/path/to/world-series/.venv/bin/python ./reproduce.sh --output .work-tmp/FRESH_REVIEW
```

This builds/extracts a fresh archive, runs the full test suite and original
analysis/artifact checks, and reloads WFIM predictions. It uses the caller's
installed dependencies. It is not independent-person reproduction and does not
retrain all nine studies. Add `--full-wfim` only for the recorded finite training
replay. Other full historical replay commands and isolated dependency locks are
in `docs/closure/` and `docs/execution/development-v2/`.

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

The current manuscript corrects the WFT evaluation/transfer denominator and
teacher description. Frozen protocols and historical snapshots remain unchanged.
Named authors, approved distribution terms, complete closest-work review and
human scientific responsibility are still outstanding for public publication.

## Static analysis scope

The repository has no configured type checker. Existing Ruff findings are
retained in the release receipts rather than applying mass formatting to frozen
source files. CI checks fatal syntax/undefined-name rules plus all tests; it
does not claim full lint cleanliness or scientific validation.
