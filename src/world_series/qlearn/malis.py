"""Bounded discrete action engine. This is a development MALIS subset."""
import copy
import random
import numpy as np
import torch

ACTIONS = ('sgd', 'momentum', 'adamw', 'replay', 'huber', 'checkpoint', 'rollback')

class DiscreteEngine:
    def __init__(self, task, rate=.03):
        self.task = task
        self.model = task.build()
        self.rate = rate
        self.optimizers = {
            'sgd': torch.optim.SGD(self.model.parameters(), lr=rate),
            'momentum': torch.optim.SGD(self.model.parameters(), lr=rate, momentum=.9),
            'adamw': torch.optim.AdamW(self.model.parameters(), lr=rate, weight_decay=.01),
        }
        self.active = 'sgd'
        self.loss_name = 'mse'
        self.replay_ids = list(range(len(task.support_x)))
        self.controller_state = {'completed_updates': 0}
        self.saved = None
        # Spent work must never roll back with the computational state.
        self.attempted_actions = 0
        self.gradient_evaluations = 0

    def snapshot(self):
        return copy.deepcopy({'model': self.model.state_dict(),
            'optimizers': {k: v.state_dict() for k, v in self.optimizers.items()},
            'active': self.active, 'loss_name': self.loss_name,
            'replay_ids': self.replay_ids, 'controller_state': self.controller_state,
            'torch_rng': torch.random.get_rng_state(), 'numpy_rng': np.random.get_state(),
            'python_rng': random.getstate()})

    def restore(self, snapshot):
        state = copy.deepcopy(snapshot)
        self.model.load_state_dict(state['model'])
        for k, optimizer in self.optimizers.items(): optimizer.load_state_dict(state['optimizers'][k])
        self.active, self.loss_name = state['active'], state['loss_name']
        self.replay_ids, self.controller_state = state['replay_ids'], state['controller_state']
        torch.random.set_rng_state(state['torch_rng'])
        np.random.set_state(state['numpy_rng'])
        random.setstate(state['python_rng'])

    def support_loss(self):
        with torch.no_grad():
            return float((self.model(self.task.support_x) - self.task.support_y).square().mean())

    def query_loss(self):
        with torch.no_grad():
            return float((self.model(self.task.query_x) - self.task.query_y).square().mean())

    def act(self, action, ledger=None):
        if action not in ACTIONS: raise ValueError(f'Unsupported MALIS action {action}')
        self.attempted_actions += 1
        if ledger: ledger.consume_step()
        if action == 'checkpoint':
            self.saved = self.snapshot()
            return
        if action == 'rollback':
            if self.saved is None: raise ValueError('No saved state for rollback')
            self.restore(self.saved)
            return
        self.active = action if action in self.optimizers else 'sgd'
        self.loss_name = 'huber' if action == 'huber' else 'mse'
        ids = self.replay_ids
        if action == 'replay':
            # Past support observations only, sampled without replacement.
            ids = random.sample(ids, max(1, len(ids)//2))
        x, y = self.task.support_x[ids], self.task.support_y[ids]
        optimizer = self.optimizers[self.active]
        optimizer.zero_grad(set_to_none=True)
        prediction = self.model(x)
        objective = torch.nn.functional.huber_loss(prediction, y) if self.loss_name == 'huber' else (prediction-y).square().mean()
        objective.backward()
        optimizer.step()
        self.gradient_evaluations += 1
        self.controller_state['completed_updates'] += 1


def run_experiment(cfg, run):
    from world_series.core.budgets import Budget, BudgetLedger
    from world_series.qlearn.regression import regression_task
    ledger = BudgetLedger(Budget(**cfg['budget']))
    seed = cfg['seed']; actions = ACTIONS[:5]; horizon = 32
    training = [regression_task(seed*100+i, f, width=8, support_size=24, query_size=24)
                for i, f in enumerate(['linear', 'sin'])]
    # Fit a phase-conditioned action ranking from support-progress traces.
    scores = np.zeros((4, len(actions)))
    traces = []
    for task in training:
        for j, action in enumerate(actions):
            engine = DiscreteEngine(task)
            for step in range(horizon):
                before = engine.support_loss(); engine.act(action, ledger); after = engine.support_loss()
                gain = (before-after)/max(before, 1e-8)
                scores[min(3, step//8), j] += gain if np.isfinite(gain) else -1e6
                traces.append({'task': task.task_id, 'action': action, 'step': step, 'before': before, 'after': after})
    chosen = [actions[int(j)] for j in scores.argmax(axis=1)]
    rows = []
    for case in range(4):
        task = regression_task(seed*100+20+case, 'tanh', width=8, support_size=24, query_size=24)
        for method in ['sgd', 'momentum', 'adamw', 'random', 'learned_phase', 'learned_with_rollback']:
            random.seed(seed+case)
            engine = DiscreteEngine(task)
            query = [engine.query_loss()]; events = []
            for step in range(horizon):
                action = (random.choice(actions) if method == 'random' else
                          chosen[min(3, step//8)] if method.startswith('learned') else method)
                before = engine.support_loss()
                snapshot = engine.snapshot()
                engine.act(action, ledger)
                after = engine.support_loss()
                rolled_back = False
                # Rollback consumes another action and cannot access query diagnostics.
                if method == 'learned_with_rollback' and after > before*1.5 and engine.attempted_actions < horizon:
                    engine.saved = snapshot
                    engine.act('rollback', ledger); rolled_back = True
                query.append(engine.query_loss())
                events.append({'action': action, 'support_before': before, 'support_after': after, 'rollback': rolled_back})
                if engine.attempted_actions >= horizon: break
            valid = bool(np.isfinite(query).all())
            rows.append({'method': method, 'case': case, 'task': task.task_id,
                         'query_losses': query, 'events': events,
                         'value': float(query[-1]/task.scale) if valid else None,
                         'attempted_actions': engine.attempted_actions,
                         'gradient_evaluations': engine.gradient_evaluations})
    result = {'status': 'SUCCEEDED', 'study': 'discrete-malis-v1', 'research_outcome': 'INCONCLUSIVE',
              'rows': rows, 'training_traces': traces, 'learned_phase_actions': chosen,
              'cost': ledger.snapshot(), 'scope': 'Discrete optimizer/replay/loss/rollback engine with support-only phase ranking; a bounded prototype, not the full MALIS architecture. Equal action caps do not equalize gradients.'}
    run.store.write_json('discrete-malis.json', result)
    return result
