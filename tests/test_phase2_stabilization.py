"""F2 stabilization regression tests: bugs from independent adversarial audit."""
from pathlib import Path
import fitz
import json
import pytest
from epistarium import retho, domares, synthia


def create_pdf(path, title='A controlled academic paper about communication', doi='10.1234/right.2025', footer='1', ref_doi=None, negated_results=False):
    doc=fitz.open()
    page=doc.new_page()
    page.insert_text((50,60),title,fontsize=15)
    if doi: page.insert_text((50,85),'DOI: '+doi)
    body=['This study has twenty participants and uses qualitative interviews.',
          'The methodological framework uses empirical content analysis.',
          'The research question concerns public communication and online behavior.']
    if negated_results:
        body+=['The study does not report any results or findings at this point.']
    else:
        body+=['Results show communication sources change trust perception.']
    for j,t in enumerate(body):page.insert_text((50,135+j*30),t,fontsize=10)
    if ref_doi:
        page.insert_text((50,350),'References',fontsize=12)
        page.insert_text((50,370),'Cited work https://doi.org/'+ref_doi,fontsize=9)
    page.insert_text((300,805),footer)
    doc.save(path); doc.close()
    return path


def candidate(doi='10.1234/right.2025',title='A controlled academic paper about communication'):
    return {'article_id':'study-1','doi':doi,'title':title,'authors':'Test Researcher',
            'year':2025,'type':'journal-article','available_level':'metadata'}


def test_doi_appears_only_in_references_cannot_verify_pdf(tmp_path):
    path=create_pdf(tmp_path/'paper.pdf',doi=None,ref_doi='10.1234/right.2025')
    result=retho.build([candidate()],tmp_path/'ret',{'10.1234/right.2025':{'pdf_path':str(path)}})[0]
    assert result['source_identity_status']=='unconfirmed'
    assert result['status']=='identity_review_required'
    assert domares.analyze([result],tmp_path/'dom')[0]['reading_level']=='not_read'


def test_wrong_title_with_matching_doi_requires_review(tmp_path):
    path=create_pdf(tmp_path/'paper.pdf',title='Completely different study of molecules and enzymes')
    result=retho.build([candidate()],tmp_path/'ret',{'10.1234/right.2025':{'pdf_path':str(path)}})[0]
    assert result['source_identity_status']=='doi_title_unconfirmed'
    assert result['status']=='identity_review_required'
    assert domares.analyze([result],tmp_path/'dom')[0]['reading_level']=='not_read'


def test_matching_identity_then_pdf_mutated_detects_hash(tmp_path):
    path=create_pdf(tmp_path/'paper.pdf')
    item=retho.build([candidate()],tmp_path/'ret',{'10.1234/right.2025':{'pdf_path':str(path)}})[0]
    assert item['status']=='fulltext_local'
    create_pdf(tmp_path/'other.pdf', title='A second uncontrolled paper',doi='10.5555/other')
    path.write_bytes((tmp_path/'other.pdf').read_bytes())
    review=domares.analyze([item],tmp_path/'dom')[0]
    assert review['reading_level']=='identity_or_integrity_conflict'
    assert review['integrity_status']=='hash_mismatch'
    assert not any(review['reported_by_author'].values())


def test_retho_hash_missing_cannot_be_worked_around(tmp_path):
    path=create_pdf(tmp_path/'paper.pdf')
    item=retho.build([candidate()],tmp_path/'ret',{'10.1234/right.2025':{'pdf_path':str(path)}})[0]
    item['pdf_sha256']=None
    review=domares.analyze([item],tmp_path/'dom')[0]
    assert review['integrity_status']=='missing_reference_hash'
    assert review['reading_level']=='identity_or_integrity_conflict'


def test_footer_year_not_printed_page(tmp_path):
    path=create_pdf(tmp_path/'paper.pdf',footer='2026')
    item=retho.build([candidate()],tmp_path/'ret',{'10.1234/right.2025':{'pdf_path':str(path)}})[0]
    review=domares.analyze([item],tmp_path/'dom')[0]
    assert review['reading_level']=='machine_fulltext_extracted'
    assert all(x.get('printed_page') != 2026 for fields in review['reported_by_author'].values() for x in fields)


