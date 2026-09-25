#!/usr/bin/env python3
"""Standalone archive verification with optional safe fresh extraction."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import tempfile


def safe_name(name):
    path=PurePosixPath(name)
    return bool(name) and not path.is_absolute() and '..' not in path.parts and '\\' not in name and path.as_posix()==name


def require(condition, message):
    """Keep integrity checks active even when Python runs with -O."""
    if not condition:
        raise ValueError(message)


def main(directory,extract=None):
    directory=directory.resolve()
    receipt=json.loads((directory/'receipt.json').read_text())
    archive=directory/'world-series-review.tar.gz'
    with archive.open('rb') as f:
        require(hashlib.file_digest(f,'sha256').hexdigest()==receipt['sha256'], 'Archive checksum mismatch')
    with tarfile.open(archive,'r:gz') as tar:
        members=tar.getmembers()
        names=[m.name for m in members]
        require(len(names)==len(set(names)), 'Duplicate archive members')
        require(all(safe_name(m.name) and m.isfile() for m in members), 'Unsafe archive member')
        manifest=json.load(tar.extractfile('manifest.json'))
        require(manifest==json.loads((directory/'manifest.json').read_text()), 'Manifest mismatch')
        require(set(names)==set(manifest['files'])|{'manifest.json'}, 'Archive inventory mismatch')
        for name,expected in manifest['files'].items():
            member=tar.getmember(name)
            require(member.size==expected['bytes'], f'Wrong size: {name}')
            with tar.extractfile(member) as handle:
                require(hashlib.file_digest(handle,'sha256').hexdigest()==expected['sha256'], f'Checksum mismatch: {name}')
        # No existing checkout or external sidecar bundle is needed.
        with tempfile.TemporaryDirectory(prefix='world-series-bundle-') as work:
            work=Path(work)
            bundle=work/'source.bundle'
            with tar.extractfile('source.bundle') as source,bundle.open('wb') as target:
                while chunk:=source.read(1024*1024): target.write(chunk)
            subprocess.run(['git','init','--bare','--quiet',str(work/'verify.git')],check=True)
            check=subprocess.run(['git','-C',str(work/'verify.git'),'bundle','verify',str(bundle)],capture_output=True,text=True,check=True)
        if extract is not None:
            extract=extract.resolve()
            extract.mkdir(parents=True,exist_ok=False)
            tar.extractall(extract,filter='data')
    result={'passed':True,'verified_files':len(manifest['files']),'archive_sha256':receipt['sha256'],
            'source':manifest['source'],'git_bundle_verification':check.stdout+check.stderr,
            'extracted_to':None if extract is None else str(extract),
            'scope':'Archive integrity, safe extraction and self-contained Git bundle validation; not scientific replication.'}
    (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source','git_bundle_verification')}))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    parser.add_argument('--extract',type=Path)
    args=parser.parse_args()
    main(args.directory,args.extract)
