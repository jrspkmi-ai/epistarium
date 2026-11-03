"""Check local Markdown links, paired section scope, and catalog identity.

Structural parity cannot prove translation quality or scientific meaning.
"""
from pathlib import Path
import argparse
import json
import re
import sys
from urllib.parse import unquote
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
SECTION = re.compile(r'<!-- section: ([a-z0-9-]+) -->')
LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)')


def anchors(text):
    seen, values = {}, set()
    for line in text.splitlines():
        if not re.match(r'^#{1,6} ', line):
            continue
        value = re.sub(r'[`*_]', '', re.sub(r'^#+\s*', '', line)).lower()
        value = ''.join(c for c in value if c in ' -_' or c.isalnum() or unicodedata.category(c).startswith('L'))
        value = value.strip().replace(' ', '-')
        index = seen.get(value, 0)
        seen[value] = index + 1
        values.add(value if index == 0 else f'{value}-{index}')
    return values


def check(root=ROOT):
    manifest = json.loads((root / 'docs/DOCS_MANIFEST.json').read_text(encoding='utf8'))
    issues, pairs = [], manifest['pairs']
    paths = {root / p[lang] for p in pairs for lang in ('en', 'id')}
    paths |= {root / n for n in ('AGENTS.md', 'docs/AGENTS.id.md', 'THIRD_PARTY_NOTICES.md')}
    paths |= set((root / '.agents/skills').rglob('*.md'))
    paths |= {p for p in (root / 'reports/v0.7.0').glob('*.md')}
    paths |= {p for p in (root / 'reports/v0.7.1').glob('*.md')}
    pair_sections = 0
    for pair in pairs:
        texts = []
        for lang in ('en', 'id'):
            p = root / pair[lang]
            text = p.read_text(encoding='utf8') if p.is_file() else ''
            texts.append(text)
            ids = SECTION.findall(text)
            if ids != pair['sections']:
                issues.append(f'{pair[lang]}: section coverage mismatch')
        if texts[0] == texts[1]:
            issues.append(f"{pair['en']}: language editions are identical")
        pair_sections += len(pair['sections'])
    links = 0
    for p in sorted(paths):
        if not p.is_file():
            issues.append(f'Missing active document: {p.relative_to(root)}'); continue
        text = p.read_text(encoding='utf8')
        # Ignore fenced code, where Markdown targets can be example syntax.
        prose = re.sub(r'```.*?```', '', text, flags=re.S)
        for raw in LINK.findall(prose):
            if raw.startswith(('http:', 'https:', 'mailto:')):
                continue
            links += 1
            target, _, fragment = unquote(raw.strip('<>')).partition('#')
            resolved = (p.parent / target).resolve() if target else p.resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                issues.append(f'{p.relative_to(root)}: broken local link {raw}')
            elif fragment and resolved.suffix == '.md' and fragment not in anchors(resolved.read_text(encoding='utf8')):
                issues.append(f'{p.relative_to(root)}: missing anchor {raw}')
    catalog = json.loads((root / 'docs/PERSONAS.json').read_text(encoding='utf8'))
    actual = {p.parent.name for p in (root / '.agents/skills').glob('*/SKILL.md')}
    if len(catalog) != 10 or {p['slug'] for p in catalog} != actual:
        issues.append('Persona catalog and canonical skills differ')
    for p in catalog:
        for readme in ('README.md', 'README.id.md'):
            if any(p[k] not in (root / readme).read_text(encoding='utf8') for k in ('name', 'title', 'function', 'slug')):
                issues.append(f'{readme}: incomplete persona {p["name"]}')
    platforms = json.loads((root / 'docs/PLATFORMS.json').read_text(encoding='utf8'))
    if len(platforms) != 10:
        issues.append('Expected ten researched platform entries')
    for p in platforms:
        for lang in ('en', 'id'):
            path = root / f'docs/{lang}/platforms/{p["slug"]}.md'
            if not path.is_file() or p['official_source'] not in path.read_text(encoding='utf8'):
                issues.append(f'{p["slug"]}: missing official source in {lang}')
    return {'status': 'FAIL' if issues else 'PASS', 'version': manifest['version'], 'document_count': len(paths),
            'paired_document_count': len(pairs), 'paired_section_count': pair_sections, 'local_link_count': links,
            'persona_count': len(actual), 'platform_count': len(platforms), 'issues': issues,
            'scope': 'Local links and declared section parity. Semantic equivalence and native activation require separate review.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser();p.add_argument('--out')
    args = p.parse_args(); result = check()
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out: Path(args.out).write_text(output + '\n', encoding='utf8')
    print(output)
    raise SystemExit(1 if result['issues'] else 0)
