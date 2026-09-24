"""Audit all stream receipts, recompute metrics, and report seed-paired contrasts."""
from collections import defaultdict,Counter
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
DIRECTORY=ROOT/'campaigns/qapen-lifecycle-v1'
OUT=ROOT/'docs/closure'


def main():
    summary=json.loads((DIRECTORY/'summary.json').read_text())
    assert summary['expected_stream_methods']==512 and len(summary['receipts'])==512
    results=[];seen=set();events=Counter();costs=defaultdict(list)
    for receipt in summary['receipts']:
        for filename,digest in receipt['files'].items():
            assert hashlib.sha256((DIRECTORY/filename).read_bytes()).hexdigest()==digest,filename
        result=json.loads((DIRECTORY/(receipt['key']+'.json')).read_text())
        unit=tuple(result[k] for k in ['seed','schedule','noise','method'])
        assert unit not in seen;seen.add(unit)
        assert result['complete'] and len(result['rows'])==320
        for i,row in enumerate(result['rows']):
            expected=.5*np.log(2*np.pi*row['variance'])+.5*(row['target']-row['mean'])**2/row['variance']
            assert abs(expected-row['nll'])<1e-10 and row['time']==i
            assert row['operations']<=2_000_000 and row['active']<=4 and row['identities']<=16
        assert abs(np.mean([r['nll'] for r in result['rows']])-result['summary']['all']['nll'])<1e-12
        if result['method']!='rolling_ridge':
            state=result['state'];identities=state['experts']
            for e in state['engrams']:
                assert e['expert_id'] in identities and e['utility_count']<=e['accesses']
            assert len(state['engrams'])<=64
            for e in state['events']:
                events[(result['method'],e['event'],e.get('to',e.get('state')))]+=1
                if e.get('from')=='WARMUP':
                    m=identities[e['identity']]
                    assert e['time']>m['birth'] and m['prospective_count']>=8
                    if e['to']=='ACTIVE':assert m['prospective_gain']>0
            if result['method'] in {'lifecycle_no_memory','fixed_no_memory'}:
                assert not state['engrams'] and state['costs']['retrieval_distances']==0
        results.append(result)
    methods=sorted({r['method'] for r in results});seeds=sorted({r['seed'] for r in results})
    assert len(methods)==8 and len(seeds)==8
    seed_values={};table=[];conditions=[]
    for method in methods:
        rows=[r for r in results if r['method']==method];assert len(rows)==64
        seed_values[method]={s:float(np.mean([r['summary']['all']['nll'] for r in rows if r['seed']==s])) for s in seeds}
        table.append({'method':method,'stream_count':len(rows),'mean_nll':float(np.mean(list(seed_values[method].values()))),
                      'coverage95':float(np.mean([r['summary']['all']['coverage95'] for r in rows])),
                      'mean_operations':float(np.mean([r['operations'] for r in rows])),
                      'total_seconds':sum(r['elapsed_seconds'] for r in rows),
                      'mean_checkpoint_bytes':float(np.mean([r['checkpoint_bytes'] for r in rows]))})
        for condition,noise in sorted({(r['schedule'],r['noise']) for r in rows}):
            subset=[r for r in rows if (r['schedule'],r['noise'])==(condition,noise)];assert len(subset)==8
            for endpoint in ['all','rare','ordinary','recovery']:
                values=[r['summary'][endpoint]['nll'] for r in subset]
                conditions.append({'method':method,'schedule':condition,'noise':noise,'endpoint':endpoint,
                                   'mean_nll':float(np.mean(values)) if all(v is not None for v in values) else None,
                                   'observations':sum(r['summary'][endpoint]['n'] for r in subset)})
    rng=np.random.default_rng(240925);comparisons=[]
    for method in methods:
        if method=='lifecycle_memory':continue
        diff=np.array([seed_values['lifecycle_memory'][s]-seed_values[method][s] for s in seeds])
        intervals=np.quantile(rng.choice(diff,size=(10000,8),replace=True).mean(1),[.025,.975]).tolist()
        comparisons.append({'control':method,'candidate_minus_control_nll':float(diff.mean()),'seed_differences':diff.tolist(),'descriptive_bootstrap95':intervals})
    payload={'verified_stream_methods':512,'verified_predictions':512*320,'all_complete':True,
             'identity':summary['identity'],'table':table,'conditions':conditions,'per_seed':seed_values,'comparisons':comparisons,
             'events':[{'method':m,'event':e,'state':s,'count':n} for (m,e,s),n in sorted(events.items())],
             'scope':'Eight independent parameter seeds, paired across eight schedules/noise conditions. Same-host finite linear-Gaussian development. No independent confirmation or full world-model claim.'}
    (OUT/'QAPEN_RESULTS.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    lines=['# Causal lifecycle and delayed-memory results','','All 512 stream-method cells completed: 163,840 causal predictions. Artifact hashes, NLL recomputation, resource caps, prospective warmup and memory references passed audit.','',
           '| Method | Mean NLL | 95% coverage | Mean operation proxy | Total execution seconds |','|---|---:|---:|---:|---:|']
    for r in table:lines.append(f"| {r['method']} | {r['mean_nll']:.6g} | {r['coverage95']:.4f} | {r['mean_operations']:.0f} | {r['total_seconds']:.3f} |")
    lines+=['','Lower NLL is better. All methods obey the same operation cap, but actual work is unequal. The operation proxy omits hardware-specific constants; elapsed times are not randomized or equal-wall-time comparisons. Checkpoint bytes include state/serialization metadata and are not peak RSS. Codebook pretraining is shared and recorded separately.','',
            '| Control | Candidate minus control NLL | Descriptive paired-seed 95% interval |','|---|---:|---|']
    for r in comparisons:lines.append(f"| {r['control']} | {r['candidate_minus_control_nll']:.6g} | {r['descriptive_bootstrap95']} |")
    lines+=['','Intervals are exploratory, unadjusted and based on eight seed units. Do not treat the 163,840 timesteps as independent samples or infer practical equivalence. The complete condition table includes ordinary, rare and recovery metrics; unavailable rare/recovery cells in no-shift streams remain null.','',
            'This implements and exercises a finite linear-Gaussian lifecycle and memory candidate. It does not implement neural latent dynamics, imagination/planning or every later PEN-family proposal. All negative outcomes remain part of the evidence.']
    (OUT/'QAPEN_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'table':table,'events':payload['events']}))


if __name__=='__main__':main()
