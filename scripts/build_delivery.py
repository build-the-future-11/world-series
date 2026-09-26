#!/usr/bin/env python3
"""Complete local review archive using repository-relative inputs only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ('src','tests','scripts','configs','docs','paper','data','experiments','provenance','results','runs','campaigns','.github')
ROOT_FILES = ('README.md','AGENTS.md','.gitignore','pyproject.toml','requirements.lock.txt','reproduce.sh','LICENSE','LICENSE.md','NOTICE','THIRD_PARTY.md','FINAL_RELEASE_REPORT.md')


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle,'sha256').hexdigest()


def gather_files(root):
    files = {}
    for folder in FOLDERS:
        for path in sorted((root/folder).rglob('*')):
            if path.is_symlink():
                raise ValueError(f'Symlink input is not a portable regular artifact: {path}')
            if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc' or (folder=='paper' and path.suffix in {'.log','.aux','.out','.toc'}):
                continue
            files['repository/'+path.relative_to(root).as_posix()] = path
    for name in ROOT_FILES:
        if not (root/name).is_file():
            raise FileNotFoundError(root/name)
        files['repository/'+name] = root/name
    imported = json.loads((root/'provenance/IMPORT_MANIFEST.json').read_text())
    for entry in imported['files']:
        path = (root/entry['path']).resolve()
        if not path.is_relative_to(root.resolve()) or digest(path)!=entry['sha256']:
            raise ValueError(f'Changed imported evidence: {entry["path"]}')
    return files


def source_identity(root):
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    status = subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
    sources = {p.relative_to(root).as_posix():digest(p) for p in sorted((root/'src').rglob('*.py'))}
    return {'git_head':head,'git_dirty':bool(status.strip()),'git_status':status,
            'source_file_hashes':sources,
            'source_hash_schema':'sha256(canonical sorted JSON of relative source paths and SHA256)',
            'content_hash':hashlib.sha256(json.dumps(sources,sort_keys=True,separators=(',',':')).encode()).hexdigest()}


def main(output,root=ROOT):
    root=root.resolve()
    output=output.resolve()
    if any(output.is_relative_to(root/folder) for folder in FOLDERS):
        raise ValueError('Delivery output must be outside included input folders')
    output.mkdir(parents=True,exist_ok=False)
    files=gather_files(root)
    bundle=output/'source.bundle'
    subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=root,check=True)
    files['source.bundle']=bundle
    manifest={'schema_version':2,'scope':'Complete local review evidence, including failures. No submission, license clearance, external signature or independent scientific verdict.',
              'source':source_identity(root),
              'files':{name:{'sha256':digest(path),'bytes':path.stat().st_size} for name,path in sorted(files.items())},
              'included_folders':FOLDERS,'external_weights':'Celo2 weights are not redistributed; pinned fetch information is in docs/execution/development-v2/CELO2_PROVENANCE.json.',
              'historical_paths':'Absolute paths inside immutable receipts describe their original environment. They are not package input dependencies.'}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=output/'world-series-review.tar.gz'
    with tarfile.open(archive,'w:gz',compresslevel=6) as tar:
        tar.add(output/'manifest.json',arcname='manifest.json',recursive=False)
        for name,path in sorted(files.items()):
            if digest(path)!=manifest['files'][name]['sha256']:
                raise RuntimeError(f'Input changed during packaging: {name}')
            tar.add(path,arcname=name,recursive=False)
    receipt={'archive':archive.name,'sha256':digest(archive),'bytes':archive.stat().st_size,
             'file_count':len(files),'source':manifest['source']}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='source'}))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
