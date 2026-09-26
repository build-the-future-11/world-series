# World Series v0.1

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/build-the-future-11/world-series?include_prereleases)](https://github.com/build-the-future-11/world-series/releases/tag/v0.1.0-oss)
[![CI](https://github.com/build-the-future-11/world-series/actions/workflows/ci.yml/badge.svg)](https://github.com/build-the-future-11/world-series/actions/workflows/ci.yml)

Installable research workbench for nine independently testable projects under shared contracts.

**License:** Apache-2.0 — see [`LICENSE`](LICENSE), [`NOTICE`](NOTICE), [`THIRD_PARTY.md`](THIRD_PARTY.md).
**Release:** [v0.1.0-oss](https://github.com/build-the-future-11/world-series/releases/tag/v0.1.0-oss) (includes hashed review archive).
**arXiv package (ready to upload):** [`paper/arxiv/`](paper/arxiv/).

## Status — open-source packaging, 26 September 2026

Bounded development evidence across nine modules, with negative and incomplete
aggregates preserved. This is a mechanism-verification / negative-results
workbench, **not** a claim that the nine original architectures or independent
confirmation are complete.

See:

- [Open-source go-live checklist](docs/OPEN_SOURCE_GO_LIVE.md)
- [Authorship attestation](docs/AUTHORSHIP.md)
- [Headline reproduction](docs/HEADLINE_REPRODUCTION.md)
- [Claims index](results/claim_index.json)
- [Manuscript](paper/preprint.md)
- Collection [closure registry](https://github.com/build-the-future-11/world-series-research-records/blob/main/RESEARCH_CLOSURE/REGISTRY.json)

## Environment (locked)

- Python **3.12** via `.venv`
- See `requirements.lock.txt`

```bash
cd world-series
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock.txt
pip install -e ".[dev]"
python -m pytest tests -q
python -m world_series doctor
python scripts/verify_headline_claims.py
```

## Evidence archive

A source-only clone does **not** include raw campaigns/runs. Download the hashed
review archive and restore it using
[docs/RELEASE_REPRODUCIBILITY.md](docs/RELEASE_REPRODUCIBILITY.md).

Celo2 weights are external; see
[CELO2_PROVENANCE.json](docs/execution/development-v2/CELO2_PROVENANCE.json).

## Layout

- `src/world_series/` — package (`core`, `data`, `evaluation`, nine namespaces)
- `configs/` — smoke and study plans
- `campaigns/`, `runs/` — present after archive restore
- `docs/closure/` — protocols and result reports
- `paper/` — shared bounded manuscript
- `data/optdigits/` — UCI data (CC BY 4.0)

## Citation

Cite the repository URL and exact commit SHA, and the primary sources listed in
`paper/preprint.md`. Author: Ryan.
