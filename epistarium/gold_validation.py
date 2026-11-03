"""Private validation adapter: compare candidate passage locations to user-reviewed workbook.

Overlap of cited page numbers measures *retrieval*, never semantic correctness.
Gold workbooks/PDFs remain outside source distribution.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from pathlib import Path
import re
from .common import save_json, now_iso
from ._version import __version__ as VERSION
from .liora import normalize_doi

FIELDS = {
    'desain': 7,
    'partisipan_unit': 9,
    'sampling': 10,
    'instrumen': 13,
    'analisis': 14,
    'teori_konsep': 15,
    'hasil': 16,
    'keterbatasan': 17,
}


def parse_pdf_pages(note):
    pages = set()
    text=str(note or '')
    for match in re.finditer(r'\bPDF\s*(?:hlm\.?|pages?|pp?\.?)\s*([0-9,\s\u2013-]+)', text, flags=re.I):
        chunk=match.group(1)
        for a,b in re.findall(r'(\d+)\s*[-\u2013]\s*(\d+)', chunk):
            lo, hi=int(a), int(b)
            if 0 < lo <= hi <= 10000 and hi-lo<200:
                pages.update(range(lo,hi+1))
        singles = re.sub(r'\d+\s*[-\u2013]\s*\d+',' ',chunk)
        pages.update(int(n) for n in re.findall(r'\d+',singles) if 0 < int(n) <= 10000)
    return pages


@localized
def compare_gold(readings, template_path, out_dir):
    from openpyxl import load_workbook
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    book=load_workbook(template_path,data_only=False)
    from .synthia import HEADERS,HEADERS_EN,literature_sheet,literature_header_row
    sheet=literature_sheet(book)
    head_row=literature_header_row(sheet)
    if head_row is None:raise ValueError(tr('Header workbook tidak ditemukan'))
    cols=[sheet.cell(head_row,c).value for c in range(1,21)]
    if len(cols)!=20 or str(cols[1]).strip() not in ('Penulis','Authors') or str(cols[19]).strip()!='Link':
        raise ValueError(tr('Skema workbook pengguna tidak cocok dengan matriks 20 kolom'))
    gold_rows=list(sheet.iter_rows(min_row=head_row+1,max_col=20,values_only=True))
    book.close()
    gold_index={}
    for row in gold_rows:
        doi=normalize_doi((row[19] or '').replace('https://doi.org/',''))
        if doi:gold_index[doi]=row
    comparisons=[]; uncovered=[]
    for r in readings:
        doi=normalize_doi(r.get('doi')); record=gold_index.get(doi)
        if record is None:
            uncovered.append({'doi':doi,'reason':'no_matching_gold_row'});continue
        for field,col in FIELDS.items():
            expected=parse_pdf_pages(record[col])
            candidates=(r.get('reported_by_author') or {}).get(field) or []
            actual={x.get('pdf_page') for x in candidates if isinstance(x.get('pdf_page'),int)}
            if not expected: status='GOLD_PAGE_UNAVAILABLE'
            elif not candidates: status='NO_CANDIDATE'
            elif expected & actual: status='PAGE_OVERLAP'
            else: status='NO_PAGE_OVERLAP'
            comparisons.append({'doi':doi,'field':field,'gold_pages':sorted(expected),
                'candidate_pages':sorted(actual),'status':status,
                'note':tr('Page overlap bukan bukti kesesuaian makna atau penilaian metode.')})
    counts={k:sum(x['status']==k for x in comparisons) for k in ['PAGE_OVERLAP','NO_PAGE_OVERLAP','NO_CANDIDATE','GOLD_PAGE_UNAVAILABLE']}
    result={'version':VERSION,'generated_at':now_iso(),'gold_rows':len(gold_index),
            'articles_evaluated':len({x['doi'] for x in comparisons}),
            'fields_evaluated':len(comparisons),'status_counts':counts,
            'semantic_accuracy':'NOT MEASURED','comparisons':comparisons,'missing_gold':uncovered}
    save_json(out/'gold_page_overlap.json',result)
    lines=[tr('# Domares: evaluasi kandidat berdasarkan review manusia'), '',
      tr('Ukuran: apakah halaman kandidat teks tumpang tindih dengan halaman rujukan pada workbook manusia. Ini bukan penilaian kesamaan metode, temuan, atau keterbatasan.'), '',
      tr('Artikel: {v0}; perbandingan bidang: {v1}.',v0=f"{result['articles_evaluated']}", v1=f'{len(comparisons)}'), '']
    lines.extend(f'- **{k}**: {v}' for k,v in counts.items())
    lines.extend(['',tr('**Akurasi semantik: NOT MEASURED.** Masih perlu pembacaan ahli dan adjudikasi isi per bidang.'),''])
    (out/'gold_page_overlap.md').write_text('\n'.join(lines),encoding='utf-8')
    return result
