#!/usr/bin/env python3
"""Reproduce an isolated review package without installing into the caller's env."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from build_delivery import main as build
from verify_delivery import main as verify


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True,help='Fresh output directory outside included source folders')
    parser.add_argument('--full-wfim',action='store_true',help='Also replay all 80 historical WFIM training/selection runs')
    args=parser.parse_args()
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    build(out/'delivery')
    verify(out/'delivery',out/'extracted')
    root=out/'extracted/repository'
    scratch=out/'scratch';scratch.mkdir()
    env=dict(os.environ, PYTHONNOUSERSITE='1', PYTHONPATH=str(root/'src'),
             OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
             TMPDIR=str(scratch),MPLCONFIGDIR=str(scratch),XDG_CACHE_HOME=str(scratch))
    commands=[('dependencies',['-m','pip','check']),
              ('tests',['-m','pytest','tests','-q','--basetemp',str(scratch/'pytest')]),
              ('doctor',['-m','world_series','doctor']),
              ('analysis',['scripts/analyze_development.py']),
              ('artifact_audit',['scripts/audit_development.py']),
              ('wfim_predictions',['scripts/closure/analyze_wfim_learning.py','--root',
                                   'campaigns/wfim-coordinate-development-v1','--output',str(out/'wfim_predictions.json')])]
    if args.full_wfim:
        commands.append(('wfim_training',['scripts/closure/replay_wfim_training.py','--root',
                                          'campaigns/wfim-coordinate-development-v1','--output',str(out/'wfim_training')]))
    receipts=[]
    for name,parts in commands:
        start=time.monotonic();log=out/f'{name}.log'
        with log.open('w') as handle:
            try:
                run=subprocess.run([sys.executable,*parts],cwd=root,env=env,stdout=handle,stderr=subprocess.STDOUT,timeout=1800)
                code=run.returncode
            except subprocess.TimeoutExpired:
                code=124
        receipts.append(dict(step=name,argv=[sys.executable,*parts],cwd=str(root),exit_code=code,
                             seconds=time.monotonic()-start,log=log.name,
                             log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
        result=dict(passed=all(r['exit_code']==0 for r in receipts),commands=receipts,
                    scope='Isolated archive source and preserved data using caller dependency environment; not independent replication or all nine full retrainings.')
        (out/'reproduction.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(receipts[-1]),flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__=='__main__':
    main()
