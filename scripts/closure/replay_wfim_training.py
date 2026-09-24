#!/usr/bin/env python3
"""Reconstruct all selection checkpoints without altering the original campaign."""
import argparse, hashlib, json
from pathlib import Path
import torch
from world_series.wfim.learning import CompositionModel


def main(root,output):
    output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1)
    protocol=json.loads((root/"protocol.json").read_text())
    for file,digest in protocol["source"].items():
        assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==digest
    data=json.loads((root/"data.json").read_text());words=data["words"]
    tokens=torch.full((len(words),8),-1,dtype=torch.long)
    for i,w in enumerate(words):tokens[i,:len(w)]=torch.tensor(w)
    masks={s:torch.tensor([v==s for v in data["splits"]]) for s in ["train","selection"]}
    receipts=[]
    for row in json.loads((root/"summary.json").read_text()):
        name=f"{row['seed']}-{row['task']}-{row['kind']}"
        saved=json.loads((root/f"{name}.json").read_text())
        target=torch.tensor(saved["targets"],dtype=torch.float64)
        torch.manual_seed(row["seed"]);model=CompositionModel(row["kind"])
        optimizer=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=0.01)
        best=float("inf");scores=[]
        for step in range(1,151):
            optimizer.zero_grad();loss=(model(tokens[masks["train"]])-target[masks["train"]]).square().mean()
            assert float(loss.detach())==saved["history"][step-1],(name,step,"loss mismatch")
            loss.backward();optimizer.step()
            if step in [50,100,150]:
                with torch.no_grad():score=float((model(tokens[masks["selection"]])-target[masks["selection"]]).square().mean())
                scores.append(dict(step=step,mse=score))
                if score<best:
                    best=score;chosen=step;state={k:v.detach().clone() for k,v in model.state_dict().items()}
        original=torch.load(root/f"{name}.pt",weights_only=True)
        assert chosen==saved["selected_step"] and best==saved["selection_mse"]
        assert state.keys()==original.keys() and all(torch.equal(v,original[k]) for k,v in state.items())
        receipt=dict(name=name,training_losses_exact=True,selected_state_exact=True,selected_step=chosen,selection_scores=scores,
                     original_checkpoint_sha256=hashlib.sha256((root/f"{name}.pt").read_bytes()).hexdigest())
        (output/f"{name}.json").write_text(json.dumps(receipt,indent=2)+"\n")
        receipts.append(receipt);print(name,flush=True)
    (output/"summary.json").write_text(json.dumps(dict(models=len(receipts),training_updates=150*len(receipts),selection_scores=3*len(receipts),all_exact=True,scope="same-host replay; not independent confirmation"),indent=2)+"\n")


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();main(a.root,a.output)
