#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
SEEDS="${SEEDS:-0 1 2}"
PROJECTS="${PROJECTS:-qlearn qapen qwipii wcode wpinn ultron}"
mkdir -p experiments/multiseed
for p in $PROJECTS; do
  for s in $SEEDS; do
    cfg="configs/${p}/dev.yaml"
    # override seed via temp config
    python - << PY
import yaml, pathlib
cfg=yaml.safe_load(pathlib.Path("$cfg").read_text())
cfg["seed"]=int("$s")
cfg["experiment"]="dev_multiseed"
path=pathlib.Path("experiments/multiseed/${p}_seed${s}.yaml")
path.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(path)
PY
    python -m world_series run --config "experiments/multiseed/${p}_seed${s}.yaml" | tee "experiments/multiseed/${p}_seed${s}.out.json"
  done
done
python scripts/aggregate_multiseed.py
