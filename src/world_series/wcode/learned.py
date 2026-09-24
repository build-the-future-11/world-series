"""Learned task-conditioned graph/token scorers for a frozen integer DSL pool.

Scorers accept AST structure and public examples only. Finite-domain signatures
belong to dataset construction/evaluation, never the ranking API.
"""
from dataclasses import dataclass
import hashlib
import math
import numpy as np
import torch
from torch import nn
from world_series.wcode.dsl import Lit,Var,BinOp,If,ast_nodes
from world_series.wcode.interpreter import interpret,Fuel,validate_ast

DOMAIN=tuple(range(-8,9))
OPS=['lit','var','+','-','*','//','%','<','if']
MODES=['relational','flat','token','no_relations','no_hierarchy','no_task']
RELATIONS=6


def canonical_signature(program):
    validate_ast(program)
    return tuple(interpret(program,{'x':x},Fuel(128)) for x in DOMAIN)


def program_pool():
    x=Var('x');raw=[]
    for a in range(-2,3):
        for b in range(-3,4):
            for c in range(-2,3):
                p=BinOp('+',BinOp('+',BinOp('*',Lit(a),BinOp('*',x,x)),BinOp('*',Lit(b),x)),Lit(c))
                raw.append(('polynomial',p))
    for modulus in [2,3,4,5]:
        for a in [-2,-1,1,2]:
            for b in [-2,0,2]:
                for op in ['%','//']:
                    raw.append(('modular' if op=='%' else 'floor',BinOp('+',BinOp('*',Lit(a),BinOp(op,x,Lit(modulus))),Lit(b))))
    for a in [-2,-1,1,2]:
        for b in [-2,0,2]:
            raw.append(('cubic',BinOp('+',BinOp('*',Lit(a),BinOp('*',BinOp('*',x,x),x)),Lit(b))))
    for threshold in [-3,-1,1,3]:
        for a in [-2,-1,1,2]:
            for b in [-2,0,2]:
                raw.append(('conditional',If(BinOp('<',x,Lit(threshold)),BinOp('+',x,Lit(a)),BinOp('*',x,Lit(b)))))
    grouped={}
    for category,p in raw:
        signature=canonical_signature(p)
        record=grouped.get(signature)
        if record is None or (ast_nodes(p),repr(p))<(ast_nodes(record['program']),repr(record['program'])):
            grouped[signature]={'program':p,'signature':signature,'category':category}
    rows=[]
    for signature,record in grouped.items():
        identity=hashlib.sha256(','.join(map(str,signature)).encode()).hexdigest()
        bucket=int(identity[:8],16)%10
        role='evaluation_composition' if record['category'] in {'cubic','conditional'} else 'train' if bucket<6 else 'selection' if bucket<8 else 'evaluation_family'
        rows.append(dict(record,identity=identity,role=role))
    return sorted(rows,key=lambda r:r['identity'])


def structure(program):
    features=[];edges=[[] for _ in range(RELATIONS)]
    def visit(node,depth):
        index=len(features)
        op='lit' if isinstance(node,Lit) else 'var' if isinstance(node,Var) else node.op if isinstance(node,BinOp) else 'if'
        feature=[float(op==token) for token in OPS]+[float(node.value)/5 if isinstance(node,Lit) else 0.,depth/6]
        features.append(feature)
        children=[]
        if isinstance(node,BinOp):children=[node.left,node.right]
        elif isinstance(node,If):children=[node.cond,node.then,node.else_]
        indices=[visit(child,depth+1) for child in children]
        for order,child in enumerate(indices):
            edges[order].append((child,index))
            edges[3].append((index,child))
        for a,b in zip(indices,indices[1:]):edges[4].append((a,b));edges[5].append((b,a))
        return index
    visit(program,0)
    return features,edges


@dataclass
class StructureBatch:
    features:torch.Tensor
    membership:torch.Tensor
    roots:torch.Tensor
    sizes:torch.Tensor
    edges:list
    token_edges:list
    candidate_count:int


