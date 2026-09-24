"""Versioned, bounded development benchmarks; never a confirmation evaluator."""
from __future__ import annotations

from collections import defaultdict
import itertools
import math
import time
import numpy as np
from scipy.integrate import solve_ivp

from world_series.core.budgets import Budget, BudgetLedger


def aggregate(rows, key='value'):
    """All attempted rows remain in the denominator; failures invalidate means."""
    groups = defaultdict(list)
    for row in rows:
        groups[(row['method'], row.get('condition', 'all'))].append(row)
    return [{'method': method, 'condition': condition, 'attempted': len(rs),
             'failures': sum(r.get(key) is None or not math.isfinite(r[key]) for r in rs),
             'mean': float(np.mean([r[key] for r in rs]))
             if all(r.get(key) is not None and math.isfinite(r[key]) for r in rs) else None}
            for (method, condition), rs in sorted(groups.items())]


def run_experiment(cfg, run):
    ledger = BudgetLedger(Budget(**cfg['budget']))
    fn = globals()[cfg['project'] + '_study']
    result = fn(int(cfg['seed']), cfg.get('params', {}), ledger)
    result.update(status='SUCCEEDED', study='development-v2', project=cfg['project'],
                  seed=cfg['seed'], research_outcome='INCONCLUSIVE',
                  protocol_state='DRAFT_NOT_AUTHORIZED', cost=ledger.snapshot())
    ref = run.store.write_json('development-v2.json', result)
    return {**result, 'raw_artifact': {'path': ref.relative_path, 'sha256': ref.sha256}}


class ContextMemory:
    """Causal past-context retrieval, explicitly a new baseline-scale mechanism.

    Store observed outcomes only after predicting. Retrieve using previous five
    observations; no regime IDs, current outcomes, or future data enter queries.
    """
    def __init__(self, seed, memory=True, random_read=False, max_experts=8):
        from world_series.qapen.lifecycle import QAPENModel
        self.base = QAPENModel(max_experts=max_experts)
        self.memory, self.random_read = memory, random_read
        self.rng = np.random.default_rng(seed)
        self.history, self.keys, self.values = [], [], []
        self.pending = None
        self.reads = 0

    def predict(self):
        mean, var = self.base.predict()
        a = np.asarray(self.history[-5:] or [0.])
        self.pending = np.array([a.mean(), a.std(), a[-1]])
        if self.memory and len(self.values) >= 5:
            distance = np.sum((np.array(self.keys) - self.pending) ** 2, axis=1)
            ids = self.rng.choice(len(self.values), 5, replace=False) if self.random_read else np.argsort(distance)[:5]
            values = np.array(self.values)[ids]
            mm, vv = float(values.mean()), max(.05, float(values.var()))
            # Equal fixed mixture; account for between-component uncertainty.
            mean, var = .5 * (mean + mm), .5 * (var + vv) + .25 * (mean - mm) ** 2
            self.reads += 1
        return mean, var

    def update(self, y):
        self.base.update(y)
        if self.memory:
            self.keys.append(self.pending.copy()); self.values.append(float(y))
            self.keys, self.values = self.keys[-128:], self.values[-128:]
        self.history = (self.history + [float(y)])[-5:]


