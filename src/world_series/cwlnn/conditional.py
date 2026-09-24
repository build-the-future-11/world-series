"""Trained sparse hierarchy and genuinely conditional fine-node refinement.

Public parent labels and stable node identifiers are inputs, never inferred
from targets. Hard routing uses a selected-node straight-through surrogate
during training; it is not an exact gradient of the top-k decision.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import torch


@dataclass
class SparseWorld:
    x: torch.Tensor
    edges: torch.Tensor
    parent: torch.Tensor
    batch: torch.Tensor
    node_id: torch.Tensor

    def validate(self):
        n = len(self.x)
        if self.x.ndim != 2 or self.x.shape[1] != 4 or not torch.isfinite(self.x).all():
            raise ValueError('Expected finite [N,4] public node features')
        if self.x.device.type != 'cpu':
            raise NotImplementedError('Reference implementation supports CPU only')
        if self.edges.ndim != 2 or self.edges.shape[0] != 2:
            raise ValueError('Expected [2,E] sparse edges')
        for value in (self.edges, self.parent, self.batch, self.node_id):
            if value.dtype != torch.long or value.device != self.x.device:
                raise ValueError('CPU int64 structural metadata required')
        if any(value.shape != (n,) for value in (self.parent, self.batch, self.node_id)):
            raise ValueError('Invalid node metadata shape')
        if self.edges.numel() and (int(self.edges.min()) < 0 or int(self.edges.max()) >= n):
            raise ValueError('Edge outside graph')
        if n:
            if int(self.parent.min()) < 0 or int(self.batch.min()) < 0:
                raise ValueError('Negative parent or batch')
            parents = torch.unique(self.parent)
            if not torch.equal(parents, torch.arange(len(parents))):
                raise ValueError('Parents must be contiguous with no empty groups')
            if self.edges.numel() and not torch.equal(self.batch[self.edges[0]], self.batch[self.edges[1]]):
                raise ValueError('Cross-graph edge')
            for group in torch.unique(self.batch):
                ids = self.node_id[self.batch == group]
                if len(torch.unique(ids)) != len(ids):
                    raise ValueError('Node identifiers must be unique within each graph')
            # Scatter-reduce avoids a per-parent scan, including on large graphs.
            lo = torch.full((len(parents),), int(self.batch.max()) + 1, dtype=torch.long)
            hi = torch.full((len(parents),), -1, dtype=torch.long)
            lo.scatter_reduce_(0, self.parent, self.batch, reduce='amin', include_self=True)
            hi.scatter_reduce_(0, self.parent, self.batch, reduce='amax', include_self=True)
            if not torch.equal(lo, hi):
                raise ValueError('Parent crosses graph boundary')


def mean_aggregate(x, edges):
    """Incoming normalized sum, with isolated nodes receiving zero messages."""
    out = torch.zeros_like(x)
    degree = x.new_zeros(len(x))
    if edges.numel():
        out.index_add_(0, edges[1], x[edges[0]])
        degree.index_add_(0, edges[1], torch.ones(len(edges[1]), dtype=x.dtype))
    return out / degree.clamp_min(1)[:, None]


def pool(x, parent):
    count = int(parent.max()) + 1 if len(parent) else 0
    out = x.new_zeros((count, x.shape[1]))
    sizes = x.new_zeros(count)
    if len(parent):
        out.index_add_(0, parent, x)
        sizes.index_add_(0, parent, torch.ones(len(parent), dtype=x.dtype))
    return out / sizes.clamp_min(1)[:, None]


def coarse_edges(edges, parent):
    """Actual quotient adjacency, not an assumed path after coarsening."""
    if not edges.numel():
        return edges.new_empty((2, 0))
    pairs = parent[edges]
    pairs = pairs[:, pairs[0] != pairs[1]]
    return torch.unique(pairs, dim=1)


def select(scores, batch, node_id, fraction):
    if not 0 <= fraction <= 1 or not torch.isfinite(scores).all():
        raise ValueError('Finite scores and fraction in [0,1] required')
    chosen = []
    budgets = []
    for group in torch.unique(batch, sorted=True):
        members = torch.where(batch == group)[0]
        # Stable ID is transformed with the graph: ties do not depend on row order.
        ordered = members[torch.argsort(node_id[members], stable=True)]
        ordered = ordered[torch.argsort(scores[ordered], descending=True, stable=True)]
        budget = math.floor(fraction * len(members))
        chosen.append(ordered[:budget])
        budgets.append(budget)
    return (torch.cat(chosen) if chosen else batch.new_empty(0)), budgets


class ConditionalWorld(torch.nn.Module):
    def __init__(self, context='hierarchy', routing='none', width=24, attention_limit=512):
        super().__init__()
        if context not in ('hierarchy', 'flat5', 'local', 'attention') or routing not in ('none', 'learned', 'norm', 'random'):
            raise ValueError('Unknown context/routing')
        self.context, self.routing, self.width = context, routing, width
        self.attention_limit = attention_limit
        # Every control gets the same raw public parent mean, as well as x.
        self.encoder = torch.nn.Linear(8, width)
        self.local = torch.nn.Linear(2 * width, width)
        self.context_layer = torch.nn.Linear(2 * width, width)
        self.cheap_readout = torch.nn.Linear(2 * width, 1)
        self.refine = torch.nn.Sequential(torch.nn.Linear(3 * width, 4 * width), torch.nn.SiLU(),
                                          torch.nn.Linear(4 * width, width), torch.nn.SiLU(),
                                          torch.nn.Linear(width, 1))
        self.router = torch.nn.Sequential(torch.nn.Linear(4, 8), torch.nn.Tanh(), torch.nn.Linear(8, 1)) if routing == 'learned' else None

    def forward(self, graph, fraction=1., explore=False):
        graph.validate()
        x, edges, parent = graph.x, graph.edges, graph.parent
        n = len(x)
        if not 0 <= fraction <= 1:
            raise ValueError('Budget fraction outside [0,1]')
        if not n:
            return x.new_empty(0), {'nodes': 0, 'selected': 0, 'refine_rows': 0, 'attention_pairs': 0, 'budgets': []}
        pooled_raw = pool(x, parent)[parent]
        h = torch.nn.functional.silu(self.encoder(torch.cat([x, pooled_raw], dim=1)))
        h = torch.nn.functional.silu(self.local(torch.cat([h, mean_aggregate(h, edges)], dim=1)))
        attention_pairs = 0
        quotient_edges = 0
        if self.context == 'hierarchy':
            coarse = pool(h, parent)
            ce = coarse_edges(edges, parent)
            quotient_edges = ce.shape[1]
            context = torch.nn.functional.silu(self.context_layer(torch.cat([coarse, mean_aggregate(coarse, ce)], dim=1)))[parent]
            context_rows = len(coarse)
        elif self.context in ('flat5', 'local'):
            message = h
            for _ in range(3 if self.context == 'flat5' else 1):
                message = mean_aggregate(message, edges)
            context = torch.nn.functional.silu(self.context_layer(torch.cat([h, message], dim=1)))
            context_rows = n
        else:
            message = torch.zeros_like(h)
            for group in torch.unique(graph.batch):
                ix = torch.where(graph.batch == group)[0]
                if len(ix) > self.attention_limit:
                    raise ValueError('Declared dense attention size limit exceeded')
                weights = torch.softmax(h[ix] @ h[ix].T / math.sqrt(self.width), dim=1)
                message[ix] = weights @ h[ix]
                attention_pairs += len(ix) ** 2
            context = torch.nn.functional.silu(self.context_layer(torch.cat([h, message], dim=1)))
            context_rows = n
        cheap = self.cheap_readout(torch.cat([h, context], dim=1)).squeeze(-1)
        neighbor = mean_aggregate(h, edges)
        if self.routing == 'none':
            selected = torch.arange(n)
            budgets = [int((graph.batch == group).sum()) for group in torch.unique(graph.batch)]
            scores = None
        else:
            if self.routing == 'learned':
                features = torch.stack([(h.square().mean(dim=1)+1e-12).sqrt(), (context.square().mean(dim=1)+1e-12).sqrt(),
                                        ((h - neighbor).square().mean(dim=1)+1e-12).sqrt(), h.new_full((n,), fraction)], dim=1)
                scores = self.router(features).squeeze(-1)
                priority = scores + .2 * torch.randn_like(scores) if explore and self.training else scores
            elif self.routing == 'norm':
                scores = None
                priority = (h - neighbor).square().sum(dim=1)
            else:
                scores = None
                # Stable deterministic permutation-like priority, invariant to row order.
                priority = ((graph.node_id * 1103515245 + 12345) % 2147483647).to(h.dtype)
            selected, budgets = select(priority, graph.batch, graph.node_id, fraction)
        output = cheap.clone()
        if len(selected):
            # Expensive refinement is evaluated ONLY on selected rows.
            residual = self.refine(torch.cat([h[selected], context[selected], neighbor[selected]], dim=1)).squeeze(-1)
            if self.router is not None and self.training:
                soft = torch.sigmoid(scores[selected])
                residual = residual * (1 + soft - soft.detach())
            output = output.index_add(0, selected, residual)
        receipt = {'nodes': n, 'fine_edges': edges.shape[1], 'coarse_edges': quotient_edges,
                   'context_rows': context_rows, 'selected': len(selected), 'refine_rows': len(selected),
                   'attention_pairs': attention_pairs, 'budgets': budgets,
                   'selected_ids': graph.node_id[selected].detach().tolist(),
                   'refine_linear_multiply_adds': len(selected) * (3*self.width*4*self.width + 4*self.width*self.width + self.width),
                   'router_rows': n if self.router is not None else 0}
        return output, receipt


def permute(graph, order):
    inverse = torch.empty_like(order)
    inverse[order] = torch.arange(len(order))
    return SparseWorld(graph.x[order], inverse[graph.edges], graph.parent[order], graph.batch[order], graph.node_id[order])


def batch_graphs(graphs):
    xs, edges, parents, batches, ids = [], [], [], [], []
    node_offset = parent_offset = graph_offset = 0
    for graph in graphs:
        graph.validate()
        xs.append(graph.x)
        edges.append(graph.edges + node_offset)
        parents.append(graph.parent + parent_offset)
        batches.append(graph.batch + graph_offset)
        ids.append(graph.node_id)
        node_offset += len(graph.x)
        parent_offset += int(graph.parent.max()) + 1 if len(graph.parent) else 0
        graph_offset += int(graph.batch.max()) + 1 if len(graph.batch) else 0
    if not graphs:
        raise ValueError('No graphs to batch')
    return SparseWorld(torch.cat(xs), torch.cat(edges, dim=1), torch.cat(parents), torch.cat(batches), torch.cat(ids))
