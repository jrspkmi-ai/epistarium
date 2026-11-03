"""Mechanical checks adapted from SimpleEnglish Plain. This is not a meaning test."""
from pathlib import Path
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
INSTRUCTION=re.compile(r'^(?:Use|Keep|Read|Run|Select|Record|Do not|Make sure|Treat|Pass|Set|Open|If|Before)\b')
WORDS=re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")


def check():
    paths=[ROOT/n for n in ('README.md','AGENTS.md','docs/en/START_HERE.md','CHANGELOG.md')]
    paths+=list((ROOT/'docs/en').glob('*.md'))
    paths+=list((ROOT/'.agents/skills').glob('*/references/guide.en.md'))
    paths+=[ROOT/'docs/style/SIMPLE_ENGLISH.md']
    paths += [ROOT / p['en'] for p in json.loads((ROOT/'docs/DOCS_MANIFEST.json').read_text())['pairs']]
    paths = sorted(set(paths))
    issues=[];counts=[]
    for path in paths:
        code=False
        for line_number,line in enumerate(path.read_text(encoding='utf8').splitlines(),1):
            if line.startswith('```'):
                code=not code
                continue
            if code or line.startswith(('#','|')):
                continue
            text=re.sub(r'`[^`]*`','CODE',line)
            text=re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',text)
            for sentence in re.split(r'(?<=[.!?])\s+',text.strip()):
                count=len(WORDS.findall(sentence))
                if not count:continue
                limit=20 if INSTRUCTION.match(sentence) else 25
                counts.append((count,path.relative_to(ROOT).as_posix(),line_number))
                if count>limit:issues.append({'file':path.relative_to(ROOT).as_posix(),'line':line_number,'rule':'sentence_length','words':count,'limit':limit})
            if '\u2014' in text or ';' in text:issues.append({'file':path.relative_to(ROOT).as_posix(),'line':line_number,'rule':'punctuation'})
            if re.search(r'\b(?:should|would|could|may|might|leverage|utilize|seamlessly)\b',text,re.I):
                issues.append({'file':path.relative_to(ROOT).as_posix(),'line':line_number,'rule':'word_choice'})
    return {'status':'FAILED' if issues else 'SUCCESS','document_count':len(paths),
            'three_longest_sentences':[{'words':n,'file':p,'line':line} for n,p,line in sorted(counts,reverse=True)[:3]],
            'issues':issues,'scope':'Static English prose only. Code, tables, source quotations, meaning, and dynamic input require separate review.',
            'source':'AminBlg/SimpleEnglish 2.1.1, Plain mode','certification':'NOT_CLAIMED'}


if __name__=='__main__':
    result=check()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if result['issues'] else 0)
