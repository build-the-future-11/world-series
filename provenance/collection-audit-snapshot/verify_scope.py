"""Inspect historical-source cache separately and verify preserved inputs."""
from pathlib import Path
import hashlib, json, sys
import numpy as np
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
REPO=ROOT/'world-series'
sys.path.insert(0,str(REPO/'src'))
from world_series.core.identity import source_identity

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
frozen=REPO/'.work-tmp/frozen-v1'
files=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
       for p in sorted(frozen.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
identity=source_identity(frozen)
assert identity['content_hash']=='6a0fa8d2eff817671edba7a1fc806928f46fadb2a2c10a72e7ffc39f1659b924'
snapshot={'role':'Historical source snapshot of the same nine projects, used by original QLearn replay; not a new project.',
          'source':identity,'files':files}
(OUT/'frozen_source_inventory.json').write_text(json.dumps(snapshot,indent=2)+'\n')
arrays=0
sources={n:np.loadtxt(REPO/'data/optdigits'/n,delimiter=',') for n in ['optdigits.tra','optdigits.tes']}
for campaign in ['natural-digits-v1','natural-digits-sensitivity-v1']:
    summary=json.loads((REPO/'campaigns'/campaign/'summary.json').read_text())
    for receipt in summary['cells']:
        folder=REPO/'runs'/receipt['run_id']/'artifacts/digits'
        splits=json.loads((folder/'splits.json').read_text())
        with np.load(folder/'data.npz') as data:
            for i,row in enumerate(splits):
                raw=sources[row['source']][row['row_ids']]
                name=f"task_{i//2}_{row['partition']}"
                assert np.array_equal(data[name+'_x'],raw[:,:64]/16.)
                assert np.array_equal(data[name+'_y'],np.where(raw[:,-1:]==row['pair'][0],-1.,1.))
                arrays+=2
inventory=json.loads((OUT/'inventory.json').read_text())
changed=[r['path'] for r in inventory['files'] if sha(ROOT/r['path'])!=r['sha256']]
assert not changed,changed
result={'historical_snapshot_files':len(files),'historical_source_hash':identity['content_hash'],
        'digit_arrays_verified_against_original_source_rows':arrays,
        'original_files_rechecked':len(inventory['files']),'original_files_changed':changed,
        'scope':'Runtime trees excluded except separately inventoried historical research source. No notebook files found in project or historical-source inventories.'}
(OUT/'receipts/scope_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
