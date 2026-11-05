"""Patch an existing optimized GitHub Actions file; preserve CI rules and matrix."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'.github/workflows/checks.yml'
s=p.read_text(encoding='utf-8')
if 'EPISTARIUM_v0.7.1_RELEASE_CANDIDATE.zip' not in s and 'EPISTARIUM_v0.8.0_RELEASE_CANDIDATE.zip' not in s:
    raise RuntimeError('Unexpected workflow version; no changes written')
s=s.replace('EPISTARIUM_v0.7.1_RELEASE_CANDIDATE.zip','EPISTARIUM_v0.8.0_RELEASE_CANDIDATE.zip')
s=s.replace('name: EPISTARIUM candidate checks','name: EPISTARIUM v0.8.0 candidate checks',1)
marker='      - run: python -m pytest -q'
new='      - run: python -m epistarium observatory --help\n      - run: node --check epistarium/observatory/static/app.js\n'+marker
if marker not in s and new not in s:raise RuntimeError('Expected pytest step missing; no changes written')
s=s.replace(marker,new) if new not in s and 'node --check epistarium/observatory/static/app.js' not in s else s
p.write_text(s,encoding='utf-8')
print('CI updated while preserving workflow triggers and matrix')