def qapen_study(seed, params, ledger):
    from world_series.qapen.baselines import FixedEnsemble, AdaptiveNoMemory, RecentMemoryControl, nll
    rng = np.random.default_rng(seed)
    models = {'context_memory': ContextMemory(seed), 'no_memory': ContextMemory(seed, memory=False),
              'random_memory': ContextMemory(seed, random_read=True),
              'single_expert_memory': ContextMemory(seed, max_experts=1),
              'recent': RecentMemoryControl(5), 'cumulative': AdaptiveNoMemory(), 'fixed': FixedEnsemble()}
    # Entire schedules are seed-level units. Regime 1 occupies 20%, returns four times.
    schedule = np.tile(np.repeat([0, 1], [80, 20]), 4)
    outcomes = rng.normal(2 * schedule, .5)
    rows, raw, times = [], [], {m: 0. for m in models}
    for t, (regime, y) in enumerate(zip(schedule, outcomes)):
        ledger.check_alive()
        for name, model in models.items():
            ledger.consume_sim()
            start = time.perf_counter(); mean, var = model.predict()
            score = nll(float(y), mean, var)
            if hasattr(model, 'update'): model.update(float(y))
            times[name] += time.perf_counter() - start
            raw.append({'t': t, 'regime': int(regime), 'observed': float(y), 'method': name,
                        'predicted_mean': mean, 'predicted_variance': var, 'nll': score})
    for name in models:
        for condition in ['all', 'rare', 'ordinary', 'return_first5']:
            rs = [r for r in raw if r['method'] == name and
                  (condition == 'all' or condition == 'rare' and r['regime'] == 1 or
                   condition == 'ordinary' and r['regime'] == 0 or
                   condition == 'return_first5' and r['regime'] == 1 and r['t'] % 100 < 85)]
            rows.append({'method': name, 'condition': condition, 'n': len(rs),
                         'value': float(np.mean([r['nll'] for r in rs]))})
    return {'primary_metric': 'causal_mean_nll_by_regime', 'rows': rows, 'trajectories': raw,
            'summary': aggregate(rows), 'method_wall_seconds': times,
            'memory_reads': {m: x.reads for m, x in models.items() if isinstance(x, ContextMemory)},
            'scope': 'New causal context-memory intervention; not full lifecycle Q-APEN. Equal stream prediction calls, unequal compute.'}


def qwipii_study(seed, params, ledger):
    from world_series.qwipii.domains import RingState
    from world_series.qwipii.search import bfs, quotient_bfs, ranking_only_bfs, replay
    rng = np.random.default_rng(seed)
    rows = []
    for n in [4, 5, 6]:
        for case in range(6):
            start = RingState(tuple(int(x) for x in rng.permutation(n)), tuple(range(n)))
            for cap in [12, 120]:
                for method in ['brute', 'quotient', 'ranking_only']:
                    timer = time.perf_counter()
                    if method == 'ranking_only':
                        path, expansions, status = ranking_only_bfs(start, ledger, lambda s: -sum(a != b for a, b in zip(s.tokens, s.goal)), cap)
                    else:
                        path, expansions, status = {'brute': bfs, 'quotient': quotient_bfs}[method](start, ledger, cap)
                    ok = path is not None and replay(start, path).tokens == start.goal
                    if status == 'solved' and not ok: raise AssertionError('Unliftable path')
                    rows.append({'method': method, 'condition': f'n{n}/budget{cap}', 'case': case,
                                 'start': list(start.tokens), 'goal': list(start.goal), 'path': path,
                                 'value': float(ok), 'expansions': expansions, 'status': status,
                                 'wall_seconds': time.perf_counter() - timer})
    return {'primary_metric': 'verified_solve_rate_at_equal_expansion_cap', 'rows': rows, 'summary': aggregate(rows),
            'scope': 'Distinct fixed goal labels leave no nontrivial goal stabilizer; quotient savings are not guaranteed.'}


def synthesis_cases(seed):
    from world_series.wcode.search import enumerate_small_programs
    from world_series.wcode.interpreter import interpret, Fuel
    from world_series.wcode.dataset import SynthesisTask
    from world_series.wcode.graph import ast_hash
    rng = np.random.default_rng(seed)
    seen, tasks = set(), []
    for program in enumerate_small_programs():
        signature = tuple(interpret(program, {'x': x}, Fuel(128)) for x in range(-8, 9))
        if signature in seen: continue
        seen.add(signature)
        xs = [int(x) for x in rng.choice(np.arange(-4, 5), 3, replace=False)]
        examples = [({'x': x}, interpret(program, {'x': x}, Fuel(128))) for x in xs]
        held = [({'x': x}, y) for x, y in zip(range(-8, 9), signature) if x not in xs]
        tasks.append(SynthesisTask(ast_hash(program), ast_hash(program), program, examples, held))
    return tasks


