"""Domares: conservative page-grounded candidate extraction from accessible PDFs.

This deterministic pass identifies candidate passages, not a full semantic review.
It never treats metadata/abstract as evidence for methodological or result fields.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
import re
from pathlib import Path
from . import pdf_backend as fitz
from .common import save_json, now_iso, sha256, validate_schema, require_unique_ids
from .vanlan import detect_printed_pages

from ._version import __version__ as VERSION
# Each pattern is intentionally an indicator of a passage, not proof that the field was answered.
CUES = {
 'masalah': [r'\bproblem\b',r'\bresearch gap\b',r'\blatar belakang\b',r'\bpermasalahan\b'],
 'tujuan': [r'\b(?:aim|objective|purpose)\s+(?:of|is|was|to)\b',r'\btujuan penelitian\b',r'\bbertujuan\b'],
 'teori_konsep': [r'\btheor(?:y|etical|ies)\b',r'\bframework\b',r'\bteori\b',r'\bkerangka konseptual\b'],
 'pertanyaan_hipotesis': [r'\bhypothes(?:is|es)\b',r'\bresearch question\b',r'\bhipotesis\b',r'\bpertanyaan penelitian\b'],
 'desain': [r'\b(?:cross.sectional|experimental|case study|mixed.methods|qualitative|quantitative|survey design)\b',r'\bstudi kasus\b',r'\bdesain penelitian\b'],
 'sumber_data': [r'\b(?:data source|dataset|data were collected|data collection)\b',r'\bsumber data\b'],
 'partisipan_unit': [r'\b(?:participants?|respondents?|sample size|interviewees?)\b',r'\b(?:partisipan|responden|informan|unit analisis)\b'],
 'sampling': [r'\b(?:sampling|recruitment|purposive|randomly assigned|convenience sample)\b',r'\b(?:purposif|pengambilan sampel|teknik sampling)\b'],
 'instrumen': [r'\b(?:questionnaire|interview guide|instrument|survey items|scale reliability)\b',r'\b(?:kuesioner|pedoman wawancara|instrumen penelitian)\b'],
 'analisis': [r'\b(?:regression|thematic analysis|content analysis|statistical analysis|coding procedure)\b',r'\b(?:analisis data|pengodean|regresi|analisis tematik)\b'],
 'hasil': [r'\b(?:results?|findings?)\b',r'\b(?:hasil penelitian|temuan penelitian)\b'],
 'keterbatasan': [r'\b(?:limitations?|small sample|generalizability)\b',r'\b(?:keterbatasan penelitian|keterbatasan studi)\b'],
 'penelitian_lanjutan': [r'\b(?:future research|further research|future studies|future work)\b',r'\b(?:penelitian selanjutnya|penelitian lanjutan)\b'],
}


def _paragraphs(text):
    # PDF line breaks are unreliable. Split into short blocks when possible.
    blocks = re.split(r'\n\s*\n+', text or '')
    if len(blocks) < 2:
        blocks = re.split(r'(?<=[.!?])\s+(?=[A-Z])', ' '.join((text or '').split()))
    return [re.sub(r'\s+', ' ', b).strip() for b in blocks if len(b.strip())>=25]


def _extract_pdf(pdf_path, max_chars=5_000_000):
    """Use Vanlan's corroborated pagination, never infer page numbers from a year."""
    pages=[]; total=0
    with fitz.open(pdf_path) as doc:
        pagination = detect_printed_pages(doc)
        for n,page in enumerate(doc):
            text=page.get_text(sort=True)
            total+=len(text)
            if total>max_chars: raise ValueError('text_char_limit_exceeded')
            label=page.get_label() if hasattr(page,'get_label') else None
            entry = pagination[n] if pagination else {}
            value = entry.get('printed_page')
            method = entry.get('printed_page_method') or tr('belum dapat ditentukan')
            pages.append({'pdf_page':n+1,'printed_page':value, 'printed_page_method':method,
                          'pdf_page_label':label, 'text':text})
    return pages


