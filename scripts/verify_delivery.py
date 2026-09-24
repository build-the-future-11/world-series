#!/usr/bin/env python3
"""Read-only verification of every member in a locally built review archive."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile


def main(directory):
    receipt=json.loads((directory/'receipt.json').read_text())
    archive=directory/'world-series-review.tar.gz'
    assert hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()==receipt['sha256']
    with tarfile.open(archive,'r:gz') as tar:
        members=tar.getmembers()
        names=[m.name for m in members]
        assert len(names)==len(set(names)), 'Duplicate archive members'
        manifest=json.load(tar.extractfile('manifest.json'))
        assert manifest==json.loads((directory/'manifest.json').read_text())
        assert set(names)==set(manifest['files'])|{'manifest.json'}
        for name,expected in manifest['files'].items():
            member=tar.getmember(name)
            assert member.isfile() and member.size==expected['bytes']
            with tar.extractfile(member) as handle:
                assert hashlib.file_digest(handle,'sha256').hexdigest()==expected['sha256'],name
    check=subprocess.run(['git','bundle','verify',str((directory/'source.bundle').resolve())],
                         capture_output=True,text=True,check=True)
    result={'passed':True,'verified_files':len(manifest['files']),
            'archive_sha256':receipt['sha256'],'source':manifest['source'],
            'git_bundle_verification':check.stdout+check.stderr,
            'scope':'Archive integrity and Git bundle validation; not independent scientific replication.'}
    (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path)
    main(parser.parse_args().directory)
