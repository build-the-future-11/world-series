#!/usr/bin/env python3
"""Plots from generated CSVs only. Run in the isolated analysis environment."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'docs/execution/development-v2'
rows=list(csv.DictReader((ROOT/'digits_per_seed.csv').open()))
methods=['sgd','momentum','adamw','official_celo2','full','reset_state','feedforward','no_budget','no_gates','initialization_only']
fig,axes=plt.subplots(1,2,figsize=(13,6),layout='constrained')
for index,method in enumerate(methods):
    selected=[r for r in rows if r['method']==method and r['horizon']=='32']
    values=np.array([float(r['auc']) for r in selected]); accuracy=np.array([float(r['accuracy']) for r in selected])
    color='#006d77' if method=='full' else '#52677d'
    axes[0].scatter(values,np.full(len(values),index)+np.linspace(-.12,.12,len(values)),s=23,alpha=.65,color=color)
    axes[0].plot([values.mean()],[index],'|',markersize=20,color='#111111')
    axes[1].scatter(accuracy*100,np.full(len(accuracy),index)+np.linspace(-.12,.12,len(accuracy)),s=23,alpha=.65,color=color)
    axes[1].plot([accuracy.mean()*100],[index],'|',markersize=20,color='#111111')
for ax in axes:
    ax.set_yticks(range(len(methods)),[m.replace('_',' ') for m in methods]);ax.invert_yaxis()
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.2)
axes[0].set_xlabel('Normalized loss AUC over 32 adaptation steps (lower is better)')
axes[1].set_xlabel('Held writer accuracy, % (higher is better)')
fig.suptitle('Natural digit development: each dot is one seed mean\nEight seeds share one dataset; no confirmatory claim',fontsize=14)
for suffix in ['svg','pdf','png']: fig.savefig(ROOT/f'natural-digits-comparison.{suffix}',dpi=160)
plt.close(fig)
print(ROOT/'natural-digits-comparison.pdf')
