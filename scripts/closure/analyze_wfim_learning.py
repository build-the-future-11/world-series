#!/usr/bin/env python3
"""Reload every completed WFIM model and verify saved predictions and metrics."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import torch
from world_series.wfim.learning import CompositionModel


def main(root, output):
    if output.exists(): raise FileExistsError(output)
    protocol=json.loads((root/"protocol.json").read_text())
    for name,digest in protocol["source"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:raise ValueError(f"source changed: {name}")
    data=json.loads((root/"data.json").read_text());words=data["words"];splits=data["splits"]
    tokens=torch.full((len(words),8),-1,dtype=torch.long)
    for i,w in enumerate(words):tokens[i,:len(w)]=torch.tensor(w)
    records=json.loads((root/"summary.json").read_text())
    assert len(records)==80
    seen=set()
    for row in records:
        key=(row["seed"],row["task"],row["kind"]);assert key not in seen;seen.add(key)
        name="-".join(map(str,key));saved=json.loads((root/f"{name}.json").read_text())
        model=CompositionModel(row["kind"])
        model.load_state_dict(torch.load(root/f"{name}.pt",weights_only=True))
        with torch.no_grad():pred=model(tokens);norm=model.encode(tokens).abs().sum(-1)
        assert torch.equal(pred,torch.tensor(saved["predictions"],dtype=torch.float64))
        assert torch.equal(norm,torch.tensor(saved["norm_l1"],dtype=torch.float64))
        target=torch.tensor([sum(tuple(w[i:i+3])==(0,0,1) for i in range(len(w)-2))/max(1,len(w)-2) if row["task"]=="order" else sum(w)/len(w) for w in words],dtype=torch.float64)
        assert target.tolist()==saved["targets"]
        for split,score in row["mse"].items():
            mask=torch.tensor([s==split for s in splits]);assert float((pred[mask]-target[mask]).square().mean())==score
        assert row["storage"]==model.storage()
    summary=[]
    for task in ["order","count"]:
        for kind in protocol["kinds"]:
            group=[r for r in records if r["task"]==task and r["kind"]==kind]
            summary.append(dict(task=task,kind=kind,models=len(group),
                template_mse=float(np.mean([r["mse"]["template"] for r in group])),
                length_mse=float(np.mean([r["mse"]["length"] for r in group])),
                payload_bytes=group[0]["storage"]["total_payload_bytes"],
                training_seconds=float(np.mean([r["training_ns"] for r in group]))/1e9))
    result=dict(models_reloaded=80,predictions_replayed=80*len(words),exact_predictions=True,exact_targets=True,
                source_hashes_verified=True,summary=summary,
                limitations=["same-host replay, not independent confirmation","selection histories retain training losses and selected score, not every checkpoint score","common cap with unequal used bytes; not exact byte-matched capacity","two fixed tasks, not a sampled family population"],
                artifacts={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.is_file()})
    output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(summary))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();main(a.root,a.output)