def _candidate_text(paragraph, field):
    """Remove DOI/URL identifiers and exclude explicit non-result assertions."""
    plain=re.sub(r'https?://\S+|\b10\.\d{4,9}/[^\s,;]+', ' ', paragraph,flags=re.I)
    if field=='hasil' and re.search(
        r'\b(?:no results? (?:are |were )?(?:available|reported|presented)|'
        r'no (?:study )?findings?|(?:does not|did not|has not|have not|not yet) '
        r'(?:report|present|have|provide) (?:any )?(?:results?|findings?|outcomes?)|'
        r'(?:results?|findings?) (?:are |were )?not (?:yet )?(?:available|reported|presented))\b', plain, re.I):
        return ''
    return plain


SECTION_HEADINGS={
    'abstract':r'abstract|abstrak',
    'introduction':r'introduction|pendahuluan|background|latar belakang',
    'methods':r'methods?|methodology|materials and methods|metode(?: penelitian)?|metodologi',
    'results':r'results?|findings|hasil(?: penelitian)?',
    'discussion':r'discussion|pembahasan|results and discussion|hasil dan pembahasan',
    'conclusion':r'conclusions?|kesimpulan|simpulan',
    'limitations':r'limitations?|keterbatasan(?: penelitian)?|future research',
    'references':r'references|bibliography|daftar pustaka|daftar rujukan',
}
METHOD_FIELDS={'desain','sumber_data','partisipan_unit','sampling','instrumen','analisis'}


def section_passages(pages):
    """Rank by detected section, retaining page provenance; stop at references."""
    section='unknown'
    for page in pages:
        buffer=[]
        def flush():
            return [(page,section,p) for p in _paragraphs('\n'.join(buffer))]
        for line in page['text'].splitlines():
            heading=re.sub(r'^\s*\d+(?:\.\d+)*[.)]?\s*','',line).strip().rstrip(':').casefold()
            found=next((k for k,v in SECTION_HEADINGS.items() if re.fullmatch(v,heading)),None)
            if found:
                yield from flush();buffer=[]
                section=found
                if section=='references':return
            else:buffer.append(line)
        yield from flush()


def section_score(field, section):
    preferred='methods' if field in METHOD_FIELDS else 'results' if field=='hasil' else 'limitations' if field in ('keterbatasan','penelitian_lanjutan') else 'introduction'
    return 3 if section==preferred else 2 if section in ('discussion','conclusion') else 0 if section=='abstract' else 1


