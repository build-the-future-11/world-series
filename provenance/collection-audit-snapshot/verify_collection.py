"""Read-only research evidence audit; all new outputs stay beside this script."""
from pathlib import Path
import collections, csv, fcntl, hashlib, itertools, json, os, subprocess, sys
import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
REPO = ROOT / 'world-series'
sys.path[:0] = [str(REPO / 'scripts'), str(REPO / 'src')]
import analyze_development as analysis
import analyze_sensitivity as sensitivity

def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

# Inventory project-controlled files recursively, including ignored raw evidence.
# Dependency/cache trees are accounted for separately, never treated as projects.
excluded = {'.git', '.venv', '.venv-celo2', '.work-tmp', '__pycache__',
            '.pytest_cache', '.ruff_cache', 'publication_audit'}
inventory, exclusions, dirs, links = [], [], [], []
for base, subdirs, files in os.walk(ROOT, followlinks=False):
    base = Path(base)
    dirs.append(str(base.relative_to(ROOT)))
    for d in subdirs[:]:
        p = base / d
        if d in excluded:
            exclusions.append(str(p.relative_to(ROOT))); subdirs.remove(d)
        elif p.is_symlink():
            links.append({'path': str(p.relative_to(ROOT)), 'target': str(p.resolve())})
            subdirs.remove(d)
    for name in files:
        p = base / name
        if p.is_symlink():
            links.append({'path': str(p.relative_to(ROOT)), 'target': str(p.resolve())}); continue
        inventory.append({'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': sha(p)})
dump('inventory.json', {'files': inventory, 'directories': dirs, 'excluded_runtime_or_audit_trees': exclusions, 'symlinks': links})
hash_groups = collections.defaultdict(list)
for row in inventory:
    if row['bytes']: hash_groups[row['sha256']].append(row['path'])
dump('duplicates.json', {h: ps for h, ps in hash_groups.items() if len(ps) > 1})

locks = []
for p in sorted((REPO/'campaigns').glob('*/worker.lock')):
    with p.open('r') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state = 'unheld_at_check'; fcntl.flock(f, fcntl.LOCK_UN)
        except BlockingIOError: state = 'held_at_check'
    locks.append({'path': str(p.relative_to(ROOT)), 'state': state})
dump('receipts/locks.json', locks)

campaigns, allruns, errors = [], [], []
for p in sorted((REPO/'campaigns').glob('*/summary.json')):
    summary = json.loads(p.read_text())
    cells = summary.get('cells', [])
    counts = collections.Counter(c.get('status') for c in cells)
    checked = 0
    for cell in cells:
        if not cell.get('run_id'): continue
        run = REPO/'runs'/cell['run_id']
        for relative, expected in cell.get('file_hashes', {}).items():
            path = run/relative
            if not path.is_file() or sha(path) != expected: errors.append(str(path))
            checked += 1
    campaigns.append({'campaign': p.parent.name, 'complete': summary.get('complete'),
                      'cells': len(cells), 'statuses': dict(counts), 'hashes_checked': checked})
for p in sorted((REPO/'runs').glob('*/manifest.json')):
    m = json.loads(p.read_text())
    allruns.append({k: m.get(k) for k in ('run_id','project','experiment','split','seed','status','source')})
dump('run_index.json', allruns)
assert not errors, errors

# Regenerate analyses in a separate output directory, retaining original reports.
analysis.OUT = OUT/'recomputed'
analysis.main()
sensitivity.OUT = OUT/'recomputed'
sensitivity.main()
compared = []
for p in sorted((OUT/'recomputed').iterdir()):
    original = REPO/'docs/execution/development-v2'/p.name
    if original.exists(): compared.append({'file': p.name, 'byte_identical': sha(p) == sha(original)})
dump('receipts/analysis_comparison.json', compared)

# Recompute every module summary from individual observations, not report prose.
from world_series.evaluation.development import aggregate, synthesis_cases
from world_series.qwipii.domains import RingState
from world_series.qwipii.search import replay
module_checks, contrast_values = [], collections.defaultdict(list)
for manifest, result in analysis.campaign('development-v2'):
    project = manifest['project']; rows = result['rows']
    assert aggregate(rows) == result['summary'], (project, manifest['run_id'])
    if project == 'qapen':
        assert len(result['trajectories']) == 2800
        for r in result['trajectories']:
            expected = .5*np.log(2*np.pi*r['predicted_variance'])+.5*(r['observed']-r['predicted_mean'])**2/r['predicted_variance']
            assert abs(expected-r['nll']) < 1e-12
    if project == 'qwipii':
        for r in rows:
            assert r['expansions'] <= int(r['condition'].split('budget')[1])
            if r['value']: assert replay(RingState(tuple(r['start']),tuple(r['goal'])),r['path']).tokens == tuple(r['goal'])
    if project in {'wcode','ultron'}:
        assert all(r['candidates'] <= int(r['condition'].split('budget')[1]) for r in rows)
    if project == 'ultron':
        assert set(result['training_task_ids']).isdisjoint(result['evaluation_task_ids'])
    if project == 'wpinn': assert all(r['train_id'] != r['held_id'] for r in rows)
    for r in result['summary']:
        contrast_values[(project,r['method'],r['condition'])].append({'seed':manifest['seed'], 'value':r['mean']})
    module_checks.append({'project':project,'seed':manifest['seed'],'run_id':manifest['run_id'],
                         'raw_rows':len(rows),'failed_rows':sum(r['value'] is None for r in rows)})
