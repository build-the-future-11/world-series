#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
python -m world_series doctor
python -m pytest tests -q
python -m world_series smoke-all
