"""Synthia: evidence-gated literature matrix, with optional template-preserving XLSX.

The 20-column matrix remains stable. Source excerpts in every populated analytical
field are explicitly marked unverified pending human reading. Artifacts contain no PDFs.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from pathlib import Path
import re
import unicodedata
from .common import save_csv, save_json, now_iso, validate_schema

from ._version import __version__ as VERSION
HEADERS=['No','Penulis','Tahun','Judul','Tipe artikel','Latar Belakang','Tujuan /Perumusan masalah',
'Metode/strategi penelitian','Metode pengumpulan data','Jumlah','Metode pengambil sampel/informan',
'Karakteristik partisipan/sampel','Lokasi','Skala dan Sumber','Analisis Data','Teori/Konsep',
'Temuan','Kekurangan/Limitations','Future Research','Link']
HEADERS_EN=['No','Authors','Year','Title','Article type','Background','Aim / Research problem',
'Research design / Method','Data collection method','Sample size','Sampling method',
'Participant / Sample characteristics','Location','Scale and source','Data analysis','Theory / Concepts',
'Findings','Limitations','Future research','Link']


def literature_sheet(workbook):
    candidates=[workbook[name] for name in ('Database Literatur','Literature Database') if name in workbook.sheetnames]
    if len(candidates)!=1:raise ValueError(tr('Workbook harus memiliki tepat satu lembar literatur ID atau EN'))
    return candidates[0]


def literature_header_row(sheet):
    accepted=[[h.strip() for h in headers] for headers in (HEADERS,HEADERS_EN)]
    return next((n for n in range(1,16) if [str(sheet.cell(n,c).value or '').strip() for c in range(1,21)] in accepted),None)

FIELDS={5:'masalah',6:'tujuan',7:'desain',8:'sumber_data',10:'sampling',14:'analisis',15:'teori_konsep',16:'hasil',17:'keterbatasan',18:'penelitian_lanjutan'}


def safe_spreadsheet_literal(value):
    """Never turn untrusted bibliographic strings into executable sheet formulas."""
    if isinstance(value,str) and value.lstrip().startswith(('=', '+', '-', '@')):
        return "'"+value
    return value


def _clip(s, n=240):
    return re.sub(r'\s+',' ',str(s or '')).strip()[:n]


def _render_candidates(reading, key, audit, rid):
    fragments=(reading.get('reported_by_author') or {}).get(key) or []
    if reading.get('reading_level')!='machine_fulltext_extracted':return ''
    if not fragments:return ''
    v=[]
    for fragment in fragments[:2]:
        pg=fragment.get('pdf_page'); pp=fragment.get('printed_page')
        excerpt=_clip(fragment.get('excerpt'),190)
        v.append(tr('Kandidat teks PDF hlm. {v0}',v0=f'{pg}')+(tr(' (cetak {v0})',v0=f'{pp}') if pp is not None else '')+f": {excerpt}")
        audit.append({'article_id':rid,'field':key,'pdf_page':pg,'printed_page':pp,
                      'excerpt':excerpt,'verification_status':tr('kandidat; belum divalidasi makna'),
                      'source_pdf_sha256':reading.get('pdf_sha256'),'source_identity_status':reading.get('source_identity_status')})
    return '\n'.join(v)


@localized
def matrix(readings):
    if isinstance(readings,dict): readings=readings.get('readings',readings.get('records',[]))
    rows=[]; audit=[]
    for num,r in enumerate(readings,1):
        row=dict.fromkeys(HEADERS,'')
        row.update({tr('No'):num,'Penulis':r.get('authors') or '',
                    'Tahun':r.get('year') or '', 'Judul':r.get('title') or '',
                    'Tipe artikel':r.get('article_type') or '',
                    'Link':('https://doi.org/'+r['doi']) if r.get('doi') else (r.get('query_url') or '')})
        if r.get('reading_level')=='machine_fulltext_extracted':
            for idx,field in FIELDS.items():
                row[HEADERS[idx]]=_render_candidates(r,field,audit,r.get('article_id'))
            # A number in arbitrary sentences cannot establish sample size.
            row['Jumlah']=tr('Belum diverifikasi dari uraian sampel dalam PDF')
            row['Karakteristik partisipan/sampel']=tr('Perlu ekstraksi/validasi manual')
            row['Lokasi']=tr('Perlu ekstraksi/validasi manual')
            row['Skala dan Sumber']=tr('Perlu ekstraksi/validasi manual')
        else:
            for col in HEADERS[5:19]: row[col]=tr('Belum dinilai (full-text tidak tersedia/terekstraksi)')
        rows.append(row)
    return rows,audit


def _summary(readings, rows):
    total=len(readings)
    full=[r for r in readings if r.get('reading_level')=='machine_fulltext_extracted']
    fields={k:sum(bool((r.get('reported_by_author') or {}).get(k)) for r in full) for k in ('masalah','tujuan','teori_konsep','desain','analisis','hasil','keterbatasan','penelitian_lanjutan')}
    years=sorted({str(r['year']) for r in readings if r.get('year')})
    report=[
        tr('# Synthia: sintesis literatur sementara'),'',
        tr('Waktu produksi: {v0}',v0=f'{now_iso()}'),'',
        tr('Artikel terdaftar: **{v0}**. PDF yang berhasil diekstraksi sebagai teks mesin: **{v1}**.',v0=f'{total}', v1=f'{len(full)}'),'',
        tr('**Batas interpretasi:** hasil ini memetakan kandidat bukti yang ditemukan secara heuristik. Belum menjadi systematic review, penilaian kualitas metodologi, atau konfirmasi kebaruan.'),'',
        tr('Tahun publikasi yang tercatat: {v0}.',v0=f"{', '.join(years) or 'tidak tersedia'}"),'',
        tr('## Sintesis tematik'),'',
        tr('Tema substantif belum dapat ditetapkan otomatis tanpa pembacaan argumentasi dan pengelompokan konsep yang diverifikasi. Gunakan kandidat bagian hasil, teori dan masalah pada matriks sebagai bahan pengodean tematik.'),'',
        tr('## Perbandingan metode'),'',
        tr('Kandidat passage desain terdeteksi pada **{v0}** artikel dan analisis pada **{v1}** artikel yang dapat diproses. Deteksi bukan verifikasi desain.',v0=f"{fields['desain']}", v1=f"{fields['analisis']}"),'',
        tr('## Persamaan, perbedaan dan kontradiksi temuan'),'',
        tr('Kandidat passage hasil terdeteksi pada **{v0}** artikel. Belum ada adjudikasi persamaan maupun pertentangan lintas studi; bagian ini memerlukan penelaahan substantif.',v0=f"{fields['hasil']}"),'',
        tr('## Keterbatasan dan penelitian lanjutan'),'',
        tr('Kandidat bagian keterbatasan terdeteksi pada **{v0}** artikel; penelitian lanjutan pada **{v1}** artikel. Ketidakterdeteksian bukan berarti penulis tidak melaporkannya.',v0=f"{fields['keterbatasan']}", v1=f"{fields['penelitian_lanjutan']}"),'',
        '## Research gap','',
        tr('Belum cukup bukti untuk mengklaim kesenjangan pengetahuan definitif. Perlu pemeriksaan cakupan pencarian, sintesis temuan yang diverifikasi, studi paling dekat dan penelitian mutakhir. Tidak ditemukannya sebuah artikel bukan bukti bahwa studi tersebut tidak ada.'),'',
        tr('## Langkah verifikasi'),'',
        tr('Periksa semua cuplikan pada halaman PDF, selesaikan konflik identitas dokumen, isi rincian sampel/lokasi/skala dengan pembacaan manual, dan bandingkan temuan lintas studi sebelum menulis klaim kesenjangan.'),''
    ]
    return '\n'.join(report)


@localized
def export(readings,out_dir,*, template_xlsx=None, xlsx=True):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    if isinstance(readings,dict):readings=readings.get('readings',readings.get('records',[]))
    rows,audit=matrix(readings)
    save_csv(out/'database_literatur.csv',rows,HEADERS)
    save_csv(out/'audit_bukti.csv',audit,['article_id','field','pdf_page','printed_page','excerpt','verification_status','source_pdf_sha256','source_identity_status'])
    save_json(out/'database_literatur.json',validate_schema({'language':get_language(),'display_columns':HEADERS_EN if get_language()=='en' else HEADERS,'columns':HEADERS,'records':rows,'source':'Domares critical_readings.json','evidence_level':'draft_requires_human_review'},'synthia_matrix'))
    (out/'sintesis_sementara.md').write_text(_summary(readings,rows),encoding='utf8')
    excel_status='not_requested'
    if xlsx:
        try:
            _export_xlsx(rows,audit,out/'database_literatur.xlsx',template_xlsx=template_xlsx)
            excel_status='created'
        except (ImportError,ModuleNotFoundError) as ex:
            excel_status='dependency_not_available: '+type(ex).__name__
        except Exception as ex:
            excel_status='failed: '+type(ex).__name__+': '+str(ex)[:150]
    merge_audit_path=out/'template_merge_audit.json'
    merge_audit=None
    if excel_status=='created' and merge_audit_path.is_file():
        from .common import load_json
        merge_audit=load_json(merge_audit_path)
    save_json(out/'export_status.json',{'language':get_language(),'xlsx_status':excel_status,'template_path':str(template_xlsx) if template_xlsx else None,
                                      'template_merge_audit_file':'template_merge_audit.json' if merge_audit is not None else None,
                                      'template_existing_records':merge_audit.get('existing_rows_preserved') if merge_audit else None,
                                      'template_appended_records':merge_audit.get('appended_count') if merge_audit else None,
                                      'template_duplicates_skipped':len(merge_audit.get('skipped_existing',[])) if merge_audit else None,
                                      'template_identity_conflicts':len(merge_audit.get('conflicting_identity',[])) if merge_audit else None,
                                      'template_imported':bool(template_xlsx) and excel_status=='created',
                                      'preserved_format_verified':False,
                                      'record_count':len(rows),'generated_at':now_iso()})
    return {'rows':rows,'audit':audit,'xlsx_status':excel_status}


def _title_key(title):
    text = unicodedata.normalize('NFKD', str(title or '')).casefold()
    return ' '.join(re.findall(r'[a-z0-9]+', text.split('\n')[0]))


def _doi_key(value):
    s=str(value or '').strip()
    m=re.search(r'10\.\d{4,9}/[^\s<>]+',s,flags=re.I)
    return m.group(0).rstrip('.,;]').casefold() if m else ''


def _export_xlsx(rows, audit, path, *, template_xlsx=None):
    """Append to a user workbook using portable openpyxl; source is never saved."""
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    def literal(sheet, row_number, column, value):
        cell = sheet.cell(row_number, column)
        cell.value = value
        # Force all source strings to text, including leading =,+,-,@ and tabs.
        if isinstance(value, str):
            cell.data_type = 's'
        cell.alignment = Alignment(wrap_text=True, vertical='top')
        return cell

    review = {'source_template': str(template_xlsx) if template_xlsx else None,
              'incoming_count': len(rows), 'existing_rows_preserved': 0,
              'skipped_existing': [], 'conflicting_identity': [], 'appended_count': 0,
              'note': tr('Isian manusia dan lembar lain dipertahankan; kandidat mesin ditambahkan.')}
    if template_xlsx:
        if Path(template_xlsx).resolve() == Path(path).resolve():
            raise ValueError(tr('Keluaran harus berbeda dari template sumber'))
        wb = load_workbook(template_xlsx, data_only=False, keep_links=True)
        sheet = literature_sheet(wb)
        head_row = literature_header_row(sheet)
        if head_row is None:raise ValueError(tr('Header template tidak sesuai 20 kolom resmi'))
    else:
        wb = Workbook()
        sheet = wb.active
        sheet.title = 'Literature Database' if get_language()=='en' else 'Database Literatur'
        head_row = 1
        for c,h in enumerate(HEADERS_EN if get_language()=='en' else HEADERS,1):literal(sheet,1,c,h)
        sheet.freeze_panes = 'A2'
        for c in range(1,21):
            cell=sheet.cell(1,c);cell.fill=PatternFill('solid',fgColor='133A52')
            cell.font=Font(bold=True,color='FFFFFF')
            sheet.column_dimensions[get_column_letter(c)].width = 10 if c in (1,3) else 32
        helper=wb.create_sheet('Column Guide' if get_language()=='en' else 'Penjelasan Kolom')
        helper.append([tr('No'),tr('Nama kolom'),tr('Keterangan kolom')])
        for i,h in enumerate(HEADERS_EN if get_language()=='en' else HEADERS,1):
            helper.append([i,h,tr('Kandidat otomatis memerlukan pemeriksaan halaman PDF dan konteks.')])
        helper.column_dimensions['B'].width=32
        helper.column_dimensions['C'].width=72
    last=head_row;old_ids=[];old_dois=set();old_titles={}
    for n in range(head_row+1,sheet.max_row+1):
        old=[sheet.cell(n,c).value for c in range(1,21)]
        if not any(v not in (None,'') for v in old):continue
        last=n;review['existing_rows_preserved']+=1
        doi=_doi_key(old[19]);key=(_title_key(old[3]),str(old[2] or '').strip())
        if doi:old_dois.add(doi)
        if key[0]:old_titles[key]=doi
        try:old_ids.append(int(old[0]))
        except (ValueError,TypeError):pass
    next_number=max(old_ids,default=0)
    for row in rows:
        doi=_doi_key(row.get('Link'));title=_title_key(row.get('Judul'))
        key=(title,str(row.get('Tahun') or '').strip())
        if doi and doi in old_dois:
            review['skipped_existing'].append({'title':row.get('Judul'),'doi':doi,'reason':'doi_in_existing_template'})
            continue
        if title and key in old_titles:
            olddoi=old_titles[key]
            if doi and olddoi and doi!=olddoi:
                review['conflicting_identity'].append({'title':row.get('Judul'),'incoming_doi':doi,'existing_doi':olddoi})
            else:
                review['skipped_existing'].append({'title':row.get('Judul'),'doi':doi,'reason':'same_title_and_year'})
            continue
        last+=1;next_number+=1
        for c,h in enumerate(HEADERS,1):literal(sheet,last,c,next_number if h==tr('No') else row.get(h,''))
        review['appended_count']+=1
        if doi:old_dois.add(doi)
        if title:old_titles[key]=doi
    headers=['article_id','field','pdf_page','printed_page','excerpt','verification_status','source_pdf_sha256','source_identity_status']
    audit_names=[n for n in ('Audit F2','Evidence Audit') if n in wb.sheetnames]
    if len(audit_names)>1:raise ValueError(tr('Lebih dari satu lembar audit ditemukan'))
    audit_sheet=wb[audit_names[0]] if audit_names else wb.create_sheet('Evidence Audit' if get_language()=='en' else 'Audit F2')
    if not audit_names:
        for letter,width in {'A':22,'B':24,'C':12,'D':14,'E':80,'F':42,'G':28,'H':26}.items():
            audit_sheet.column_dimensions[letter].width=width
        audit_sheet.freeze_panes='A2'
    existing=[audit_sheet.cell(1,c).value for c in range(1,9)]
    if any(v not in (None,'') for v in existing) and existing != headers:
        raise ValueError(tr('Audit F2 memiliki header berbeda; lembar tidak ditimpa'))
    for c,h in enumerate(headers,1):literal(audit_sheet,1,c,h)
    for row in audit:
        n=audit_sheet.max_row+1
        for c,h in enumerate(headers,1):literal(audit_sheet,n,c,row.get(h))
    wb.save(path)
    reopened=load_workbook(path,data_only=False)
    if literature_sheet(reopened).max_column < 20:raise ValueError(tr('Reopen check XLSX gagal'))
    reopened.close();wb.close()
    save_json(Path(path).with_name('template_merge_audit.json'),review)