def synthesis_attempt(task, mode, cap):
    from world_series.wcode.search import synthesize
    from world_series.wcode.verifier import verify_program
    local = BudgetLedger(Budget(max_candidate_evals=cap))
    start = time.perf_counter()
    program, found, used = synthesize(task.public_examples, local, cap, mode)
    verified = bool(found and verify_program(program, task.heldout)['ok'])
    return {'value': float(verified), 'candidates': used, 'public_fit': found,
            'wall_seconds': time.perf_counter() - start}


def wcode_study(seed, params, ledger):
    rows = []
    for task in synthesis_cases(seed):
        for cap in [8, 24, 53]:
            for mode in ['uniform', 'length', 'token', 'flat', 'hierarchical']:
                ledger.check_alive()
                receipt = synthesis_attempt(task, mode, cap)
                ledger.consume_candidates(receipt['candidates'])
                rows.append({'method': mode, 'condition': f'budget{cap}', 'task': task.task_id,
                             'public': task.public_examples, **receipt})
    return {'primary_metric': 'heldout_solve_at_candidate_budget', 'rows': rows, 'summary': aggregate(rows),
            'scope': 'Untrained structural rankers over a shared finite DSL; all semantic executions are charged. No learned-encoder claim.'}


def full_rollout_error(held, coef):
    """Evaluate every fitted term without clipping damping or dropping nonlinear terms."""
    evaluations = 0
    def rhs(t, state):
        nonlocal evaluations
        evaluations += 1
        if evaluations > 4000 or not np.isfinite(state).all() or np.max(np.abs(state)) > 1e6:
            raise FloatingPointError('Integration work/state cap exceeded')
        q, v = state
        return [v, sum(coef.get(k, 0.) * x for k, x in {'q': q, 'v': v, 'q2': q*q, 'v2': v*v, 'qv': q*v}.items())]
    try:
        with np.errstate(over='ignore', invalid='ignore'):
            sol = solve_ivp(rhs, (held.times[0], held.times[-1]), held.observations[0], t_eval=held.times,
                            rtol=1e-7, atol=1e-9)
    except FloatingPointError:
        return None
    if not sol.success or sol.y.shape != held.observations.T.shape or not np.isfinite(sol.y).all(): return None
    return float(np.mean((sol.y.T - held.observations) ** 2))


def wpinn_study(seed, params, ledger):
    from world_series.wpinn.systems import make_trajectory
    from world_series.wpinn.train import weak_only_fit
    from world_series.wpinn.baselines import data_only_accel_fit, known_support_fit
    rows = []
    for k, c in [(1., 0.), (2., .3), (4., .8)]:
        for noise in [0., .02, .1]:
            ledger.consume_step()
            train = make_trajectory(seed * 100 + 1, k, c, noise)
            # Same physical law, independent initial condition, clean target trajectory.
            held = make_trajectory(seed * 100 + 2, k, c, 0.)
            weak, _, _ = weak_only_fit(train)
            fits = {'weak': weak, 'data_only': data_only_accel_fit(train),
                    'known_support': known_support_fit(train), 'wrong_conservation': {**weak, 'v': 0.}}
            for method, coef in fits.items():
                rows.append({'method': method, 'condition': f'k{k}/c{c}/noise{noise}',
                             'value': full_rollout_error(held, coef), 'coefficients': coef,
                             'coefficient_error': float(sum((coef.get(x, 0.) - y)**2 for x, y in {'q': -k, 'v': -c, 'q2': 0., 'v2': 0., 'qv': 0.}.items())),
                             'train_id': train.trajectory_id, 'held_id': held.trajectory_id})
    return {'primary_metric': 'full_polynomial_held_initial_condition_rollout_mse', 'rows': rows, 'summary': aggregate(rows),
            'scope': 'Three oscillator parameter settings; each fit has its own independent held initial condition. Known-support baseline is oracle-assisted.'}


