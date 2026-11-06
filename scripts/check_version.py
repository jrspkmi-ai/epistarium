"""Check active release metadata, not historical documents."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from epistarium._version import __version__

def check():
    issues=[]
    for name in ('RELEASE.json','docs/DOCS_MANIFEST.json'):
        if json.loads((ROOT/name).read_text(encoding='utf-8')).get('version')!=__version__:
            issues.append(name)
    for name in ('README.md','README.id.md','AGENTS.md','docs/AGENTS.id.md'):
        if f'v{__version__}' not in (ROOT/name).read_text(encoding='utf-8'):
            issues.append(name)
    for skill in sorted((ROOT/'.agents/skills').glob('*/SKILL.md')):
        if f'v{__version__}' not in skill.read_text(encoding='utf-8'):
            issues.append(str(skill.relative_to(ROOT)))
    return {'version':__version__,'issues':issues,'status':'FAIL' if issues else 'PASS'}

if __name__=='__main__':
    result=check();print(json.dumps(result,indent=2));raise SystemExit(bool(result['issues']))
