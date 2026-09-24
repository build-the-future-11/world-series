# CWLNN conditional routing development protocol

Development only; DRAFT_NOT_AUTHORIZED for confirmation. Preserve the historical
budget-4 failure and flat4 superiority. This candidate tests the original
small-graph hierarchy/routing claim, not language-model or portfolio-backbone
capability. Freeze numerical source before profile and campaign.

## Inputs and tasks

Seeds2707,2711,2713,2719,2729,2731,2741,2749; separate profile seed2699.
Two tasks: an explicitly hierarchy-aligned fine/coarse diffusion composition,
and a diffusion/reaction target whose labels never access parent maps.
Sparse heat propagation via SciPy expm_multiply generates labels, not a learned
candidate forward pass. Public inputs are two random signals, diffusion time,
normalized coordinate, node IDs, and sparse edges. Parent IDs=floor(nodeID/2).
Every control receives the same raw parent means. Training topologies path/cycle,
sizes24/48, time .3/.8. Held sizes96/192/384, topologies path/cycle/tree and times
.3/1.2, four fresh graphs per cell. The hierarchy-aligned task is an inductive
bias advantage and must be disclosed; the second task is retained regardless
of result. Tree generalization and held diffusion time cannot be omitted.

Each seed/task has32 training graphs and8 selection graphs with distinct
generator IDs;72 evaluation graphs. Whole graphs are the split unit. No target
labels build hierarchy, routing features, or preprocessing.

## Models and training

All models use width24 float64 CPU, learned input encoding, fine local update,
learned context transformation, cheap readout and an expensive 72->96->24->1
refinement MLP. Hierarchy context pools, propagates on the actual quotient
adjacency, then broadcasts. Flat5 uses three extra fine aggregations, matching
the maximum fine-graph reach of pairwise hierarchy on training paths including
public raw pooling. Local uses one extra aggregation (explicit lower-reach
control). Attention uses dense similarity of trained embeddings, capped at512
nodes per graph; its N² pairs are counted and never called sparse. No claim of
receptive-field matching on arbitrary trees, where quotient edges can connect
distant children of the supplied groups.

Eight models: hierarchy/full, flat5/full, local/full, attention/full,
hierarchy/learned-route, hierarchy/disagreement-route, hierarchy/fixed-hash-route,
flat5/learned-route. The first four process every refinement node. Routed models
evaluate fractions0,.25,.5,1, with floor(fraction*N) per graph. Hard selection
happens BEFORE expensive refinement. Router cost, full cheap path and sorting
remain. Fixed-hash routing is deterministic, not stochastic Monte Carlo routing.
Learned router is a4->8->1 MLP on feature norms, local disagreement and budget.
It adds49 parameters; all other parameter counts match exactly. Record this
small capacity difference rather than padding controls with unused parameters.

160 Adam updates at .003, batch4 graphs, same generated batches per model.
Routed training cycles fractions0,.25,.5,1 and adds N(0,.2²) priority exploration.
Selected residuals use a straight-through sigmoid gate, forward multiplier1;
gradient is only a surrogate on selected rows, not an exact top-k derivative.
Full controls use all rows for all updates; training compute is therefore
different and measured. Select checkpoint80 or160 by average selection MSE
over all four route fractions (full controls only fraction1). All training
losses, checkpoints, selection scores and state hashes saved. No evaluation
labels choose weights, route budgets or model configuration.

## Primary and cost policy

Primary: prediction MSE at an inference latency ceiling of3 milliseconds per
whole held graph, including input tensor copies, parent construction, graph
validation, quotient construction, pooling, routing, refinement and decoding.
Resident model loading and synthetic label generation are excluded. Warm each
configuration once; five repetitions in a seeded randomized configuration order.
Save every timing, report median per graph and complete error/time curve. A
configuration must meet the ceiling on at least95% of all72 held graphs within
each seed/task. Do not select the best budget with held errors: the primary
routed operating point is fraction.5; other fractions are descriptive tradeoffs.
Report per-seed means, eight-seed descriptive bootstrap, and paired errors;
no population or independent-confirmation claim. If a method misses the ceiling,
its result is infeasible at this declared operating point, not a speedup.

Record raw parameter/state storage, graph arrays, receipts (refinement rows,
attention pairs, quotient edges and refine multiply-adds), training wall time
and process peak RSS. RSS is global, not a per-method memory claim. Timings on
this uncontrolled single CPU host support local evidence only. Counter savings
do not imply wall-time savings. Run a separate large sparse allocation check;
do not extrapolate attention beyond its declared cap.

One numerical worker, threads1. At most128 trained models/20,480 updates and
23,040 held model-budget-graph predictions before five timing repeats. Unexpected
failures abort with preserved receipt. Audit split IDs, checkpoint selections,
all prediction/route receipts, consistent node permutations and source hashes.
