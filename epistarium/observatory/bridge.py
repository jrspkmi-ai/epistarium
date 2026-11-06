"""A restricted, run-scoped event channel for external research hosts.

Events are claims by the host, never proof that work happened or that a claim
is supported. The channel has no approval or evidence-promotion capability.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets

from .store import PERSONAS

SCHEMA = 'epistarium.agent-event.v1'
STATUSES = {'RUNNING', 'SUCCESS', 'PARTIAL', 'BLOCKED', 'FAILED'}
ACTORS = {'opencode', 'antigravity', 'cli', 'other'}
OPERATIONS = {'start','run','finish','read','write','search','extract','audit','export','handoff','error'}
IDENTIFIER = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$')
HEX64 = re.compile(r'^[a-f0-9]{64}$')
EVENT_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{7,79}$')
REQUIRED = {'schema_version', 'event_id', 'run_id', 'step_id', 'persona', 'actor', 'operation', 'status'}
OPTIONAL = {'parent_step_id', 'artifact_ref'}


def issue_capability(directory: Path) -> None:
    """Create a local secret, not exposed in HTTP responses or the event log."""
    path = directory / 'bridge.token'
    token = secrets.token_urlsafe(32)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii') as stream:
        stream.write(token + '\n')


def authorized(store, run_id: str, candidate: str) -> bool:
    if not isinstance(candidate, str) or len(candidate) > 200:
        return False
    try:
        path = store._dir(run_id) / 'bridge.token'
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 200:
            return False
        return secrets.compare_digest(path.read_text(encoding='ascii').strip().encode('ascii'), candidate.encode('utf-8'))
    except (OSError, ValueError, UnicodeError):
        return False


def _artifact(store, run_id, value):
    if not isinstance(value, dict) or set(value) != {'path', 'sha256'}:
        raise ValueError('artifact_ref must have path and sha256')
    relative, digest = value['path'], value['sha256']
    if not isinstance(relative, str) or not relative or len(relative) > 240 or '\\' in relative or '\0' in relative:
        raise ValueError('Invalid artifact path')
    parts = PurePosixPath(relative)
    if parts.is_absolute() or any(p in ('.', '..') for p in relative.split('/')) or ':' in relative:
        raise ValueError('Invalid artifact path')
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise ValueError('Invalid artifact digest')
    root = store._output(run_id).resolve()
    path = root
    for component in parts.parts:
        path = path / component
        if path.is_symlink():
            raise ValueError('Symlink artifact paths are not accepted')
    if root not in path.resolve().parents or not path.is_file() or path.stat().st_size > 100_000_000:
        raise ValueError('Artifact unavailable or too large')
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    if not secrets.compare_digest(h.hexdigest(), digest):
        raise ValueError('Artifact hash mismatch')
    return {'path': relative, 'sha256': digest, 'hash_checked_at_ingestion': True}


def ingest(store, run_id, payload):
    """Validate, append once, and retain agent provenance in the durable log."""
    if not isinstance(payload, dict) or not REQUIRED <= payload.keys() or set(payload) - REQUIRED - OPTIONAL:
        raise ValueError('Invalid event fields')
    from ..common import validate_schema
    validate_schema(payload,'agent_event')
    if payload['schema_version'] != SCHEMA or payload['run_id'] != run_id:
        raise ValueError('Invalid schema or run scope')
    if not isinstance(payload['event_id'], str) or not EVENT_ID.fullmatch(payload['event_id']):
        raise ValueError('Invalid event identifier')
    for key in ('step_id', 'operation'):
        if not isinstance(payload[key], str) or not IDENTIFIER.fullmatch(payload[key]):
            raise ValueError('Invalid event identifier')
    if payload['operation'] not in OPERATIONS:
        raise ValueError('Unsupported operation')
    parent = payload.get('parent_step_id')
    if parent is not None and (not isinstance(parent, str) or not IDENTIFIER.fullmatch(parent)):
        raise ValueError('Invalid parent step identifier')
    if payload['persona'] not in PERSONAS or payload['actor'] not in ACTORS or payload['status'] not in STATUSES:
        raise ValueError('Unsupported persona, actor or status')
    if payload['status'] == 'SUCCESS' and 'artifact_ref' not in payload:
        raise ValueError('SUCCESS reports require an existing artifact and hash')
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    fingerprint = hashlib.sha256(canonical).hexdigest()
    with store.lock:
        # Search the complete durable ledger, not only the 1000-event UI window.
        path = store._dir(run_id) / 'events.jsonl'
        if path.exists():
            with path.open(encoding='utf-8') as stream:
                for line in stream:
                    try:
                        row = json.loads(line)
                    except (ValueError, UnicodeError):
                        continue
                    if isinstance(row,dict) and row.get('kind') == 'agent_event' and row.get('source_event_id') == payload['event_id']:
                        if row.get('payload_sha256') != fingerprint:
                            raise ValueError('Event identifier already used for different content')
                        store.reconcile_agent_plan(run_id)
                        return {'accepted': True, 'duplicate': True, 'source_event_id': payload['event_id']}
        if store.get(run_id)['status'] in ('RELEASE_AUTHORIZED','REJECTED'):
            raise ValueError('Run is closed to new agent events')
        artifact = _artifact(store, run_id, payload['artifact_ref']) if 'artifact_ref' in payload else None
        fields = {key: payload[key] for key in ('step_id', 'persona', 'actor', 'operation', 'status')}
        fields.update(source_event_id=payload['event_id'], parent_step_id=parent,
                      payload_sha256=fingerprint, artifact_ref=artifact,
                      event_source='agent_reported', executor_identity=payload['actor'],
                      provenance='SELF_REPORTED',
                      message='Agent-reported activity; execution and evidence require independent review.')
        store._append(run_id, 'agent_event', **fields)
        store.reconcile_agent_plan(run_id)
    return {'accepted': True, 'duplicate': False, 'source_event_id': payload['event_id']}
