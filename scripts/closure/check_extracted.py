"""Fresh-environment package checks, preserving each exit code and log."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--python',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=args.root.resolve(); python=args.python.resolve(); out=args.output.resolve()
    # Keep venv executable's path rather than resolving its interpreter symlink.
    python=args.python.absolute()
    out.mkdir(parents=True,exist_ok=False)
    env=dict(os.environ); env.pop('PYTHONPATH',None)
    env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONNOUSERSITE='1')
    commands=[('install',[str(python),'-m','pip','install','--no-deps','--no-build-isolation','-e','.']),
              ('dependencies',[str(python),'-m','pip','check']),
              ('environment',[str(python),'-c','import sys,platform,world_series; import importlib.metadata as m; print(sys.prefix); print(sys.base_prefix); print(world_series.__file__); print(platform.platform()); print({p:m.version(p) for p in ["numpy","scipy","torch","pytest"]})']),
              ('tests',[str(python),'-m','pytest','-q']),
              ('doctor',[str(python),'-m','world_series','doctor']),
              ('analysis',[str(python),'scripts/analyze_development.py']),
              ('artifact_audit',[str(python),'scripts/audit_development.py'])]
    report_dir=root/'docs/execution/development-v2'
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in report_dir.iterdir() if p.is_file()}
    receipts=[]
    for label,argv in commands:
        started=time.perf_counter()
        result=subprocess.run(argv,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        path=out/f'{label}.log'; path.write_text(result.stdout)
        row={'step':label,'argv':argv,'cwd':str(root),'exit_code':result.returncode,
             'seconds':time.perf_counter()-started,'log':path.name,'log_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        receipts.append(row)
        print(json.dumps({'step':label,'exit_code':result.returncode}),flush=True)
        (out/'progress.json').write_text(json.dumps(receipts,indent=2))
    after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in report_dir.iterdir() if p.is_file()}
    result={'root':str(root),'python':str(python),'platform':platform.platform(),'commands':receipts,
            'existing_report_changes':[name for name in before if before[name]!=after.get(name)],
            'report_hashes_before':before,'report_hashes_after':after,
            'all_commands_passed':all(r['exit_code']==0 for r in receipts),
            'scope':'Fresh dependency environment on same host; installation, tests and original analysis/audit. Not all full experiments or independent scientific replication.'}
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'all_commands_passed':result['all_commands_passed'],'existing_report_changes':result['existing_report_changes']}))


if __name__=='__main__': main()
