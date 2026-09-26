# Headline reproduction manifest

**Scope:** reconstruct or verify every manuscript headline from preserved
artifacts. This is release verification (E0), not new training and not
independent multi-lab replication.

**Path roots:**

- Implementation checkout: repository root of `world-series`
- Raw campaigns/runs: restore from the hashed review archive (Git clone alone is insufficient)
- Collection records (optional): sibling `world-series-research-records`

## A. Source-only checks (no archive)

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m pytest tests -q
.venv/bin/python -m world_series doctor
.venv/bin/python scripts/verify_headline_claims.py --claim-index results/claim_index.json
```

Expected: tests pass; claim-index analysis digests match local report files.

## B. Archive restore (required for raw campaigns)

Follow `docs/RELEASE_REPRODUCIBILITY.md` to download `review-20260925` (or the
current public release asset), verify, and restore. Then re-run section A inside
the restored tree.

## C. Per-headline artifact map

| Headline (paper §) | Claim id | Definitive report | Protocol | Reconstruction mode |
|---|---|---|---|---|
| QLearn AUC table (§4.1) | qlearn-bounded-results | `docs/closure/GATE_RESULTS.json` | `configs/natural-digits-v1.json` | analyze preserved campaign; optional full meta-training replay receipt |
| QAPEN NLL (§4.1) | qapen-bounded-results | `docs/closure/QAPEN_RESULTS.json` | `docs/closure/QAPEN_PROTOCOL.md` | analyze preserved lifecycle campaign |
| QWIPII expansions/time (§4.2) | qwipii-bounded-results | `docs/closure/QWIPII_LEARNED_AUDIT.json` | `campaigns/qwipii-learned-development-v1/protocol.json` | path replay from saved cells |
| WCODE cap24 (§4.2) | wcode-bounded-results | `docs/closure/WCODE_RESULTS.json` | `docs/closure/WCODE_PROTOCOL.md` | search audit over preserved receipts |
| WFIM MSE (§4.4) | wfim-bounded-results | `docs/closure/WFIM_LEARNING_AUDIT.json` | `campaigns/wfim-coordinate-development-v1/protocol.json` | checkpoint prediction replay (exact) |
| WFT error (§4.3) | wft-bounded-results | `docs/closure/WFT_RESULTS.json` | `docs/closure/WFT_PROTOCOL.md` | NumPy/SciPy reanalysis of saved fits |
| WPINN failures (§4.3) | wpinn-bounded-results | `docs/closure/WPINN_RESULTS.json` | `docs/closure/WPINN_PROTOCOL.md` | rollout/prediction replay; retain failures |
| CWLNN routing (§4.3) | cwlnn-bounded-results | `docs/closure/CWLNN_RESULTS.json` | `docs/closure/CWLNN_PROTOCOL.md` | isolated prediction/permutation replay |
| Ultron routing (§4.2–5) | ultron-bounded-results | `docs/closure/GATE_RESULTS.json` | `docs/execution/development-v2/PROTOCOL.md` | preserved development-v2 cells |

Machine-readable twin: `docs/HEADLINE_REPRODUCTION.json`.

## D. Paper build

```sh
cd paper
pandoc preprint.md --standalone -V geometry:margin=0.85in -V fontsize=11pt -V papersize=a4 -o preprint.tex
tectonic preprint.tex
```

## E. Explicit non-goals

- Retraining all nine studies from scratch is not required to publish the bounded report.
- Same-host replay ≠ independent confirmation.
- Celo2 weights must be fetched via `CELO2_PROVENANCE.json`; they are not in Git.
