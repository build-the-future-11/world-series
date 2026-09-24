#!/usr/bin/env python3
import argparse, hashlib, itertools, json, time
from pathlib import Path
import torch
from world_series.wfim.learning import CompositionModel


def save(path,data):path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")


def main(output):
    output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1)
    seeds=[3109,3119,3121,3137,3163,3167,3169,3181]
    kinds=["learned_coordinates","identity_coordinates","vector","bilinear","binding"]
    source=list(Path("src/world_series/wfim").glob("*.py"))+[Path(__file__)]
    save(output/"protocol.json",dict(seeds=seeds,kinds=kinds,steps=150,checkpoints=[50,100,150],
        optimizer="Adam lr 0.01, full batch, float64 CPU",degree=6,decoder_width=32,storage_cap=1048576,
        primary="held-template and held-length MSE; finite exhaustive binary words, not independent real datasets",
        tasks=["frequency of contiguous 001","fraction of ones (order-insensitive control)"],
        split="length 2..6, prefix 001 or 110 held templates; other words sha256 first byte modulo 5 zero selection; length 7..8 held length",
        cost="training selection and inference measured; payload and actual checkpoint bytes retained",
        caveat="common byte cap and equal decoder/representation dimension; unequal encoder capacity disclosed",
        confirmation="DRAFT_NOT_AUTHORIZED",source={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in source}))
    words=[w for n in range(2,9) for w in itertools.product(range(2),repeat=n)]
    splits=[]
    for w in words:
        if len(w)>6:split="length"
        elif w[:3] in [(0,0,1),(1,1,0)]:split="template"
        elif hashlib.sha256(bytes(w)).digest()[0]%5==0:split="selection"
        else:split="train"
        splits.append(split)
    tokens=torch.full((len(words),8),-1,dtype=torch.long)
    for i,w in enumerate(words):tokens[i,:len(w)]=torch.tensor(w)
    save(output/"data.json",dict(words=words,splits=splits))
    masks={s:torch.tensor([v==s for v in splits]) for s in set(splits)}
    results=[]
    for seed in seeds:
      for task in ["order","count"]:
        target=torch.tensor([sum(w[i:i+3]==(0,0,1) for i in range(len(w)-2))/max(1,len(w)-2) if task=="order" else sum(w)/len(w) for w in words],dtype=torch.float64)
        for kind in kinds:
          torch.manual_seed(seed);model=CompositionModel(kind)
          storage=model.storage()
          if storage["total_payload_bytes"]>1048576:raise ValueError("storage cap")
          optimizer=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=0.01)
          history=[];selected=None;best=float("inf")
          begin=time.perf_counter_ns()
          for step in range(1,151):
            optimizer.zero_grad();loss=(model(tokens[masks["train"]])-target[masks["train"]]).square().mean();loss.backward();optimizer.step()
            history.append(float(loss.detach()))
            if step in [50,100,150]:
              with torch.no_grad():score=float((model(tokens[masks["selection"]])-target[masks["selection"]]).square().mean())
              if score<best:best=score;selected={k:v.detach().clone() for k,v in model.state_dict().items()};selected_step=step
          train_ns=time.perf_counter_ns()-begin;model.load_state_dict(selected)
          name=f"{seed}-{task}-{kind}"
          torch.save(selected,output/f"{name}.pt")
          begin=time.perf_counter_ns()
          with torch.no_grad():pred=model(tokens);norm=model.encode(tokens).abs().sum(-1)
          infer_ns=time.perf_counter_ns()-begin
          row=dict(seed=seed,task=task,kind=kind,selected_step=selected_step,selection_mse=best,training_ns=train_ns,inference_and_norm_ns=infer_ns,
                   storage=storage,checkpoint_bytes=(output/f"{name}.pt").stat().st_size,
                   mse={s:float((pred[m]-target[m]).square().mean()) for s,m in masks.items()})
          save(output/f"{name}.json",dict(**row,history=history,predictions=pred.tolist(),targets=target.tolist(),norm_l1=norm.tolist()))
          results.append(row);print(name,flush=True)
    save(output/"summary.json",results)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);main(p.parse_args().output)
