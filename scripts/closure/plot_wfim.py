#!/usr/bin/env python3
"""Plot paired seed outcomes; no population confidence claim."""
import hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root=Path("campaigns/wfim-coordinate-development-v1")
rows=json.loads((root/"summary.json").read_text())
fig,axes=plt.subplots(1,2,figsize=(8,3.4),layout="constrained")
for ax,split,title in zip(axes,["template","length"],["Held templates","Held lengths"]):
    group=[r for r in rows if r["task"]=="order"]
    for seed in sorted({r["seed"] for r in group}):
        vals=[next(r["mse"][split] for r in group if r["seed"]==seed and r["kind"]==kind) for kind in ["identity_coordinates","learned_coordinates"]]
        ax.plot([0,1],vals,"o-",color="#516b91",alpha=.65,linewidth=1)
    ax.set_xticks([0,1],["Identity","Learned"]);ax.set_title(title);ax.set_ylabel("Mean squared error");ax.set_xlim(-.3,1.3);ax.grid(axis="y",alpha=.2)
fig.suptitle("WFIM: coordinate learning on ordered-pattern frequency")
out=Path("paper/figures");out.mkdir(exist_ok=True)
fig.savefig(out/"wfim-paired-seeds.png",dpi=220)
fig.savefig(out/"wfim-paired-seeds.svg")
(out/"wfim-paired-seeds.json").write_text(json.dumps({"source":str(root/"summary.json"),"sha256":hashlib.sha256((root/"summary.json").read_bytes()).hexdigest(),"caption":"Each line is one paired training seed on the same fixed finite task. Eight seeds do not represent eight independent task families. Lower is better. No population confidence interval is shown."},indent=2)+"\n")
