# 08 — CWLNN
## Working research title
Sparse Multiscale World Representations with Budgeted Local-to-Global Computation.

Retain the user's CWLNN brand (“Convoluted World Large Neural Network”) without treating “large” as proof of capability. The first model is deliberately small. Its research purpose is a measurable hierarchy and routing mechanism, not another giant language-model pretraining project.

## Prior work and narrow claim

Perceiver IO [R32], Switch Transformers [R33], DiffPool [R34], Mamba [R35] and equivariant graph processing [R09] cover bottlenecks, sparse routing, hierarchy and efficient computation. The proposed experiment asks whether a genuinely sparse multiscale relational architecture yields better accuracy-versus-cost and size transfer on a chosen task than matched flat/local controls. Adding all known efficient mechanisms is not by itself a novel contribution.

## Graph hierarchy

Represent a sample with sparse levels `G_0,…,G_L` and parent maps `p_l:[N_l]→[N_{l+1}]`. Begin with a supplied/public deterministic structural hierarchy; do not use target labels to build it. Each level performs local relation-aware aggregation:

`h_i'=σ(W_self h_i+Σ_{j∈N(i)}K(e_ij)h_j)`.

Pool children by normalized sums/means using parent indices, then broadcast coarse updates back through the same mapping with a residual connection. Keep level widths and aggregation normalization explicit. A parent with many children should not gain an unintended magnitude advantage unless the task intentionally encodes count.

Use sparse index/scatter operations; no dense N×N soft assignment or adjacency in the claimed sparse path. A dense DiffPool-like baseline may be useful for accuracy, but its cost must be measured rather than hidden inside a “linear” complexity label.

## Routing scope

The reference always processes a fixed hierarchy. The next candidate may learn which nodes require expensive fine-scale updates, using local uncertainty/disagreement/budget features. Define a budget ledger and count routing itself. Begin with a fixed threshold control and a learned score with an explicit top-k budget. Training through hard selection may use a surrogate/straight-through estimator, but document that it is not an exact gradient of the discrete routing objective.

Expert mixtures and variable-depth computation are deferred until the hierarchy-alone ablation is interpretable. Avoid simultaneously changing hierarchy, width, routing and loss and then attributing gains to one named mechanism.

## Complexity statement and assumptions

If `N_l≤N/2^l`, bounded degree k, fixed width h and constant updates per level, aggregation/feature work is `O(Σ_l(N_lkh+N_lh²))=O(Nkh+Nh²)`. Building the hierarchy, sorting, dynamic routing and output decoding add work. Include those costs. An all-pairs attention step anywhere in the path can reintroduce quadratic interactions. Linear asymptotic scaling does not guarantee a faster small-N implementation.

Permutation behavior requires care. A hierarchy built by arbitrary input node order may break equivariance. Test a node permutation with edges, parent maps and public structural labels transformed consistently. Do not claim equivariance when only features are permuted and the hierarchy remains attached to old indices. Learned hierarchy construction later needs its own equivariance analysis.

## Code units and shapes

| File | Responsibility |
|---|---|
| graphs.py | Sparse graph batches and public hierarchy metadata |
| hierarchy.py | Deterministic coarsening, parent maps and sparse edges |
| local.py | Bounded-degree relational updates |
| pool.py | Count-aware pooling and consistent broadcast |
| routing.py | Fixed and learned budgeted selection with cost counters |
| model.py | Local/coarse/residual composition and readout |
| tasks.py | Multiscale graph signals and held-out graph sizes |
| baselines.py | Flat GNN/local CNN, small dense attention and relevant bottlenecks |
| evaluate.py | Accuracy, latency, memory and size-transfer curves |
| adapter.py | `encode_multiscale_world` |

`GraphLevel` contains features[N_l,H_l], edge_index[2,E_l], edge features[E_l,R], batch indices and parent_index[N_l]. A hierarchy validates every parent bound and batch boundary. `RoutingReceipt` stores selected nodes, requested/actual budget and dropped operations. Budget exhaustion cannot silently truncate a graph while reporting a normal result.

## Initial tasks and fair controls

Start with graph-signal prediction requiring both local and global information, such as multiscale diffusion or a compositional aggregation target on a public hierarchy. Train on small graphs and hold out larger graph instances and generator parameters. A task generated from exactly the candidate's architecture can favor it artificially, so include at least one task without an aligned hierarchy and report this limitation.

Compare a flat message-passing model, an equally wide local model, fixed hierarchical processing, the proposed routed hierarchy and a small dense-attention baseline at feasible sizes. Perceiver/Mamba-inspired alternatives are optional on genuinely common inputs/tasks; do not reshape graphs arbitrarily merely to claim a named-model comparison. Match parameter ranges and separately report total measured compute. Give controls access to the same public coordinates/hierarchy information where relevant.

Primary: error/accuracy at a declared measured inference-time budget on held-out graph sizes. Secondary: training cost, memory, preprocessing cost, robustness to node relabeling, performance on nonhierarchical controls and routing utilization. Save raw timings with warmup policy and synchronization; do not compare unsynchronized accelerator timing against synchronous CPU wall-clock.

## Tests

Sparse aggregation equals a tiny dense reference; pooling and broadcast shape/value checks; no cross-graph edges in batches; parent bounds; count normalization; node-permutation consistency with transformed hierarchy; deterministic routing under tied priorities; hard selected-node cap; empty/single-node graph behavior; disabled routing recovers reference hierarchy; no hidden dense adjacency at large-N test; gradient flow through supported surrogate; explicit reporting of unsupported device operations.

Use complexity counters and allocation checks as structural tests, plus measured timing as an empirical result. A test asserting that “our model is always faster” would be brittle and scientifically unjustified.

## Sunday slice and extension

Demonstrate a small multiscale forward/training pass, its routing receipt and a matched baseline comparison if completed. Defer billion-parameter scale, multimodal pretraining, arbitrary conceptual neighborhoods, universal language-model claims and making every World Series module depend on this backbone. Only after the standalone result passes should WCode or Q-APEN receive a controlled encoder-swap experiment.


---