def pack_programs(programs):
    all_features=[];membership=[];roots=[];sizes=[];edges=[[] for _ in range(RELATIONS)];token=[[] for _ in range(RELATIONS)]
    for candidate,program in enumerate(programs):
        features,relations=structure(program);offset=len(all_features);n=len(features)
        roots.append(offset);sizes.append(n);all_features.extend(features);membership.extend([candidate]*n)
        for r in range(RELATIONS):edges[r].extend((a+offset,b+offset) for a,b in relations[r])
        for r,delta in enumerate([-3,-2,-1,1,2,3]):
            token[r].extend((offset+i+delta,offset+i) for i in range(n) if 0<=i+delta<n)
    def tensor_edges(rows):return [torch.tensor(e,dtype=torch.long).reshape(-1,2).T.contiguous() for e in rows]
    return StructureBatch(torch.tensor(all_features,dtype=torch.float32),torch.tensor(membership),torch.tensor(roots),
                          torch.tensor(sizes,dtype=torch.float32),tensor_edges(edges),tensor_edges(token),len(programs))


def public_tensor(examples):
    """Public (x,y) pairs; no held outputs or program identities accepted."""
    values=np.asarray(examples,dtype=np.float32)
    if values.shape[-1]!=2 or not np.isfinite(values).all():raise ValueError('Finite public input/output pairs required')
    scaled=values.copy();scaled[...,0]/=8
    scaled[...,1]=np.sign(values[...,1])*np.log1p(np.abs(values[...,1]))/np.log(1025.)
    return torch.from_numpy(scaled)


class ProgramScorer(nn.Module):
    def __init__(self,mode='relational',width=24,layers=3):
        super().__init__()
        if mode not in MODES:raise ValueError(mode)
        self.mode=mode;self.width=width
        self.input=nn.Linear(len(OPS)+2,width)
        self.self_layers=nn.ModuleList(nn.Linear(width,width) for _ in range(layers))
        self.relation_layers=nn.ModuleList(nn.ModuleList(nn.Linear(width,width) for _ in range(RELATIONS)) for _ in range(layers))
        self.pool=nn.Linear(2*width,width)
        self.example=nn.Sequential(nn.Linear(2,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh())
        self.task=nn.Linear(width,width)

    @staticmethod
    def mean_pool(h,batch):
        result=h.new_zeros(batch.candidate_count,h.shape[-1]);result.index_add_(0,batch.membership,h)
        return result/batch.sizes[:,None]

    def encode(self,batch):
        h=torch.tanh(self.input(batch.features))
        for self_layer,layers in zip(self.self_layers,self.relation_layers):
            aggregate=self_layer(h)
            for relation,layer in enumerate(layers):
                if self.mode=='flat':
                    # Active nonlinear branches, no dormant padding parameters.
                    message=torch.tanh(layer(h))
                else:
                    edges=batch.token_edges[relation] if self.mode=='token' else batch.edges[relation]
                    if self.mode=='no_relations':edges=torch.cat(batch.edges,dim=1)
                    source,destination=edges
                    incoming=h.new_zeros(h.shape);count=h.new_zeros(len(h),1)
                    incoming.index_add_(0,destination,h[source]);count.index_add_(0,destination,h.new_ones(len(destination),1))
                    message=torch.tanh(layer(incoming/count.clamp_min(1)))
                aggregate=aggregate+message/RELATIONS
            h=torch.tanh(aggregate)
        mean=self.mean_pool(h,batch)
        root=mean if self.mode=='no_hierarchy' else h[batch.roots]
        return torch.tanh(self.pool(torch.cat([root,mean],-1)))

    def forward(self,batch,public):
        if public.ndim==2:public=public[None]
        query=self.example(public).mean(1)
        if self.mode=='no_task':query=query*0
        query=torch.tanh(self.task(query))
        return query@self.encode(batch).T/math.sqrt(self.width)
