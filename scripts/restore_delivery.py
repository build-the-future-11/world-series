#!/usr/bin/env python3
"""Restore a fresh Git checkout plus all evidence from a verified extraction."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess


def restore(extraction,output):
    extraction=extraction.resolve(); output=output.resolve()
    if output.exists(): raise FileExistsError(output)
    manifest=json.loads((extraction/'manifest.json').read_text())
    for name,entry in manifest['files'].items():
        path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:
            raise ValueError('Unsafe manifest path')
        source=extraction/name
        if source.is_symlink() or not source.is_file(): raise ValueError(f'Not a regular file: {name}')
        with source.open('rb') as handle:
            if hashlib.file_digest(handle,'sha256').hexdigest()!=entry['sha256']:
                raise ValueError(f'Changed extracted file: {name}')
    subprocess.run(['git','clone','--quiet',str(extraction/'source.bundle'),str(output)],check=True)
    subprocess.run(['git','-C',str(output),'checkout','--quiet','--detach',manifest['source']['git_head']],check=True)
    for name in manifest['files']:
        if not name.startswith('repository/'): continue
        relative=PurePosixPath(name).relative_to('repository')
        target=output/relative; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(extraction/name,target)
    result={'source_head':manifest['source']['git_head'],'source_was_dirty':manifest['source']['git_dirty'],
            'restored_files':sum(n.startswith('repository/') for n in manifest['files']),
            'output':str(output),'scope':'Restored source and evidence, not rerun experiments.'}
    print(json.dumps(result))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('extraction',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    restore(args.extraction,args.output)