def wft_study(seed, params, ledger):
    from world_series.wft.laplacian import laplacian_from_weights
    from world_series.wft.operators import learn_operator_ridge, constrained_sym_nonneg
    rng = np.random.default_rng(seed); rows = []
    for n in [12, 24]:
        for noise in [0., .1, .5]:
            for samples in [8, 32]:
                ledger.consume_step()
                W = np.zeros((n, n)); weights = rng.uniform(.3, 1.5, n - 1)
                W[np.arange(n-1), np.arange(1,n)] = weights; W += W.T
                L = laplacian_from_weights(W)
                X = rng.normal(size=(n, samples)); Y = L @ X + rng.normal(scale=noise, size=X.shape)
                test = rng.normal(size=(n, 32)); target = L @ test
                un = learn_operator_ridge(X, Y)
                constrained = laplacian_from_weights(constrained_sym_nonneg(-un))
                topology = (W > 0).astype(float)
                methods = {'ridge': un, 'constrained_laplacian': constrained,
                           'fixed_unit_weights': laplacian_from_weights(topology), 'oracle_true_graph': L}
                for method, A in methods.items():
                    rows.append({'method': method, 'condition': f'n{n}/noise{noise}/samples{samples}',
                                 'value': float(np.mean((A @ test-target)**2)),
                                 'min_eigenvalue_symmetric_part': float(np.linalg.eigvalsh((A + A.T)/2).min())})
    return {'primary_metric': 'held_vector_mse', 'rows': rows, 'summary': aggregate(rows),
            'scope': 'Independent weighted path graphs; refit at each graph size, not zero-shot size transfer. Oracle is labeled separately.'}


def cwlnn_study(seed, params, ledger):
    from world_series.cwlnn.graphs import GraphLevel, path_edges
    from world_series.cwlnn.model import forward_multiscale
    from world_series.cwlnn.baselines import flat_mp, tiny_attention
    rng = np.random.default_rng(seed); rows = []
    modes = ['flat', 'hierarchy', 'routed', 'budget_attention']
    def graph(n):
        x = rng.normal(size=(n, 4)); edges = path_edges(n)
        # Target independent of the candidate hierarchy: 4-hop diffusion + graph mean.
        y = flat_mp(x, edges, layers=4)[:, :1] + .5 * x[:, :1].mean()
        features = {}; costs = {}
        for mode in modes:
            start = time.perf_counter()
            if mode == 'flat': h = flat_mp(x, edges)
            elif mode == 'budget_attention': h, _ = tiny_attention(x, 32)
            else: h, _ = forward_multiscale(GraphLevel(x, edges), route_budget=4 if mode == 'routed' else None)
            features[mode] = np.column_stack([x, h, np.ones(n)])
            costs[mode] = time.perf_counter() - start
        return features, y, costs
    training = [graph(24) for _ in range(12)]
    weights = {}
    for mode in modes:
        X = np.concatenate([g[0][mode] for g in training]); Y = np.concatenate([g[1] for g in training])
        weights[mode] = np.linalg.solve(X.T @ X + .01*np.eye(X.shape[1]), X.T @ Y)
    for n in [24, 48, 96]:
        ledger.refuse_allocation(nodes=n)
        for case in range(8):
            ledger.consume_step(); feats, target, cost = graph(n)
            for mode in modes:
                rows.append({'method': mode, 'condition': f'n{n}', 'graph': case,
                             'value': float(np.mean((feats[mode] @ weights[mode]-target)**2)),
                             'feature_seconds': cost[mode], 'readout_parameters': int(weights[mode].size)})
    return {'primary_metric': 'held_graph_node_regression_mse', 'rows': rows, 'summary': aggregate(rows),
            'scope': 'Fixed sparse features plus equally sized trained ridge readouts; independent graphs, frozen readouts transfer to larger sizes. No universal-backbone claim.'}


