#!/usr/bin/env python3
"""Create a local, hash-indexed independent-review bundle; never upload it."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
from world_series.core.identity import source_identity

ROOT=Path(__file__).resolve().parents[1]

def main(output):
    output.mkdir(parents=True,exist_ok=False)
    files={}
    bundle=output/'source.bundle'
    subprocess.run(['git','bundle','create',str(bundle.resolve()),'--all'],cwd=ROOT,check=True)
    files['source.bundle']=bundle
    for folder in ['src','tests','scripts','configs','docs','data','experiments']:
        for path in (ROOT/folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix not in {'.pyc'}:
                files['repository/'+str(path.relative_to(ROOT))]=path
    for filename in ['README.md','AGENTS.md','.gitignore','pyproject.toml','requirements.lock.txt']:
        files['repository/'+filename]=ROOT/filename
    for name in ['development-v2','natural-digits-v1','discrete-malis-v1','natural-digits-sensitivity-v1']:
        directory=ROOT/'campaigns'/name
        summary=json.loads((directory/'summary.json').read_text())
        if not summary['complete']:raise RuntimeError(f'Incomplete required campaign {name}')
        for receipt in summary['cells']:
            run=ROOT/'runs'/receipt['run_id']
            for relative,expected in receipt['file_hashes'].items():
                path=run/relative
                if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise RuntimeError(f'Changed artifact {path}')
                files['repository/runs/'+receipt['run_id']+'/'+relative]=path
    for name in ['development-v2','natural-digits-v1','discrete-malis-v1','natural-digits-sensitivity-v1','celo2','meta-training-replay-v1','falsify-20260924']:
        for path in (ROOT/'campaigns'/name).glob('*.json'):
            files['repository/campaigns/'+name+'/'+path.name]=path
    replay=json.loads((ROOT/'campaigns/meta-training-replay-v1/summary.json').read_text())
    if not replay['all_exact']:raise RuntimeError('Original full training replay is incomplete or mismatched')
    original=ROOT/'runs/20260923T231444_deaee7ec'
    for path in original.rglob('*'):
        if path.is_file():files['repository/runs/'+original.name+'/'+str(path.relative_to(original))]=path
    frozen=Path('/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-candidate-20260923-v2')
    for name in ['manifest.json','source.tar.gz']:files['original-frozen-source/'+name]=frozen/name
    prior_analysis=Path('/Volumes/PRO-BLADE/.portfolio/verification/WS-neural-analysis-20260923')
    for path in prior_analysis.rglob('*'):
        if path.is_file():files['original-analysis/'+str(path.relative_to(prior_analysis))]=path
    manifest={'scope':'Local review package. No independent verdict, signature, secret holdout or publication claim.',
              'source':source_identity(ROOT),
              'files':{name:{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
                       for name,path in sorted(files.items())},
              'external_weights':'Celo2 checkpoint is not redistributed; fetch pinned revision from provenance.'}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=output/'world-series-review.tar.gz'
    with tarfile.open(archive,'w:gz',compresslevel=6) as tar:
        tar.add(output/'manifest.json',arcname='manifest.json',recursive=False)
        for name,path in sorted(files.items()):tar.add(path,arcname=name,recursive=False)
    receipt={'archive':str(archive),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
             'bytes':archive.stat().st_size,'file_count':len(files),'source':manifest['source']}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
