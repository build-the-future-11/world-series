"""Finite, source-bound development matrix for neural bounded-update policies."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import io
import json
import math
import time

import numpy as np
import torch

from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import RunStatus
from world_series.qlearn.regression import (
    MetaTrainer, RecurrentUpdatePolicy, adapt, fixed_adapt,
    regression_task, trajectory_record,
)


VARIANTS = {
    'full': {}, 'no_budget': {'use_budget': False},
    'no_recurrence': {'use_recurrence': False}, 'no_gates': {'learn_gates': False},
}


def dataset_hash(task):
    digest = hashlib.sha256()
    for name in ['support_x', 'support_y', 'query_x', 'query_y']:
        value = getattr(task, name).numpy()
        digest.update(name.encode())
        digest.update(str(value.shape).encode())
        digest.update(value.tobytes())
    return digest.hexdigest()


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row['method'], row['width'], row['requested_steps'])].append(row)
    result = []
    for (method, width, horizon), members in sorted(groups.items()):
        valid = all(not r['diverged'] and r['complete'] for r in members)
        result.append({
            'method': method, 'width': width, 'horizon': horizon,
            'attempted_tasks': len(members),
            'diverged_tasks': sum(r['diverged'] for r in members),
            'incomplete_tasks': sum(not r['complete'] for r in members),
            'training_seeds': sorted({r['training_seed'] for r in members}),
            # No silent finite-only mean: a failed member leaves the endpoint absent.
            'mean_gradient_step_auc': float(np.mean([r['gradient_step_auc'] for r in members])) if valid else None,
            'mean_measured_wall_time_auc': float(np.mean([r['measured_wall_time_auc'] for r in members])) if valid else None,
            'mean_normalized_final_loss': float(np.mean([r['normalized_final_loss'] for r in members])) if valid else None,
        })
    return result


def run_experiment(cfg, run):
    if cfg['device'] != 'cpu':
        raise ValueError('Neural optimizee development reference is CPU float64; no silent device fallback')
    params = cfg['params']
    seeds = params['training_seeds']
    etas = params['baseline_learning_rates']
    outer_rates = params['outer_learning_rates']
    horizons = params['evaluation_horizons']
    variants = params['variants']
    train_steps = int(params['adaptation_steps'])
    outer_steps = int(params['meta_steps'])
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError('Training seeds must be explicit, nonempty and unique')
    if not etas or len(etas) != len(outer_rates):
        raise ValueError('All compared methods require equal declared tuning trial counts')
    if any(v not in VARIANTS for v in variants) or len(set(variants)) != len(variants):
        raise ValueError('Unknown or duplicate ablation')
    if min(train_steps, outer_steps, *horizons) <= 0:
        raise ValueError('Training and evaluation horizons must be positive')
    if (params['train_tasks'] < 2 or params['selection_tasks'] < 1
            or params['evaluation_tasks'] < 1 or not params['evaluation_widths']):
        raise ValueError('Require nonempty independent partitions and both meta-training families')
    if any(not math.isfinite(v) or v <= 0 for v in [*etas, *outer_rates]):
        raise ValueError('Learning rates must be finite and positive')
    ledger = BudgetLedger(Budget(**cfg['budget']))
    refs = []

    def store_bytes(name, content, media_type):
        ledger.consume_bytes(len(content))
        ref = run.store.write_bytes(name, content, media_type)
        refs.append({'path': ref.relative_path, 'sha256': ref.sha256})
        return ref

    def store_json(name, content):
        return store_bytes(name, (json.dumps(content, indent=2, sort_keys=True,
                                            allow_nan=False) + '\n').encode(), 'application/json')

    store_json('neural-study/input_manifest.json', {
        'schema': 'qlearn-neural-development-v1', 'config': cfg,
        'protocol_state': 'DRAFT_NOT_AUTHORIZED_FOR_CONFIRMATION',
        'source': run.manifest.source,
        'training_families': ['linear', 'sin'], 'selection_families': ['quadratic'],
        'evaluation_families': ['tanh'],
        'scope': 'Constructed function-family and optimizee-width transfer; not natural data or discrete MALIS',
    })
    all_rows, trials, seed_failures = [], [], []
    start = time.perf_counter()
    for seed in seeds:
        def make(i, family, width, partition):
            return regression_task(seed * 1000 + i, family, width=width,
                                   dim=params['input_dim'], support_size=params['support_size'],
                                   query_size=params['query_size'], namespace=partition)

        train = [make(i, ['linear', 'sin'][i % 2], params['train_width'], 'meta_train')
                 for i in range(params['train_tasks'])]
        selection = [make(100 + i, 'quadratic', params['train_width'], 'selection')
                     for i in range(params['selection_tasks'])]
        held = [make(200 + i, 'tanh', width, 'evaluation')
                for width in params['evaluation_widths'] for i in range(params['evaluation_tasks'])]
        tasks = train + selection + held
        if len({t.task_id for t in tasks}) != len(tasks):
            raise ValueError('Duplicate task identity across study partitions')
        store_json(f'neural-study/seed-{seed}/datasets.json', [
            {'task_id': t.task_id, 'family': t.family, 'width': t.width,
             'dataset_sha256': dataset_hash(t), 'initialization_seed': t.initialization_seed,
             'normalization_scale': t.scale} for t in tasks])
        data = io.BytesIO()
        np.savez_compressed(data, **{f'task_{i}_{field}': getattr(t, field).numpy()
                                    for i, t in enumerate(tasks)
                                    for field in ['support_x', 'support_y', 'query_x', 'query_y']})
        store_bytes(f'neural-study/seed-{seed}/datasets.npz', data.getvalue(), 'application/octet-stream')
        selected = {}
        for method in ['sgd', 'momentum', 'adamw']:
            scores = []
            for trial, eta in enumerate(etas):
                ledger.consume_candidates()
                rows = [trajectory_record(t, method, fixed_adapt(t, method, train_steps, eta, ledger=ledger),
                                          train_steps) for t in selection]
                valid = all(not r['diverged'] for r in rows)
                score = sum(r['gradient_step_auc'] for r in rows) / len(rows) if valid else None
                trials.append({'seed': seed, 'method': method, 'trial': trial, 'learning_rate': eta,
                               'selection_score': score, 'status': 'VALID' if valid else 'DIVERGED'})
                store_json(f'neural-study/seed-{seed}/{method}-trial-{trial:02}.json', rows)
                scores.append(score if score is not None else math.inf)
            best = min(range(len(scores)), key=scores.__getitem__)
            if math.isfinite(scores[best]):
                selected[method] = {'learning_rate': etas[best], 'trial': best, 'score': scores[best]}
            else:
                seed_failures.append({'seed': seed, 'method': method, 'reason': 'all_tuning_trials_diverged'})

        selected_policies = {}
        for variant in variants:
            best_score = math.inf
            for trial, outer_lr in enumerate(outer_rates):
                ledger.check_alive()
                ledger.consume_candidates()
                torch.manual_seed(seed)
                policy = RecurrentUpdatePolicy(hidden=params['controller_hidden'], layers=params['controller_layers'],
                                               **VARIANTS[variant])
                trainer = MetaTrainer(policy, lr=outer_lr)
                history, training_rows = [], []
                failed = None
                def retain(task, trajectory):
                    row = trajectory_record(task, variant, trajectory, train_steps)
                    row['meta_step'] = trainer.completed_steps
                    training_rows.append(row)
                try:
                    for _ in range(outer_steps):
                        history.append(trainer.step(train, train_steps, ledger=ledger, on_task=retain))
                except FloatingPointError as exc:
                    failed = str(exc)
                selection_rows = [] if failed else [
                    trajectory_record(t, variant, adapt(t, policy, train_steps, gradient_mode='evaluation', ledger=ledger), train_steps)
                    for t in selection]
                valid = not failed and all(not r['diverged'] for r in selection_rows)
                score = sum(r['gradient_step_auc'] for r in selection_rows) / len(selection_rows) if valid else None
                trial_record = {'seed': seed, 'method': variant, 'trial': trial,
                                'learning_rate': outer_lr, 'selection_score': score,
                                'status': 'VALID' if valid else 'FAILED', 'failure': failed}
                trials.append(trial_record)
                store_json(f'neural-study/seed-{seed}/{variant}-trial-{trial:02}.json', {
                    'trial': trial_record, 'training_history': history,
                    'training_trajectories': training_rows, 'selection_trajectories': selection_rows})
                checkpoint = trainer.checkpoint()
                store_bytes(f'neural-study/seed-{seed}/{variant}-trial-{trial:02}.pt', checkpoint,
                            'application/octet-stream')
                if score is not None and score < best_score:
                    best_score = score
                    selected_policies[variant] = checkpoint
                    selected[variant] = {'trial': trial, 'learning_rate': outer_lr, 'score': score}
                run.append_event('neural_tuning_trial', trial_record)
            if variant not in selected_policies:
                seed_failures.append({'seed': seed, 'method': variant, 'reason': 'all_tuning_trials_failed'})

        store_json(f'neural-study/seed-{seed}/selection.json', selected)
        # Only now access the separate evaluation family. No evaluation-based selection.
        for method in ['sgd', 'momentum', 'adamw', *variants]:
            if method not in selected:
                continue
            if method in variants:
                policy = RecurrentUpdatePolicy(hidden=params['controller_hidden'], layers=params['controller_layers'],
                                               **VARIANTS[method])
                MetaTrainer(policy).restore(selected_policies[method])
            for horizon in horizons:
                rows = []
                for task in held:
                    trajectory = adapt(task, policy, horizon, gradient_mode='evaluation', ledger=ledger) if method in variants else fixed_adapt(
                        task, method, horizon, selected[method]['learning_rate'], ledger=ledger)
                    row = trajectory_record(task, method, trajectory, horizon)
                    row['training_seed'] = seed
                    rows.append(row)
                all_rows.extend(rows)
                store_json(f'neural-study/seed-{seed}/{method}-horizon-{horizon}.json', rows)
        run.append_event('neural_seed_complete', {'seed': seed, 'cost': ledger.snapshot()})
    summary = summarize(all_rows)
    expected_rows = len(seeds) * (3 + len(variants)) * len(horizons) * params['evaluation_tasks'] * len(params['evaluation_widths'])
    result = {
        'status': RunStatus.SUCCEEDED.value if len(all_rows) == expected_rows else RunStatus.FAILED.value,
        'study': 'qlearn-neural-development-v1', 'training_seeds': seeds,
        'expected_evaluation_rows': expected_rows, 'actual_evaluation_rows': len(all_rows),
        'tuning_trials_per_method_per_seed': len(etas), 'all_tuning_trials': trials,
        'failed_seed_methods': seed_failures, 'summary': summary,
        'cost': ledger.snapshot(), 'elapsed_seconds': time.perf_counter() - start,
        'research_outcome': 'NOT_EVALUATED',
        'scope_limitations': [
            'Development evidence; no externally frozen confirmation or independent reproduction.',
            'Constructed numerical regression, not the required natural image/sequence extensions.',
            'Matched support-gradient horizons and tuning-count budgets; total meta-training '
            'and wall-time costs are measured separately and are not equal.',
            'Discrete optimizer/replay/loss/rollback MALIS actions remain a separate incomplete delivery.',
            'Celo2/ELO and initialization-only external comparators are not implemented here.',
            'No inferential confidence interval or positive scientific claim is issued by this runner.',
        ],
        'artifacts': refs,
    }
    store_json('neural-study/summary.json', {k: v for k, v in result.items() if k != 'artifacts'})
    return result