def wfim_study(seed, params, ledger):
    from world_series.wfim.algebra import SparseWordSeries, multiply, project_degree, truncated_multiply, topk_prune, assert_associativity_truncated
    from world_series.wfim.transport import transported_multiply
    rng = np.random.default_rng(seed); rows = []
    for degree in [2, 3, 4]:
        for case in range(12):
            ledger.consume_step()
            def draw():
                return SparseWordSeries({tuple(int(z) for z in rng.integers(1, 4, int(rng.integers(0, 4)))): float(rng.normal()) for _ in range(8)})
            a,b,c=draw(),draw(),draw(); exact = project_degree(multiply(a,b), degree)
            for method in ['truncated', 'topk', 'transported']:
                start=time.perf_counter()
                if method == 'truncated': out=truncated_multiply(a,b,degree)
                elif method == 'topk': out=topk_prune(multiply(a,b),len(exact.coeffs))
                else: out=project_degree(transported_multiply(a,b,{1:1.2,2:.8,3:1.1}),degree)
                elapsed=time.perf_counter()-start
                keys=set(out.coeffs)|set(exact.coeffs)
                error=sum((out.coeffs.get(k,0)-exact.coeffs.get(k,0))**2 for k in keys)
                rows.append({'method':method,'condition':f'degree{degree}','case':case,'value':error,
                             'wall_seconds':elapsed,'terms':len(out.coeffs),
                             'coefficient_storage_bytes':sum(8+4*len(w) for w in out.coeffs),
                             'transport_parameter_bytes':24 if method=='transported' else 0,
                             'truncated_associative':assert_associativity_truncated(a,b,c,degree)})
    return {'primary_metric':'coefficient_error_against_degree_projection','rows':rows,'summary':aggregate(rows),
            'scope':'Finite random supports; top-k matches term count, not byte count. Algebraic equivalence is not novel representation benefit.'}


def ultron_study(seed, params, ledger):
    """Real, limited tool-selection task: same solvers and caps for every router."""
    modes=['uniform','length','token','flat','hierarchical']
    tasks=synthesis_cases(seed)
    # Split entire semantic program families; public/held rows within a task never cross roles.
    train=[t for i,t in enumerate(tasks) if i%2==0]
    held=[t for i,t in enumerate(tasks) if i%2==1]
    rng=np.random.default_rng(seed)
    def feature(t):
        x=np.array([e['x'] for e,y in t.public_examples],float); y=np.array([y for e,y in t.public_examples],float)
        return np.array([y.mean(),y.std(),np.mean(x*y),float(np.mean(y==x))])
    rows=[]; traces=[]
    for cap in [8,24,53]:
        training=[]; train_cost=0
        for t in train:
            choices=[]
            for mode in modes:
                r=synthesis_attempt(t,mode,cap); ledger.consume_candidates(r['candidates']); train_cost+=r['candidates']
                choices.append(r); traces.append({'task':t.task_id,'cap':cap,'tool':mode,**r})
            best=min(range(len(modes)),key=lambda i:(-choices[i]['value'],choices[i]['candidates'],i))
            training.append((feature(t),best))
        X=np.stack([x for x,y in training]); scale=np.maximum(X.std(axis=0),1.)
        # Cheapest measured by average charged development candidates, never tool-name length.
        mean_cost=[np.mean([r['candidates'] for r in traces if r['cap']==cap and r['tool']==m]) for m in modes]
        for t in held:
            selected={'static':'uniform','cheapest':modes[int(np.argmin(mean_cost))],
                      'random':modes[int(rng.integers(len(modes)))],
                      'learned':modes[training[int(np.argmin(np.sum(((X-feature(t))/scale)**2,axis=1)))][1]]}
            for policy,mode in selected.items():
                ledger.check_alive(); receipt=synthesis_attempt(t,mode,cap); ledger.consume_candidates(receipt['candidates'])
                rows.append({'method':policy,'condition':f'budget{cap}','task':t.task_id,'selected_tool':mode,**receipt})
    return {'primary_metric':'held_task_verified_completion','rows':rows,'summary':aggregate(rows),
            'training_traces':traces,'training_task_ids':[t.task_id for t in train],
            'evaluation_task_ids':[t.task_id for t in held], 'identical_tool_sets':modes,
            'scope':'Local finite-DSL tool routing with a nearest-neighbor learned router. All policies can fail; not an external sealed verifier or general research agent.'}