def test_no_result_sentence_does_not_create_finding(tmp_path):
    path=create_pdf(tmp_path/'paper.pdf',negated_results=True)
    item=retho.build([candidate()],tmp_path/'ret',{'10.1234/right.2025':{'pdf_path':str(path)}})[0]
    review=domares.analyze([item],tmp_path/'dom')[0]
    assert review['reading_level']=='machine_fulltext_extracted'
    assert not review['reported_by_author']['hasil']


def test_oa_rights_metadata_never_authorizes_download(tmp_path,monkeypatch):
    calls=[]
    monkeypatch.setattr(retho,'_fetch_public_pdf',lambda *a,**k:calls.append((a,k)))
    data={'10.1234/right.2025':{'oa_locations':[{'url_for_pdf':'https://example.org/public.pdf',
       'license':'cc-by-4.0','rights_basis':'confirmed_public_oa'}]}}
    item=retho.build([candidate()],tmp_path/'ret',oa_records=data,download=True)[0]
    assert not calls
    assert item['automatic_download_enabled'] is False
    assert item['download_status'].startswith('blocked')


def test_xlsx_formula_is_literal_not_formula(tmp_path):
    from openpyxl import load_workbook
    metadata={'article_id':'study-1','title':'=HYPERLINK("http://malicious.invalid","Click")',
              'authors':'+SUM(1,2)','reading_level':'not_read','query_url':'@SUM(1,2)'}
    status=synthia.export([metadata],tmp_path/'out')
    assert status['xlsx_status']=='created'
    workbook=load_workbook(tmp_path/'out'/'database_literatur.xlsx',data_only=False)
    cell=workbook['Database Literatur']['D2']
    assert cell.data_type=='s' and cell.value==metadata['title']
    from zipfile import ZipFile
    from xml.etree import ElementTree as ET
    with ZipFile(tmp_path/'out'/'database_literatur.xlsx') as z:
        root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    raw_cell=root.find('.//x:c[@r="D2"]',ns)
    assert raw_cell.get('t') in ('s','inlineStr','str')
    assert raw_cell.find('x:f',ns) is None
    assert workbook['Database Literatur']['B2'].data_type=='s'


def test_synthia_preserves_conservative_gap(tmp_path):
    result=synthia.export([{'article_id':'study-1','reading_level':'not_read'}],tmp_path/'syn',xlsx=False)
    report=(tmp_path/'syn'/'sintesis_sementara.md').read_text()
    assert 'Belum cukup bukti' in report
    assert 'Belum dinilai' in result['rows'][0]['Temuan']


def test_synthia_synthetic_template_keeps_existing_content(tmp_path):
    from openpyxl import Workbook,load_workbook
    wb=Workbook();main=wb.active;main.title='Database Literatur'
    for c,h in enumerate(synthia.HEADERS,1):main.cell(2,c,h)
    existing=['Existing item']*20
    existing[0]=1;existing[3]='Existing Paper Title'
    for c,v in enumerate(existing,1):main.cell(3,c,v)
    memo=wb.create_sheet('Penjelasan Kolom');memo.append(['Catatan','Template sintetis'])
    template=tmp_path/'template_mock.xlsx';wb.save(template)
    candidate={'article_id':'art-2','title':'=HYPERLINK("http://malicious.invalid","X")',
               'authors':'B. Invented','reading_level':'not_read'}
    res=synthia.export([candidate],tmp_path/'syn',template_xlsx=template)
    assert res['xlsx_status']=='created'
    new=load_workbook(tmp_path/'syn'/'database_literatur.xlsx',data_only=False)
    assert new['Penjelasan Kolom']['B1'].value=='Template sintetis'
    data=new['Database Literatur']
    assert data['D3'].value=='Existing Paper Title'
    assert data['D4'].data_type=='s'
    assert data['D4'].value.startswith('=HYPERLINK')
    assert 'Audit F2' in new.sheetnames
