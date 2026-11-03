"""Check active guidance, discovery metadata, commands, contracts and version."""
from pathlib import Path
import json
import re
import sys
import tomllib
import yaml
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from epistarium import __version__


def verify():
    errors=[]
    skills=sorted((ROOT/'.agents/skills').glob('*/SKILL.md'))
    if len(skills)!=10:errors.append('Jumlah persona harus tepat sepuluh')
    commands=set(re.findall(r'add_parser\([\'"]([^\'"]+)',(ROOT/'epistarium/cli.py').read_text()))
    active=[ROOT/n for n in ('README.md','README.id.md','AGENTS.md','CHANGELOG.md','CHANGELOG.id.md','docs/en/START_HERE.md','docs/id/MULAI_DI_SINI.md')]
    active += [ROOT/'docs'/n for n in ('WORKFLOW.md','STATUS_GLOSSARY.md','MIGRATION_0.5.0.md','ROADMAP.md','SECURITY.md','PLATFORM_COMPATIBILITY.md','F4_CONTRACTS.md','RIGHTS_AND_DEPENDENCIES.md','F2_CONTRACTS.md','INDEX.md','EVIDENCE_PROTOCOL.md','F2_USER_GUIDE.md','F3_CONTRACTS.md','F3_USER_GUIDE.md','F4_USER_GUIDE.md','F4_SPECIFICATION.md')]
    active+=[ROOT/'docs/archive/AUDIT_DECISIONS_v0.5.0.md']
    active+=list((ROOT/'docs/en').glob('*.md'))+[ROOT/'docs/LANGUAGE.md',ROOT/'docs/MIGRATION_0.6.0.md',ROOT/'docs/style/SIMPLE_ENGLISH.md']
    active+=list((ROOT/'.agents/skills').glob('*/references/guide.*.md'))
    for p in skills:
        text=p.read_text(encoding='utf8')
        try:
            front=yaml.safe_load(text.split('---',2)[1])
            if set(front)!={'name','description'}:errors.append(f'{p.parent.name}: field frontmatter')
            if front['name']!=p.parent.name or not re.fullmatch(r'[a-z0-9-]{1,64}',front['name']):errors.append(f'{p.parent.name}: nama')
            if not isinstance(front['description'],str) or not 20<=len(front['description'])<=1024 or 'Gunakan ketika' not in front['description']:
                errors.append(f'{p.parent.name}: deskripsi aktivasi')
            if 'Use when' not in front['description']:errors.append(f'{p.parent.name}: English trigger missing')
            for language in ('id','en'):
                if not (p.parent/'references'/f'guide.{language}.md').is_file():errors.append(f'{p.parent.name}: guide {language} missing')
            if 'epistarium doctor' not in text:errors.append(f'{p.parent.name}: prasyarat doctor')
        except (ValueError,KeyError,TypeError,yaml.YAMLError):errors.append(f'{p.parent.name}: YAML invalid')
    for p in active+skills:
        if not p.is_file():errors.append(f'Dokumen aktif tidak ditemukan: {p.name}');continue
        text=p.read_text(encoding='utf8')
        for command in re.findall(r'python -m epistarium ([a-z][a-z0-9-]+)',text):
            if command not in commands:errors.append(f'{p.name}: perintah {command} tidak terdaftar')
        for path in re.findall(r'`((?:docs|schemas|tests|examples|reports|epistarium)/[A-Za-z0-9_./-]+)`',text):
            if not (ROOT/path).exists():errors.append(f'{p.name}: rujukan {path} tidak ditemukan')
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if target.startswith(('http:','https:','#')):continue
            target=target.split('#')[0]
            if target and not (p.parent/target).exists():errors.append(f'{p.name}: tautan {target} terputus')
    for p in (ROOT/'schemas').glob('*.schema.json'):
        try:
            schema=json.loads(p.read_text());Draft202012Validator.check_schema(schema)
            if schema!=json.loads((ROOT/'epistarium/data'/p.name).read_text()):errors.append(f'{p.name}: salinan paket berbeda')
        except (ValueError,OSError) as exc:errors.append(f'{p.name}: {type(exc).__name__}')
    config=tomllib.loads((ROOT/'pyproject.toml').read_text())
    if config['tool']['setuptools']['dynamic']['version']['attr']!='epistarium._version.__version__':errors.append('Versi distribusi tidak memakai sumber tunggal')
    return {'version':__version__,'skill_count':len(skills),'command_count':len(commands),
            'checked_document_count':len(active+skills),'status':'FAILED' if errors else 'SUCCESS','errors':errors}


if __name__=='__main__':
    result=verify()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if result['errors'] else 0)
