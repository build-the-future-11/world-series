import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tarfile

import pytest


def module(name):
    path=Path(__file__).resolve().parents[1]/'scripts'/f'{name}.py'
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_complete_package_verifies_without_original_checkout_or_sidecar(tmp_path,monkeypatch):
    build,verify=module('build_delivery'),module('verify_delivery')
    root=tmp_path/'authored'; root.mkdir()
    for name in build.ROOT_FILES: (root/name).write_text('fixture\n')
    (root/'provenance').mkdir()
    (root/'provenance/IMPORT_MANIFEST.json').write_text(json.dumps({'files':[]}))
    (root/'campaigns/new-study').mkdir(parents=True)
    (root/'campaigns/new-study/failure.json').write_text('{"status":"failed"}')
    (root/'runs/unfinished').mkdir(parents=True)
    (root/'runs/unfinished/manifest.json').write_text('{"status":"RUNNING"}')
    (root/'paper').mkdir()
    (root/'paper/preprint.md').write_text('Evidence-bound manuscript\n')
    subprocess.run(['git','init','--quiet',str(root)],check=True)
    subprocess.run(['git','-C',str(root),'add','.'],check=True)
    subprocess.run(['git','-C',str(root),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','--quiet','-m','fixture'],check=True)
    output=tmp_path/'delivery'
    build.main(output,root)
    (output/'source.bundle').unlink()  # Verification must use the archive's bundle.
    moved=tmp_path/'moved-away'; root.rename(moved)
    monkeypatch.chdir(tmp_path)
    result=verify.main(output,tmp_path/'extracted')
    assert result['passed']
    assert (tmp_path/'extracted/repository/campaigns/new-study/failure.json').read_text()=='{"status":"failed"}'
    assert (tmp_path/'extracted/repository/runs/unfinished/manifest.json').is_file()
    assert (tmp_path/'extracted/repository/paper/preprint.md').read_text()=='Evidence-bound manuscript\n'
    restored=module('restore_delivery').restore(tmp_path/'extracted',tmp_path/'restored')
    assert restored['source_head']==result['source']['git_head']
    assert (tmp_path/'restored/campaigns/new-study/failure.json').is_file()
    with pytest.raises(FileExistsError): verify.main(output,tmp_path/'extracted')


def test_tampered_import_and_recursive_output_rejected(tmp_path):
    build=module('build_delivery')
    for name in build.ROOT_FILES: (tmp_path/name).write_text('fixture')
    (tmp_path/'provenance').mkdir()
    (tmp_path/'provenance/evidence').write_text('changed')
    (tmp_path/'provenance/IMPORT_MANIFEST.json').write_text(json.dumps({'files':[{'path':'provenance/evidence','sha256':'0'*64}]}))
    with pytest.raises(ValueError,match='Changed imported'): build.gather_files(tmp_path)
    with pytest.raises(ValueError,match='outside included'): build.main(tmp_path/'campaigns/output',tmp_path)


def test_unsafe_archive_member_rejected_before_extraction(tmp_path):
    verify=module('verify_delivery')
    archive=tmp_path/'world-series-review.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        info=tarfile.TarInfo('../escape'); info.size=1
        tar.addfile(info,io.BytesIO(b'x'))
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    (tmp_path/'receipt.json').write_text(json.dumps({'sha256':digest}))
    with pytest.raises(ValueError,match='Unsafe'): verify.main(tmp_path,tmp_path/'extract')
    assert not (tmp_path/'extract').exists()


@pytest.mark.parametrize("optimized", [False, True])
def test_archive_checksum_checked_before_opening(tmp_path, optimized):
    import sys

    (tmp_path / 'world-series-review.tar.gz').write_bytes(b'not a tar file')
    (tmp_path / 'receipt.json').write_text(json.dumps({'sha256': '0' * 64}))
    script = Path(__file__).resolve().parents[1] / 'scripts/verify_delivery.py'
    argv = [sys.executable] + (['-O'] if optimized else []) + [str(script), str(tmp_path)]
    result = subprocess.run(argv, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Archive checksum mismatch' in result.stderr
