#!/usr/bin/env python3
"""Write new falsification receipts without replacing historical outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
from world_series.core.identity import source_identity
from world_series.evaluation.falsify import run_all_controls

ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    historical=ROOT/'experiments/falsification_results.json'
    before=hashlib.sha256(historical.read_bytes()).hexdigest()
    controls=run_all_controls(args.seed)
    result={'seed':args.seed,'controls':controls,'source':source_identity(ROOT),
            'historical_sha256_before':before,
            'historical_sha256_after':hashlib.sha256(historical.read_bytes()).hexdigest(),
            'passed_sanity':all(c['passed'] for c in controls),
            'scope':'Sanity checks; passing does not establish the hypotheses'}
    assert result['historical_sha256_after']==before
    (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed_sanity':result['passed_sanity'],'controls':len(controls),'historical_unchanged':True}))
    raise SystemExit(0 if result['passed_sanity'] else 1)
