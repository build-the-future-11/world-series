# Q-APEN causal lifecycle development protocol v1

This is a separately versioned implementation and development experiment. It
does not modify historical PEN, QAPENModel, or development-v2 outcomes. Source,
script and protocol hashes are frozen in each receipt before execution.

Primary development question: does the implemented lifecycle plus delayed-utility
memory improve mean prequential Gaussian NLL over the strongest declared simple
control within a common 2,000,000 scalar-operation proxy cap per stream? Scores
use a moment-matched Gaussian, not the exact multimodal mixture density. Lower is
better. Required streams contain 320 predictions. Exhausting the cap makes the
required endpoint incomplete; no prefix-only or survivor-only mean replaces it.
Full elapsed time, proxy operations, parameter/storage counts and mechanism
events accompany NLL. This cap does not imply equal actual computation or time.
No practically meaningful confirmation margin or powered generalization claim
is inferred from these development results.

Independent generated stream seeds: 1009, 1103, 1201, 1301, 1409, 1511, 1601,
1709. Conditions: no-shift, rare-return, long-gap and delayed-cue schedules,
crossed with observation noise 0.1 and 0.6. Each seed supplies independently
sampled stable AR coefficients and offsets; shared draws pair methods. Regime
truth is available only to evaluation. The input contains the previous observed
value and a public noisy cue; in delayed-cue conditions it is revealed four
steps before a switch. No future target or regime label is passed to learners.

A codebook with eight centers is fitted once on separate training streams
seeds 31, 37, 41 and 43. Raw context and continuous quantization residual remain
available alongside the one-hot code. The codebook is frozen during evaluation.
Each expert is a linear probabilistic PyTorch module with Adam state and a
positive variance floor. This is a finite linear-Gaussian lifecycle candidate,
not a full latent neural world model or planning system.

Lifecycle: sustained three-event surprise triggers birth after cooldown 24;
bounded replay warmup precedes eight subsequent prediction scores. Admission
requires positive prospective NLL gain against the existing ensemble. Stable
identities that fail warmup remain PRUNED and cannot bypass admission by revival.
Stable
UUID identities retain module and optimizer state through sleep/revival. Caps:
four active experts, sixteen total identities, sixty-four engrams, replay 32.
An engram stores context/code, observed value, variance, expert identity, write
time, access counts and utility measured only on later retrieved predictions.
Consolidation evicts the lowest delayed mean utility, breaking ties by age.

Eight controls/candidates: lifecycle+memory, lifecycle without memory, fixed
four-expert+memory, fixed four-expert without memory, single-expert+memory,
lifecycle with random retrieval, lifecycle with most-recent retrieval, and
rolling ridge regression. Routing information, targets and prediction schedule
are shared. Fixed ensemble and single expert have deliberately different
capacity; full costs are reported and no parameter-matched claim is made.

Report all/rare/ordinary/first-eight-after-switch NLL, nominal 95% coverage,
expert counts, spawn/sleep/revival, memory utility/accesses, costs and failures.
Use paired seed means over all declared conditions; retain per-condition rows.
Bootstrap seeds 10,000 times with seed 240925 for descriptive paired intervals,
without treating timesteps as independent units. These intervals describe this
generator collection; there is no external holdout, novelty verdict or required
practical-equivalence conclusion. No hyperparameter selection is performed.
