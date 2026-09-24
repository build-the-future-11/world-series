# WFT symmetry and resolution-constraint results

All 160 learned fits and 64 fixed/oracle controls completed. The 2,688 evaluation rows use frozen parameters; no held-size or held-topology refit occurred. Every prediction was checked with a separate NumPy/SciPy matrix-exponential implementation.

| Method | Mean normalized transfer prediction error | Total training seconds |
|---|---:|---:|
| both | 0.0003038781 | 4.128 |
| fixed_geometry | 0.001321223 | 0.000 |
| oracle_true_operator | 0 | 0.000 |
| resolution | 0.0004980942 | 3.941 |
| symmetry | 0.0005058279 | 4.020 |
| unconstrained | 0.0009285609 | 3.628 |
| wrong_symmetry | 0.001007201 | 4.073 |

Transfer averages groups 32/64 across cycle/path, fine/coarse, both sample counts and both noise levels, first within each of eight physical-instance seeds. Lower error is better. The true-operator oracle is privileged and not a qualified learned competitor.

| Control | Both constraints minus control | Descriptive seed bootstrap 95% interval |
|---|---:|---|
| fixed_geometry | -0.001017345 | [-0.0015593387576091052, -0.0005701196500093226] |
| oracle_true_operator | 0.0003038781 | [0.00018203545786108085, 0.0004448428501628866] |
| resolution | -0.0001942161 | [-0.0003060694235063219, -9.096634009877574e-05] |
| symmetry | -0.0002019498 | [-0.0002980067107460668, -0.00011221080246832891] |
| unconstrained | -0.0006246828 | [-0.0007898783160858037, -0.0004425888557627887] |
| wrong_symmetry | -0.0007033233 | [-0.0008413927860898862, -0.0005505824991725467] |

These are unadjusted development intervals over eight parameter draws. No equivalence, broad graph-population or independently confirmed claim follows. All noise/sample/topology/size/level cells remain in WFT_RESULTS.json, including unfavorable cases.

## Contracts and scope

Reflection and equitable coarsening hold for the declared generator, while the wrong cyclic-shift constraint violates its weights. Fine/coarse model fields are independently parameterized, so the consistency penalty has a real gradient. All learned methods have 11 parameters and the same observations/steps. Frozen transfer uses public coordinates and a shared low-frequency parametric field; it is not arbitrary unseen-weight-distribution generalization.

PSD, mass-weighted Parseval, eigensolver residual and full-basis reconstruction are numerical contracts, not learned transform efficacy. Compression includes fixed geometry, oracle, training-size uncentered PCA and random projection controls. Retained ranks can expand at repeated clusters and are reported per case; no fixed-rank compression advantage is asserted.

Setup, matrix exponential, 16-signal application and eigensolver times and operator bytes are retained per row. Training includes computation of diagnostic penalties even when disabled; constraint-forward time is a subset of training time, not an additional total. Hardware contention is uncontrolled and no equal-wall-time efficiency claim is made. Dense spectral diagnostics stop at 128 nodes.

The cross-implementation audit uses 1e-10 absolute agreement for predictions and ordinary compression cases. For compression boundaries with eigengap below 1e-6, the numerical audit tolerance is 1e-8; observed discrepancies above 1e-10 and their gaps are retained in the audit JSON. This post-run verification tolerance addresses projector conditioning and does not change frozen ranks, scores, training or the primary endpoint.
