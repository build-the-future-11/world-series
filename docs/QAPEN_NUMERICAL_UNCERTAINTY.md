# QAPEN numerical uncertainty correction

The mixture and causal-lifecycle paths previously evaluated variance as a
second moment minus the squared mean. At common offsets such as `1e8`, this
can cancel a component variance of one to zero. The lifecycle then substitutes
its variance floor, changing the reported uncertainty and likelihood.

The development implementation now uses the centered law of total variance:
the weighted within-component variance plus the weighted squared distance of
component means from the mixture mean. The active-expert and retrieved-memory
routes share this implementation. Weight normalization rescales finite weights
before summing; between-component deviations are weighted before squaring to
avoid unnecessary intermediate overflow. Invalid distributions and final
moments outside the finite range fail explicitly.

Gaussian negative log likelihood now separates the logarithm of the variance
from the constant and standardizes the residual before squaring. This keeps
representable values finite when the former intermediate products overflowed.

Constructed arithmetic tests include translation invariance, independent
100-digit decimal likelihood values, and the actual causal prediction path.
No retained campaign, result table, protocol, model checkpoint or historical
negative conclusion is rewritten. Future development runs have a changed
implementation identity; this correction is not evidence of a winning mechanism
or authorization to rerun protected confirmation.
