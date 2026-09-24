# CWLNN bounded routing result

The conditional mechanism is IMPLEMENTED and BENCHMARKED. The proposed learned
routing advantage is NOT_SUPPORTED at the declared 50% operating point on this
CPU study. This closes a bounded experiment, not the whole research program.

| Task | Full hierarchy MSE / median ms | Learned 50% MSE / median ms |
|---|---:|---:|
| Hierarchy-aligned multiscale | 0.011412 / 0.7133 | 0.011939 / 0.7673 |
| Nonhierarchical diffusion | 0.029831 / 0.7125 | 0.032721 / 0.7595 |

All primary configurations satisfy the3ms ceiling in all eight seeds. Learned
routing halves expensive refinement rows but pays for scoring/sorting and the
unchanged cheap path. It has higher mean MSE and higher aggregate median time
than full hierarchy in both tasks. Paired mean error increases are0.000527
(descriptive seed interval0.000265..0.000766) and0.002890
(0.002452..0.003271). These are local finite-generator findings, not a general
impossibility result. Stronger optimization or larger refinements could change
the tradeoff; they require a newly frozen study, not relabeling this result.

Full hierarchy improves on flat5 in the aligned task (0.011412 vs0.012776), while
flat5 is better on diffusion (0.027387 vs0.029831). The aligned target explicitly
uses the public hierarchy; it is not neutral evidence for a universal backbone.
Learned routing does not clearly beat the simple disagreement router on either
task. Do not advertise a positive learned-routing contribution from these data.

All four routing budgets and all held sizes/topologies remain in raw results.
Every prediction, routing receipt and checkpoint selection was replayed. All
23,040 permutation checks agree within4.45e-16. One160-step learned-router fit
reproduces all losses, batches, weights and checkpoint selection exactly on the
same host. The allocation probe's largest operator output is[N,48] through
100,000 nodes at1% refinement, with no attention pairs. This is neither a bound
on total live allocations nor a per-model peak-memory measurement. First-call
instrumentation overhead makes the probe times unsuitable for speed comparisons.

Controls have11,978 parameters; learned routers have12,027. All receive raw
public parent means. Training compute differs, and timings include diagnostic
receipt construction. Receptive-field matching is justified on training paths,
not arbitrary held tree groupings. CW02 therefore remains open as a broad
matching requirement. Generalization to arbitrary hierarchies and external
confirmation/novelty/publication decisions remain separate open requirements.

Historical budget4 accuracy loss and flat4 superiority in the original
constructed propagation task remain unchanged in GATE_RESULTS.md. The new
trained candidate does not replace or retroactively validate those results.
