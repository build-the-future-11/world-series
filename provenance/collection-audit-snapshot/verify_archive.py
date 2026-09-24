"""Verify the existing delivery without changing it or extracting its members."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile

OUT=Path(__file__).resolve().parent
REPO=OUT.parents[1]/'world-series'
sys.path.insert(0,str(REPO/'src'))
from world_series.core.identity import source_identity

directory=REPO/'deliveries/20260924-development'
receipt=json.loads((directory/'receipt.json').read_text())
with (directory/'world-series-review.tar.gz').open('rb') as handle:
    assert hashlib.file_digest(handle,'sha256').hexdigest()==receipt['sha256']
with tarfile.open(directory/'world-series-review.tar.gz','r:gz') as archive:
    manifest=json.load(archive.extractfile('manifest.json'))
    assert manifest==json.loads((directory/'manifest.json').read_text())
    members=archive.getmembers()
    assert len({m.name for m in members})==len(members)
    assert {m.name for m in members}==set(manifest['files'])|{'manifest.json'}
    for name,expected in manifest['files'].items():
        member=archive.getmember(name)
        assert member.isfile() and member.size==expected['bytes']
        with archive.extractfile(name) as handle:
            assert hashlib.file_digest(handle,'sha256').hexdigest()==expected['sha256'],name
bundle=subprocess.run(['git','-C',str(REPO),'bundle','verify',str(directory/'source.bundle')],capture_output=True,text=True)
assert bundle.returncode==0,bundle.stderr
replays=json.loads((OUT/'receipts/replay_inventory.json').read_text())
assert len(replays)==400 and all(r['exact'] for r in replays)
result={'passed':True,'archive_files':len(manifest['files']),'archive_sha256':receipt['sha256'],
        'archive_source':manifest['source'],'current_source':source_identity(REPO),
        'bundle':bundle.stdout+bundle.stderr,'historical_replay_receipts_exact':400,
        'scope':'Archive integrity and stored replay claims checked; full meta-training not rerun in this audit.'}
(OUT/'receipts/archive_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
