"""Verify stored WFT actions using NumPy/SciPy and aggregate complete seed units."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from scipy.linalg import expm
import torch

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(Path(__file__).resolve().parent)]
from world_series.wft.constraints import domain,teacher
from wft_study import make_data

DIRECTORY=ROOT/'campaigns/wft-constraints-v1'
OUT=ROOT/'docs/closure'


def numpy_laplacian(graph,state):
    coefficients=state['coefficients'].numpy();within=float(state['within'])
    raw=graph.basis.numpy()@coefficients[graph.level]
    weights=np.where(graph.horizontal.numpy(),np.logaddexp(0,raw),np.logaddexp(0,within))*graph.scale.numpy()
    b=graph.incidence.numpy()
    return b.T@(weights[:,None]*b)


def main():
    torch.set_num_threads(1)
    summary=json.loads((DIRECTORY/'summary.json').read_text())
    assert summary['complete'] and summary['expected_fits']==224 and len(summary['receipts'])==224
    rows=[];costs=[];checked=set();data_cache={};seen=set();maximum_difference=0.;true_constraint_checks=0
    compression_differences=[]
    for receipt in summary['receipts']:
        for name,digest in receipt['files'].items():
            if name not in checked:
                assert hashlib.sha256((DIRECTORY/name).read_bytes()).hexdigest()==digest
                checked.add(name)
        record=json.loads((DIRECTORY/(receipt['key']+'.json')).read_text())
        seed=record['seed'];samples=record['samples'];noise=record['noise'];method=record['method']
        assert record['complete'] and len(record['rows'])==12
        key=(seed,samples,noise)
        if key not in data_cache:
            with np.load(DIRECTORY/f'{seed}-{samples}-{noise}-data.npz') as stored:data={k:stored[k] for k in stored.files}
            regenerated=make_data(*key)
            assert all(np.array_equal(data[k],regenerated[k]) for k in data)
            data_cache[key]=data
            truth=teacher(seed)
            for groups in [16,32,64]:
                for topology in ['cycle','path']:
                    fine=domain(groups,topology,0);coarse=domain(groups,topology,1)
                    sym,scale=truth.penalties(fine,coarse)
                    assert float(sym.detach())<1e-20 and float(scale.detach())<1e-20
                    true_constraint_checks+=1
        data=data_cache[key]
        checkpoint=torch.load(DIRECTORY/(receipt['key']+'.pt'),weights_only=True)
        state=checkpoint['state_dict']
        digest=hashlib.sha256(b''.join(state[k].numpy().tobytes() for k in ['coefficients','within'])).hexdigest()
        assert digest==record['parameter_hash']
        if not record['oracle'] and method!='fixed_geometry':
            assert len(record['history'])==100 and record['cost']['parameter_count']==11
            assert 'optimizer_state' in checkpoint
        with np.load(DIRECTORY/(receipt['key']+'-predictions.npz')) as predictions:
            for row in record['rows']:
                unit=(seed,samples,noise,method,row['groups'],row['topology'],row['level'])
                assert unit not in seen;seen.add(unit)
                assert row['frozen_parameter_hash']==digest
                graph=domain(row['groups'],row['topology'],row['level']);l=numpy_laplacian(graph,state)
                mass=graph.mass.numpy();action=l/mass[:,None]
                matrix=expm(-.15*action);name=f"{row['groups']}-{row['topology']}-{row['level']}"
                x=data['x-'+name];y=data['y-'+name];prediction=matrix@x
                difference=float(np.max(np.abs(prediction-predictions[name])));maximum_difference=max(maximum_difference,difference)
                assert difference<1e-10
                error=float(np.sum(mass[:,None]*(prediction-y)**2)/np.sum(mass[:,None]*y**2))
                assert abs(error-row['relative_prediction_error'])<1e-10
                inv=1/np.sqrt(mass);s=inv[:,None]*l*inv[None,:];eigenvalues,q=np.linalg.eigh(s)
                assert eigenvalues[0]>-1e-10 and abs(l.sum(1)).max()<1e-10
                assert row['spectral']['eigen_residual']<1e-10 and row['spectral']['full_basis_error']<1e-10
                rank=min(5,samples)
                while rank<len(mass) and abs(eigenvalues[rank]-eigenvalues[rank-1])<=1e-8*max(1.,abs(eigenvalues[rank])):rank+=1
                assert rank==row['spectral']['rank_retained']
                white=np.sqrt(mass)[:,None]*x;projection=inv[:,None]*(q[:,:rank]@(q[:,:rank].T@white))
                compression=float(np.sum(mass[:,None]*(projection-x)**2)/np.sum(white**2))
                compression_difference=abs(compression-row['relative_compression_error'])
                gap=float(eigenvalues[rank]-eigenvalues[rank-1]) if rank<len(mass) else None
                # The projector is gap-sensitive. This tolerance concerns an independent
                # floating-point audit only; the frozen ranks/metrics remain unchanged.
                tolerance=1e-8 if gap is not None and gap<1e-6 else 1e-10
                assert compression_difference<tolerance,(unit,compression_difference,gap)
                if compression_difference>=1e-10:
                    compression_differences.append({'unit':unit,'absolute_difference':compression_difference,'boundary_gap':gap,'audit_tolerance':tolerance})
                for baseline,values in row['compression_controls'].items():
                    training=np.sqrt(mass)[:,None]*data[f"train_x_{row['level']}"]
                    if baseline=='pca':basis=np.linalg.svd(training,full_matrices=False)[0][:,:min(5,samples)]
                    else:basis=np.linalg.qr(np.random.default_rng(seed+row['level']).normal(size=(len(mass),min(5,samples))))[0]
                    reconstructed=inv[:,None]*(basis@(basis.T@white))
                    error_control=float(np.sum(mass[:,None]*(reconstructed-x)**2)/np.sum(white**2))
                    assert abs(error_control-values['relative_mass_error'])<1e-10
                if method=='oracle_true_operator':assert error<1e-20
                rows.append(dict(row,seed=seed,samples=samples,noise=noise,method=method))
        costs.append(dict(record['cost'],seed=seed,samples=samples,noise=noise,method=method))
    assert len(rows)==2688 and len(data_cache)==32
    cells=[]
    for method,samples,noise,groups,topology,level in sorted({tuple(r[k] for k in ['method','samples','noise','groups','topology','level']) for r in rows}):
        subset=[r for r in rows if tuple(r[k] for k in ['method','samples','noise','groups','topology','level'])==(method,samples,noise,groups,topology,level)]
        assert len(subset)==8
        cells.append({'method':method,'samples':samples,'noise':noise,'groups':groups,'topology':topology,'level':level,
                      'instances':8,'relative_prediction_error':float(np.mean([r['relative_prediction_error'] for r in subset])),
                      'relative_compression_error':float(np.mean([r['relative_compression_error'] for r in subset])),
                      'ranks_retained':[r['spectral']['rank_retained'] for r in subset]})
    per_seed=defaultdict(dict);table=[];methods=sorted({r['method'] for r in rows});seeds=sorted({r['seed'] for r in rows})
    for method in methods:
        for seed in seeds:
            selected=[r for r in rows if r['method']==method and r['seed']==seed and r['groups']>16]
            assert len(selected)==32
            per_seed[method][seed]=float(np.mean([r['relative_prediction_error'] for r in selected]))
        method_cost=[r for r in costs if r['method']==method]
        table.append({'method':method,'physical_instances':8,'transfer_cells':256,
                      'mean_transfer_error':float(np.mean(list(per_seed[method].values()))),
                      'training_seconds':sum(r['training_seconds'] for r in method_cost),
                      'constraint_forward_seconds':sum(r['constraint_forward_seconds'] for r in method_cost)})
    rng=np.random.default_rng(240927);contrasts=[]
    for control in methods:
        if control=='both':continue
        diff=np.array([per_seed['both'][s]-per_seed[control][s] for s in seeds])
        interval=np.quantile(rng.choice(diff,size=(10000,8),replace=True).mean(1),[.025,.975]).tolist()
        contrasts.append({'control':control,'both_minus_control':float(diff.mean()),'seed_differences':diff.tolist(),'descriptive_seed_bootstrap95':interval})
    payload={'audit':{'passed':True,'file_hashes':len(checked),'reconstructed_datasets':32,'verified_rows':2688,
                      'true_constraint_checks':true_constraint_checks,'independent_expm_max_difference':maximum_difference,
                      'gap_sensitive_compression_differences':compression_differences,
                      'scope':'NumPy/SciPy cross-implementation check on same host, not independent-person replication'},
             'identity':summary['identity'],'table':table,'cells':cells,'per_seed':dict(per_seed),'contrasts':contrasts,'costs':costs,'raw_rows':rows,
             'scope':'Finite equitable graphs with frozen parametric fields; descriptive eight-instance development evidence.'}
    (OUT/'WFT_RESULTS.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    lines=['# WFT symmetry and resolution-constraint results','','All 160 learned fits and 64 fixed/oracle controls completed. The 2,688 evaluation rows use frozen parameters; no held-size or held-topology refit occurred. Every prediction was checked with a separate NumPy/SciPy matrix-exponential implementation.','',
           '| Method | Mean normalized transfer prediction error | Total training seconds |','|---|---:|---:|']
    for r in table:lines.append(f"| {r['method']} | {r['mean_transfer_error']:.7g} | {r['training_seconds']:.3f} |")
    lines+=['','Transfer averages groups 32/64 across cycle/path, fine/coarse, both sample counts and both noise levels, first within each of eight physical-instance seeds. Lower error is better. The true-operator oracle is privileged and not a qualified learned competitor.','',
            '| Control | Both constraints minus control | Descriptive seed bootstrap 95% interval |','|---|---:|---|']
    for r in contrasts:lines.append(f"| {r['control']} | {r['both_minus_control']:.7g} | {r['descriptive_seed_bootstrap95']} |")
    lines+=['','These are unadjusted development intervals over eight parameter draws. No equivalence, broad graph-population or independently confirmed claim follows. All noise/sample/topology/size/level cells remain in WFT_RESULTS.json, including unfavorable cases.',
            '', '## Contracts and scope','',
            'Reflection and equitable coarsening hold for the declared generator, while the wrong cyclic-shift constraint violates its weights. Fine/coarse model fields are independently parameterized, so the consistency penalty has a real gradient. All learned methods have 11 parameters and the same observations/steps. Frozen transfer uses public coordinates and a shared low-frequency parametric field; it is not arbitrary unseen-weight-distribution generalization.',
            '', 'PSD, mass-weighted Parseval, eigensolver residual and full-basis reconstruction are numerical contracts, not learned transform efficacy. Compression includes fixed geometry, oracle, training-size uncentered PCA and random projection controls. Retained ranks can expand at repeated clusters and are reported per case; no fixed-rank compression advantage is asserted.',
            '', 'Setup, matrix exponential, 16-signal application and eigensolver times and operator bytes are retained per row. Training includes computation of diagnostic penalties even when disabled; constraint-forward time is a subset of training time, not an additional total. Hardware contention is uncontrolled and no equal-wall-time efficiency claim is made. Dense spectral diagnostics stop at 128 nodes.']
    lines+=['','The cross-implementation audit uses 1e-10 absolute agreement for predictions and ordinary compression cases. For compression boundaries with eigengap below 1e-6, the numerical audit tolerance is 1e-8; observed discrepancies above 1e-10 and their gaps are retained in the audit JSON. This post-run verification tolerance addresses projector conditioning and does not change frozen ranks, scores, training or the primary endpoint.']
    (OUT/'WFT_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'audit':payload['audit'],'table':table}))


if __name__=='__main__':main()
