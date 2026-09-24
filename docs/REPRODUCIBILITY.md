# REPRODUCIBILITY.md

## Environment
```bash
cd world-series
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock.txt
pip install -e ".[dev]"
```

## Canonical commands
```bash
./scripts/smoke.sh                 # doctor + pytest + smoke-all
./scripts/falsify.sh 0             # cheap falsification suite
SEEDS="0 1 2" PROJECTS="qlearn qapen qwipii wpinn ultron" ./scripts/dev_multiseed.sh
python -m world_series report --run-id <RUN_ID>
```

## What a run records
`runs/<run_id>/manifest.json` includes config hash, device, seed, split, budget, `source.content_hash`, nullable `git_head`, status, metrics path.

## Protocol status
`experiments/registry.json` entries are **DRAFT_NOT_AUTHORIZED**. Do not treat local development as confirmation.

## Negative results
Preserved in `experiments/falsification_results.json` and run metrics (do not delete `runs/`).
