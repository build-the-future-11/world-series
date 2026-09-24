#!/usr/bin/env python3
"""Single-worker, source/config-bound campaign with verified completed-cell resume."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import time
import traceback
import torch
from world_series.core.identity import source_identity, hash_mapping
from world_series.core.contracts import RunStatus
from world_series.evaluation.runner import create_run
from world_series.projects import dispatch_run

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run_campaign(plan, output):
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'worker.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        torch.set_num_threads(1)
        source = source_identity(ROOT)
        identity = {'plan_sha256': hash_mapping(plan), 'source': source, 'plan': plan}
        ident = output / 'identity.json'
        if ident.exists():
            old = json.loads(ident.read_text())
            if old['plan_sha256'] != identity['plan_sha256'] or old['source']['content_hash'] != source['content_hash']:
                raise RuntimeError('Source/config changed; use a new campaign directory')
        else:
            ident.write_text(json.dumps(identity, indent=2) + '\n')
        attempts = []
        for cfg in plan['cells']:
            if source_identity(ROOT)['content_hash'] != source['content_hash']:
                raise RuntimeError('Source changed during campaign; stopping before next cell')
            cell = cfg['project'] + '-' + cfg['experiment'] + '-' + str(cfg['seed'])
            receipt = output / (cell + '.json')
            if receipt.exists():
                record = json.loads(receipt.read_text())
                if record['status'] == 'SUCCEEDED':
                    run_path = ROOT / 'runs' / record['run_id']
                    for relative, sha in record['file_hashes'].items():
                        if digest(run_path / relative) != sha:
                            raise RuntimeError(f'Corrupt resume artifact {run_path / relative}')
                    attempts.append(record)
                    print(json.dumps({'cell': cell, 'resume': 'VERIFIED'}), flush=True)
                    continue
                receipt = output / (cell + f'-retry-{time.time_ns()}.json')
            run = create_run(ROOT, cfg)
            run.set_status(RunStatus.RUNNING)
            run.store.write_json('executed_config.json', cfg)
            started = time.perf_counter()
            try:
                metrics = dispatch_run(cfg, run)
                run.write_metrics(metrics)
                status = RunStatus(metrics.get('status', 'FAILED'))
                run.set_status(status)
            except BaseException as exc:
                status = RunStatus.INTERRUPTED if isinstance(exc, KeyboardInterrupt) else RunStatus.FAILED
                run.set_status(status, error={'message': str(exc), 'traceback': traceback.format_exc()})
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
            record = {'cell': cell, 'run_id': run.manifest.run_id, 'status': status.value,
                      'config_hash': hash_mapping(cfg), 'elapsed_seconds': time.perf_counter() - started,
                      'file_hashes': {str(p.relative_to(run.path)): digest(p)
                                      for p in run.path.rglob('*') if p.is_file()}}
            receipt.write_text(json.dumps(record, indent=2) + '\n')
            attempts.append(record)
            print(json.dumps({k: v for k, v in record.items() if k != 'file_hashes'}), flush=True)
        summary = {'complete': len(attempts) == len(plan['cells']) and all(r['status'] == 'SUCCEEDED' for r in attempts),
                   'expected_cells': len(plan['cells']), 'attempted_cells': len(attempts), 'cells': attempts,
                   'confirmation': 'DRAFT_NOT_AUTHORIZED'}
        (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        return 0 if summary['complete'] else 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    raise SystemExit(run_campaign(json.loads(Path(args.plan).read_text()), Path(args.output)))