@localized
def analyze(articles, out_dir, *, max_candidates_per_field=3):
    """Input Retho articles.json (list/dict). Never fill absence with conjecture."""
    if isinstance(articles,dict): articles=articles.get('articles',articles.get('records',[]))
    require_unique_ids(articles,'article_id')
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    reviews=[]
    for art in articles:
        result={key:art.get(key) for key in ('article_id','doi','title','authors','year','journal','article_type','publication_date','source_database','query_url','document_version','access_rights','status','source_identity_status','pdf_sha256','pdf_path','abstract')}
        result.update({'reviewed_at':now_iso(),'reading_level':'not_read','extraction_method':'keyword_passage_candidates_only',
                       'reported_by_author':{k:[] for k in CUES},'ai_audit_observations':[],
                       'requires_human_review':True,'completeness_warning':'', 'field_presence':{},
                       'integrity_status':'not_checked'})
        status=art.get('status')
        pdf=art.get('pdf_path')
        if status not in ('fulltext_local','pdf_needs_ocr') or not pdf:
            result['completeness_warning']=tr('Tidak ada full-text PDF yang dapat diproses; abstrak/metadata tidak digunakan untuk mengisi temuan dan metode.')
            reviews.append(result); continue
        if art.get('source_identity_status') in ('conflict','doi_title_unconfirmed'):
            result['completeness_warning']=tr('Konflik DOI/sumber; ekstraksi diblokir sampai identitas diselesaikan.')
            reviews.append(result);continue
        if not Path(pdf).is_file():
            result['completeness_warning']=tr('File PDF hilang saat tahap pembacaan.')
            reviews.append(result);continue
        # Compare Retho's recorded hash with the file actually read. The
        # pre/post check catches mutations during extraction as well.
        expected_hash=art.get('pdf_sha256')
        if not expected_hash:
            result['integrity_status']='missing_reference_hash'
            result['reading_level']='identity_or_integrity_conflict'
            result['completeness_warning']=tr('Hash sumber dari Retho tidak tersedia; pembacaan otomatis diblokir.')
            reviews.append(result); continue
        current_hash=sha256(pdf)
        if current_hash != expected_hash:
            result['integrity_status']='hash_mismatch'
            result['reading_level']='identity_or_integrity_conflict'
            result['completeness_warning']=tr('PDF telah berubah sejak pemeriksaan Retho; hentikan pembacaan.')
            result['ai_audit_observations'].append({'type':'source_modified','expected_sha256':expected_hash,'observed_sha256':current_hash})
            reviews.append(result); continue
        try:
            pages=_extract_pdf(pdf)
        except Exception as exc:
            result['completeness_warning']=tr('PDF gagal diekstraksi: ')+type(exc).__name__
            reviews.append(result); continue
        after_hash=sha256(pdf)
        if after_hash != expected_hash:
            result['integrity_status']='hash_changed_during_read'
            result['reading_level']='identity_or_integrity_conflict'
            result['completeness_warning']=tr('PDF berubah selama pembacaan; hasil sementara dibatalkan.')
            reviews.append(result); continue
        result['integrity_status']='hash_matched_before_after'
        result['page_count']=len(pages)
        result['reading_level']='machine_fulltext_extracted' if sum(len(p['text'].strip()) for p in pages)>=150 else 'pdf_without_sufficient_machine_text'
        if result['reading_level']!='machine_fulltext_extracted':
            result['completeness_warning']=tr('Teks mesin tidak cukup; perlu OCR atau telaah manual.')
            reviews.append(result); continue
        if art.get('source_identity_status')!='doi_matched':
            result['ai_audit_observations'].append({'type':'identity_unconfirmed','note':tr('PDF dapat dibaca, tetapi identitas DOI belum terkonfirmasi oleh Retho.')})
        passages=list(section_passages(pages))
        for key,patterns in CUES.items():
            for p,section,paragraph in sorted(passages,key=lambda item:-section_score(key,item[1])):
                if len(result['reported_by_author'][key])>=max_candidates_per_field:break
                clean = _candidate_text(paragraph, key)
                if clean and any(re.search(pattern,clean,flags=re.I) for pattern in patterns):
                        result['reported_by_author'][key].append({'excerpt':paragraph[:600],
                         'detected_section':section,'selection_score':section_score(key,section),
                         'pdf_page':p['pdf_page'],'printed_page':p['printed_page'],'pdf_page_label':p['pdf_page_label'],
                         'source':'pdf_fulltext', 'printed_page_method':p.get('printed_page_method'),
                         'verification_status':tr('kandidat teks; perlu verifikasi makna dan konteks')})
        result['field_presence']={k:('candidate_found' if v else 'not_identified_by_heuristic') for k,v in result['reported_by_author'].items()}
        result['ai_audit_observations'].append({'type':'method_limit','note':tr('Penanda kata hanya mencari kandidat bagian teks; ketidaktertemuan bukan bukti ketiadaan konsep, temuan atau keterbatasan.')})
        reviews.append(result)
    validate_schema(reviews,'domares_readings')
    save_json(out/'critical_readings.json', reviews)
    lines=[tr('# Domares: laporan pembacaan kritis (kandidat otomatis)'),'',
           tr('Penanda otomatis bukan hasil telaah kritis manusia. Data tanpa full-text tidak diberi temuan atau metode.'),'']
    for r in reviews:
        found=sum(bool(x) for x in r['reported_by_author'].values())
        lines.append(tr('- **{v0}** {v1}: `{v2}`; {v3}/{v4} bidang memiliki kandidat; identitas `{v5}`. {v6}',v0=f"{r.get('article_id')}", v1=f"{r.get('title')}", v2=f"{r['reading_level']}", v3=f'{found}', v4=f'{len(CUES)}', v5=f"{r.get('source_identity_status')}", v6=f"{r['completeness_warning']}"))
    (out/'reading_report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    return reviews
