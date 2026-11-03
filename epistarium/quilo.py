"""Quilo F3: configurable writing lint, conservative edits, evidence-preserving diff.

An AI agent can propose context-sensitive rewriting, but this deterministic utility
never validates methodological argument or factual meaning by itself.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
import re
import difflib
from pathlib import Path
from .common import save_json, now_iso

PUBLIC_STYLE={'name':'academic-id','language':'id','rules':[
    {'pattern':r'(?i)\bperlu diketahui bahwa\b[\s,]*','replacement':'','why':'Pembuka yang menunda pokok kalimat'},
    {'pattern':r'(?i)\bpada kesempatan ini\b[\s,]*','replacement':'','why':'Pengantar tanpa informasi substansial'},
    {'pattern':r'(?i)\bseiring perkembangan zaman\b','replacement':None,'why':'Klaim kronologis tanpa batas waktu'},
    {'pattern':r'(?i)\bsangat penting\b','replacement':None,'why':'Penilaian kepentingan tanpa kriteria'},
    {'pattern':r'(?i)\bdalam konteks ini\b','replacement':None,'why':'Periksa apakah referen konteks jelas'},
    {'pattern':r'(?i)\bsecara fundamental\b','replacement':None,'why':'Penguat yang memerlukan bukti'}
]}
ENGLISH_STYLE={'name':'academic-en','language':'en','rules':[
    {'pattern':r'(?i)\bit is (?:important|worth noting) (?:to|that)\b','replacement':None,'why':'State the fact directly.'},
    {'pattern':r'(?i)\b(?:leverage|utilize|seamlessly|robust|comprehensive)\b','replacement':None,'why':'Use a common word or state the measurable fact.'},
    {'pattern':r'(?i)\bin order to\b','replacement':None,'why':'Consider using to.'},
    {'pattern':r'(?i)\b(?:should|would|may|might|could)\b','replacement':None,'why':'State the requirement or the uncertainty explicitly. Preserve the scientific claim.'},
    {'pattern':r'\u2014','replacement':None,'why':'Consider two sentences. Preserve the relation between the claims.'},
    {'pattern':r'(?i)\b(?:has|have) been\b','replacement':None,'why':'Consider a simple tense if the time and meaning stay intact.'},
]}
QUOTED=re.compile(r'[“”\"]([^“”\"]+)[“”\"]|«([^»]+)»')
NUMERIC=re.compile(r'(?<!\w)(?:\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)(?:%|\s*(?:orang|responden|informan|tahun|hari|bulan|people|respondents?|informants?|participants?|years?|days?|months?))?(?!\w)')
CITATIONS=re.compile(r'\([^()\n]*?(?:\b(?:19|20)\d{2}[a-z]?|n\.d\.)[^()\n]*\)',re.I)
DOIS=re.compile(r'10\.\d{4,9}/[^\s\]>)]+',re.I)


def read_manuscript(path):
    path=Path(path)
    if path.suffix.lower()=='.docx':
        from docx import Document
        doc=Document(path)
        blocks=[p.text for p in doc.paragraphs]
        blocks.extend(' | '.join(c.text for c in row.cells) for table in doc.tables for row in table.rows)
        return '\n'.join(blocks)
    if path.suffix.lower() not in ('.txt','.md','.markdown'):
        raise ValueError(tr('Quilo menerima TXT, Markdown, atau DOCX'))
    return path.read_text(encoding='utf8')


def protected_tokens(text):
    return {k: sorted(x.group(0) for x in r.finditer(text)) for k,r in
            [('quotes',QUOTED),('numbers',NUMERIC),('citations',CITATIONS),('doi',DOIS)]}


RISK_MARKERS=re.compile(r"\b(?:tidak|bukan|belum|tanpa|jangan|mustahil|semua|seluruh|sebagian|hanya|selalu|tidak\s+pernah|mungkin|dapat|pasti|harus|wajib|seharusnya|diduga|membuktikan|menemukan|meningkat|menurun|berkurang|bertambah|positif|negatif|not|never|without|no|all|only|some|always|must|can|will|may|might|possibly|increase[sd]?|decrease[sd]?|positive|negative)\b",re.I)
LOW_RISK_PREFIXES=[re.compile(r'(?i)\bperlu diketahui bahwa\b[\s,]*'), re.compile(r'(?i)\bpada kesempatan ini\b[\s,]*')]


@localized
def validate_revision(original,revised):
    """Conservative lexical guard. Never certifies semantic equivalence."""
    problems=[]
    a,b=protected_tokens(original),protected_tokens(revised)
    for key in a:
        if a[key]!=b[key]:problems.append({'type':'protected_content_changed','category':key,'before':a[key],'after':b[key]})
    aa=[x.group(0).lower() for x in RISK_MARKERS.finditer(original)]
    bb=[x.group(0).lower() for x in RISK_MARKERS.finditer(revised)]
    if aa!=bb:problems.append({'type':'semantic_risk_marker_changed','before':aa,'after':bb})
    # Token equality alone is insufficient; arbitrary edits are never greenlit.
    baseline=original
    for pattern in LOW_RISK_PREFIXES:
        baseline=pattern.sub('',baseline)
    low_risk=(original==revised or revised==baseline)
    if not low_risk and original!=revised:
        problems.append({'type':'unreviewed_semantic_change','note':tr('Perubahan leksikal di luar pembuka berisiko rendah memerlukan tinjauan manusia.')})
    token_ok=not any(x['type']=='protected_content_changed' for x in problems)
    candidate=not problems
    tier=('HARD_BLOCK' if not token_ok or aa!=bb else
          'TRIVIAL_SAFE' if low_risk else 'EDITORIAL_REVIEW')
    return {'safe_to_propose':candidate, 'protected_tokens_unchanged':token_ok,
            'revision_tier':tier,
            'semantic_validity':'NOT_ASSESSED', 'semantic_review_required':original!=revised,
            'problems':problems,'scope':'lexical_guard_not_semantic_fact_check',
            'meaning_review_required':True}


@localized
def lint(text, style=None):
    style=style or PUBLIC_STYLE
    issues=[]
    for rule in style.get('rules',[]):
        for match in re.finditer(rule['pattern'],text):
            issues.append({'start':match.start(),'end':match.end(),'text':match.group(0),
                           'reason':tr(rule['why']) if style is PUBLIC_STYLE or style is ENGLISH_STYLE else rule['why'],'suggestion':rule.get('replacement'),
                           'mode':'manual_review' if rule.get('replacement') is None else 'safe_candidate'})
    return issues


@localized
def suggested_revision(text,style=None):
    """Automates only localized low-risk removals, then token checks; not semantic rewriting."""
    style=style or PUBLIC_STYLE
    proposed=text
    edits=[]
    for rule in style.get('rules',[]):
        if rule.get('replacement') is None:continue
        matches=list(re.finditer(rule['pattern'],proposed))
        if matches:
            proposed=re.sub(rule['pattern'],lambda m:rule['replacement'],proposed)
            edits.append({'rule':rule['pattern'],'reason':rule['why'],'matches':len(matches)})
    validation=validate_revision(text,proposed)
    if not validation['safe_to_propose']:
        return text, [],validation
    return proposed,edits,validation


@localized
def audit(original, out_dir, *, revised=None, style=None):
    if not isinstance(original,str) or not original.strip():raise ValueError(tr('Naskah teks kosong'))
    p=Path(out_dir);p.mkdir(parents=True,exist_ok=True)
    issues=lint(original,style)
    generated,edits,check=suggested_revision(original,style)
    out={'schema_version':'f3.quilo.0.1','generated_at':now_iso(),
         'style':(style or PUBLIC_STYLE).get('name'),'issues':issues,
         'automated_edits':edits,'automated_token_guard':check,
         'semantic_validity':'NOT_ASSESSED','protected_tokens_unchanged':check['protected_tokens_unchanged'],'methodology_consistency':'NOT_ASSESSED',
         'preserves_evidence_claim':'ONLY_CHECKED_FOR_EXACT_QUOTES_NUMBERS_CITATIONS_DOI'}
    (p/'usulan_sunting.txt').write_text(generated,encoding='utf8')
    (p/'perubahan.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),generated.splitlines(True),fromfile='original',tofile='usulan')),encoding='utf8')
    if revised is not None:
        out['external_revision_check']=validate_revision(original,revised)
        (p/'external_revision.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),revised.splitlines(True),fromfile='original',tofile='external_revision')),encoding='utf8')
    save_json(p/'audit_quilo.json',out)
    lines=[tr('# Quilo: audit editorial'),'',f"Preset: {out['style']}",
        tr('Saran pemeriksaan: {v0}; penghapusan pengantar lokal: {v1}',v0=f'{len(issues)}', v1=f"{sum((e['matches'] for e in edits))}"),'',
        tr('Validasi makna, referensi, RQ, metode dan temuan **tidak dilakukan otomatis**.'),
        tr('Jangan terapkan usulan tanpa membaca naskah dan konteks.'),'']
    for issue in issues:
        lines.append(tr('- Posisi {v0}: `{v1}`. {v2}. ({v3})',v0=f"{issue['start']}", v1=f"{issue['text']}", v2=f"{issue['reason']}", v3=f"{issue['mode']}"))
    if revised is not None:
        lines+=['',tr('Revisi eksternal layak sebagai kandidat editorial terbatas: {v0}.',v0=f"{out['external_revision_check']['safe_to_propose']}"),
                tr('Tes token tidak membuktikan makna tidak berubah.')]
    (p/'laporan_quilo.md').write_text('\n'.join(lines),encoding='utf8')
    return out