dump('receipts/module_checks.json', module_checks)

contrasts=[]
for project, candidate, baseline, condition in [
    ('qapen','context_memory','no_memory','all'), ('qapen','context_memory','single_expert_memory','all'),
    ('qapen','context_memory','fixed','rare'), ('ultron','learned','cheapest','budget24'),
    ('cwlnn','hierarchy','flat','n96'), ('cwlnn','routed','hierarchy','n96')]:
    a={r['seed']:r['value'] for r in contrast_values[(project,candidate,condition)]}
    b={r['seed']:r['value'] for r in contrast_values[(project,baseline,condition)]}
    diffs=[a[s]-b[s] for s in sorted(a)]
    contrasts.append({'project':project,'candidate':candidate,'baseline':baseline,'condition':condition,
        'candidate_minus_baseline':float(np.mean(diffs)),'seed_differences':diffs,
        'p_exact_exploratory_unadjusted':analysis.sign_flip(diffs),
        'scope':'Post hoc diagnostic; shared finite task distributions; no confirmatory inference.'})
dump('receipts/scoped_contrasts.json', contrasts)

# Cheap structural falsification: per-letter transport is an algebra automorphism.
from world_series.wfim.algebra import SparseWordSeries, multiply
from world_series.wfim.transport import transported_multiply
rng=np.random.default_rng(20260924); maximum=0.
for _ in range(100):
    def draw():
        return SparseWordSeries({tuple(int(v) for v in rng.integers(1,4,int(rng.integers(0,5)))):float(rng.normal()) for _ in range(12)})
    x,y=draw(),draw(); base=multiply(x,y)
    for scales in ({1:.5,2:2.,3:1.5},{1:1.2,2:.8,3:1.1}):
        out=transported_multiply(x,y,scales)
        maximum=max(maximum,max(abs(out.coeffs.get(k,0)-base.coeffs.get(k,0)) for k in set(out.coeffs)|set(base.coeffs)))
assert maximum < 1e-12
dump('receipts/wfim_transport.json', {'cases':200,'maximum_absolute_difference':maximum,
    'proof':'s(uv)=s(u)s(v), so S^-1(Sx * Sy)=x*y for every nonzero per-letter scale.',
    'scope':'Rules out product-level expressivity from the current transport, not every possible learned coordinate model.'})

# Dataset/source/role checks over every main and sensitivity run.
split_checks=[]
for name in ['natural-digits-v1','natural-digits-sensitivity-v1']:
    for manifest,result in analysis.campaign(name):
        run=REPO/'runs'/manifest['run_id']/'artifacts/digits'
        records=json.loads((run/'splits.json').read_text())
        inp=json.loads((run/'input.json').read_text())
        for source,h in inp['source_files'].items(): assert sha(REPO/'data/optdigits'/source)==h
        role_rows=collections.defaultdict(set)
        for r in records:
            role_rows[r['role']].update((r['source'],v) for v in r['row_ids'])
        assert all(not role_rows[a]&role_rows[b] for a,b in itertools.combinations(role_rows,2))
        for pair in {(tuple(r['pair'])) for r in records}:
            sub=[r for r in records if tuple(r['pair'])==pair]
            sets=[{(r['source'],v) for v in r['row_ids']} for r in sub]
            assert not sets[0]&sets[1]
        split_checks.append({'campaign':name,'seed':manifest['seed'],'run_id':manifest['run_id'],'passed':True})
dump('receipts/splits.json',split_checks)

# Historical replay receipts are audited as stored evidence, not relabeled as new reruns.
replays=[]
for p in (REPO/'campaigns/meta-training-replay-v1').glob('*.json'):
    if p.name != 'summary.json':
        r=json.loads(p.read_text()); replays.append({'file':p.name,'exact':all(r.get(k) is True for k in
            ['parameters_optimizer_counters_exact','training_history_exact','failure_exact'])})
dump('receipts/replay_inventory.json',replays)
git={command:subprocess.check_output(['git','-C',str(REPO),*command.split()],text=True).strip()
     for command in ['rev-parse HEAD','status --porcelain','branch -a','worktree list','remote -v']}
summary={'workspace':str(ROOT),'files_in_inventory':len(inventory),'directories':len(dirs),
    'campaigns':campaigns,'all_run_manifests':len(allruns),'run_statuses':dict(collections.Counter(r['status'] for r in allruns)),
    'verified_campaign_file_hashes':sum(c['hashes_checked'] for c in campaigns),'hash_errors':errors,
    'module_raw_rows':sum(r['raw_rows'] for r in module_checks),'module_failed_rows':sum(r['failed_rows'] for r in module_checks),
    'analysis_outputs_identical':all(r['byte_identical'] for r in compared),'analysis_files_compared':len(compared),
    'semantic_dsl_tasks':len(synthesis_cases(101)),'git':git,
    'scope':'Local audit and analysis replay; no new full training campaign or independent replication.'}
dump('receipts/verification.json',summary)
print(json.dumps(summary,indent=2))
