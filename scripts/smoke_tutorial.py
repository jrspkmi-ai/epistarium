"""Run the included synthetic tutorial, with explicit expected partial statuses."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import platform

ROOT = Path(__file__).resolve().parents[1]


def run(output, lang):
    base = Path(output).resolve()
    if base.exists():
        raise ValueError('Use a fresh tutorial output directory')
    config = json.loads((ROOT / 'examples/first_research_commands.json').read_text())
    commands = []
    for original, expected in zip(config['commands'], config['expected_exit_codes'], strict=True):
        args = [str(base) + v[len('private/first-research'):] if v.startswith('private/first-research') else v for v in original]
        args[args.index('--lang') + 1] = lang
        result = subprocess.run([sys.executable, '-I', '-m', 'epistarium', *args], cwd=ROOT, capture_output=True, text=True)
        commands.append({'command': ['python', '-I', '-m', 'epistarium', *args], 'expected_exit_code': expected,
                         'exit_code': result.returncode, 'status': 'PASS' if result.returncode == expected else 'FAIL',
                         'stdout': result.stdout, 'stderr': result.stderr})
    artifacts, failures = [], []
    from docx import Document
    from openpyxl import load_workbook
    from epistarium import pdf_backend
    for path in sorted(base.rglob('*')):
        if not path.is_file(): continue
        check = {'file': path.relative_to(base).as_posix(), 'size': path.stat().st_size,
                 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        try:
            if path.suffix == '.json': json.loads(path.read_text(encoding='utf8'))
            if path.suffix == '.docx': Document(path)
            if path.suffix == '.xlsx':
                book = load_workbook(path); book.close()
            if path.suffix == '.pdf':
                doc = pdf_backend.open(path); assert len(doc) > 0; doc.close()
            check['status'] = 'PASS'
        except Exception as exc:
            check['status'] = 'FAIL'; check['error'] = type(exc).__name__; failures.append(check['file'])
        artifacts.append(check)
    required = ['path/RUN_MANIFEST.json','map/ideon_origo.json','liora/candidates.json','retho/articles.json',
                'domares/critical_readings.json','synthia/database_literatur.xlsx','vanlan/contoh_sintetis_annotated.pdf',
                'full/FULL_RESEARCH_MANIFEST.json']
    missing = [p for p in required if not (base / p).is_file()]
    return {'version':'0.7.1','language':lang,'python':platform.python_version(),'platform':platform.platform(),
            'synthetic':True,'native_activation':'NOT_RUN', 'commands':commands, 'artifacts':artifacts,
            'required_artifact_count':len(required),'missing_required':missing,
            'status':'FAIL' if missing or failures or any(c['status']=='FAIL' for c in commands) else 'PASS'}


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--lang',choices=['en','id'],default='en');p.add_argument('--report',required=True)
    args=p.parse_args(); result=run(args.out,args.lang)
    Path(args.report).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ['status','version','language','missing_required']},indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)
