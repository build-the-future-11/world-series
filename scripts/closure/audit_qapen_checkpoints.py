"""Replay locally generated, hash-verified checkpoints; never load foreign pickle."""
import hashlib
import json
from pathlib import Path
import pickle
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(Path(__file__).resolve().parent)]
from world_series.qapen.causal import CausalLifecycle
from qapen_study import RollingRidge


def main():
    directory=ROOT/'campaigns/qapen-lifecycle-v1'
    summary=json.loads((directory/'summary.json').read_text());checked=[]
    centers=json.loads((directory/'codebook.json').read_text())['centers']
    for receipt in summary['receipts']:
        filename=next(name for name in receipt['files'] if name.endswith('.pkl'))
        path=directory/filename
        assert hashlib.sha256(path.read_bytes()).hexdigest()==receipt['files'][filename]
        # These pickle files were produced in this task and verified against its receipt.
        saved=pickle.loads(path.read_bytes())
        if saved['kind']=='causal_lifecycle':
            model=saved['model'];copy=CausalLifecycle.restore(model.checkpoint())
            assert np.array_equal(model.quantizer.centers,centers)
            assert set(model.models)==set(model.optimizers)==set(model.metadata)
            for identity,optimizer in model.optimizers.items():
                assert next(model.models[identity].parameters()) is optimizer.param_groups[0]['params'][0]
        else:
            model=RollingRidge();model.__dict__=saved['state']
            copy=pickle.loads(pickle.dumps(model))
        assert model.pending is None
        for context,target in [([0.,.3],.8),([-.4,1.2],-.2)]:
            assert model.predict(context)==copy.predict(context)
            assert model.observe(target)==copy.observe(target)
        checked.append(filename)
    result={'passed':True,'verified_checkpoints':len(checked),'continuation_predictions':len(checked)*2,
            'checks':['frozen codebook','module/optimizer parameter references','exact deterministic continuation'],
            'scope':'Same-host mechanism checkpoint check on public fixtures, not a new efficacy evaluation',
            'checkpoint_files':checked}
    (ROOT/'docs/closure/QAPEN_CHECKPOINT_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checkpoint_files'}))


if __name__=='__main__':main()
