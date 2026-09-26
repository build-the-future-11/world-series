# Third-party materials

This repository’s original World Series source is Apache-2.0 (see `LICENSE` and
`NOTICE`). Bundled or referenced third-party materials keep their own terms.

## Bundled data

| Material | Path | Terms | Notes |
|---|---|---|---|
| Optical Recognition of Handwritten Digits (UCI) | `data/optdigits/` | CC BY 4.0 | Alpaydin & Kaynak; DOI [10.24432/C50P49](https://doi.org/10.24432/C50P49). File hashes in `data/optdigits/provenance.json`. |

## Runtime / build dependencies (not vendored)

| Package | Typical license | Role |
|---|---|---|
| NumPy | BSD | arrays |
| SciPy | BSD | sparse/numerics |
| PyTorch | BSD-style | autograd |
| PyYAML | MIT | configs |
| pytest / hypothesis / ruff | BSD/MIT | development |

Exact pinned versions are in `requirements.lock.txt`.

## Optional / external comparators (not redistributed)

| Material | Provenance | Terms | Redistribution |
|---|---|---|---|
| Celo2 source | `docs/execution/development-v2/CELO2_PROVENANCE.json` | MIT with retained Google Apache-2.0 attribution | Fetch pinned commit yourself |
| Celo2 weights | same provenance file | No separate checkpoint license asserted upstream | Not published here; fetch pinned URL/hash locally |
| PySINDy 2.1.0 | WPINN qualification receipts | MIT | Install in the optional WPINN environment; not a core dependency |

## Historical imports

Read-only preserved proposals and legacy analysis under `provenance/` are
documented in `provenance/IMPORT_MANIFEST.json`. Treat absolute `original_path`
fields as provenance only.

## Trademark / naming

“World Series” here names this research workbench. No affiliation with Major
League Baseball or any sports trademark holder is claimed or implied.
