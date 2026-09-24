"""Compatibility qualification for pinned official PySINDy, not paper reproduction."""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import sys

import numpy as np
import pysindy as ps
from scipy.linalg import expm


def qualify():
    t = np.linspace(0, 5, 501)
    matrix = np.array([[0., 1.], [-2., -.3]])
    observed = np.array([expm(matrix * ti) @ [.7, -1.1] for ti in t])
    outputs = {}
    for method in ('derivative', 'weak'):
        np.random.seed(17)
        base = ps.PolynomialLibrary(degree=3, include_bias=True)
        lib = base if method == 'derivative' else ps.WeakPDELibrary(
            function_library=base, spatiotemporal_grid=t, K=32,
            H_xt=[1.25], is_uniform=True)
        model = ps.SINDy(feature_library=lib, optimizer=ps.STLSQ(
            threshold=.05, alpha=0., normalize_columns=False, max_iter=20))
        model.fit(observed, t=t)
        names = model.get_feature_names()
        coef = model.coefficients()[1]
        truth = np.array([-2. if n == 'x0' else -.3 if n == 'x1' else 0. for n in names])
        error = float(np.max(np.abs(coef - truth)))
        assert error < .002, (method, error)
        outputs[method] = {'names': names, 'acceleration_coefficients': coef.tolist(),
                           'max_coefficient_error': error}
    dist = metadata.distribution('pysindy')
    files = {}
    for item in dist.files:
        if str(item).endswith('.py') or 'LICENSE' in str(item):
            path = dist.locate_file(item)
            files[str(item)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {'pysindy_version': metadata.version('pysindy'),
            'dependencies': {p: metadata.version(p) for p in ('numpy', 'scipy', 'scikit-learn', 'derivative')},
            'license': dist.metadata.get('License'), 'source_files': files,
            'qualification': outputs,
            'scope': 'Official package compatibility on a clean analytic oscillator; not a reproduction of published WSINDy results.',
            'documentation': 'https://pysindy.readthedocs.io/en/stable/examples/12_weakform_SINDy_examples/example.html'}


if __name__ == '__main__':
    path = Path(sys.argv[1])
    with path.open('x') as f:
        json.dump(qualify(), f, indent=2)
