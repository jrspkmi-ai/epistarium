"""Explicit workflow contracts; a plan is not a record of execution."""
from __future__ import annotations

import copy
from .store import PERSONAS, atomic_json

DEPENDENCIES = {
    'Jorhas': [], 'Liora': ['Jorhas'], 'Agresa': ['index_journals', 'index_evidence'],
    'Retho': ['Liora'], 'Domares': ['Retho'], 'Synthia': ['Domares_fulltext'],
    'Vanlan': ['vanlan_claims', 'vanlan_pdf_dir'], 'Ideon': ['Jorhas'],
    'Quilo': ['Ideon'], 'Huxley': ['huxley_docx'],
}


def make_plan(run_id, mode):
    return {
        'schema': 'epistarium.workflow-plan.v1', 'research_run_id': run_id,
        'mode': mode, 'plan_is_not_execution': True,
        'steps': [{'step_id': name.lower(), 'parent_step_id': None if name == 'Jorhas' else 'jorhas',
                   'persona': name, 'dependencies': DEPENDENCIES[name],
                   'execution_status': 'NOT_RUN', 'deliverable_status': 'NOT_RUN',
                   'evidence_status': 'NOT_ASSESSED', 'review_status': 'PENDING',
                   'approval_status': 'NOT_REQUESTED', 'executor_identity': None,
                   'event_source': None, 'reason': 'Not yet executed', 'artifact_refs': []}
                  for name in PERSONAS],
        'rule': 'Do not run a specialist without its required input; no status establishes scientific validity.',
    }


def save_plan(store, run_id):
    plan = make_plan(run_id, store.get(run_id)['mode'])
    atomic_json(store._dir(run_id) / 'WORKFLOW_PLAN.json', plan)
    return plan


def record_observed_step(store, run_id, persona, status, *, reason=None, artifacts=None):
    from .store import read_json
    path = store._dir(run_id) / 'WORKFLOW_PLAN.json'
    with store.lock:
        plan = read_json(path) or make_plan(run_id, store.get(run_id)['mode'])
        for step in plan['steps']:
            if step['persona'] == persona:
                step.update(execution_status=status, executor_identity='epistarium_python',
                            event_source='runtime_observed', reason=reason,
                            deliverable_status='CREATED' if artifacts else 'NOT_ASSESSED',
                            artifact_refs=copy.deepcopy(artifacts or []))
                if status == 'NOT_RUN':
                    step['executor_identity'] = None
                break
        atomic_json(path, plan)

