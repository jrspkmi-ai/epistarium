"""V0.2.2 new privacy-safe fixture tests, no user PDFs in source distribution."""
import json
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from openpyxl import Workbook, load_workbook
from epistarium import synthia, retho
from epistarium.gold_validation import parse_pdf_pages


def make_mock(tmp_path):
    b=Workbook(); main=b.active; main.title='Database Literatur'
    for c,h in enumerate(synthia.HEADERS,1):main.cell(2,c,h)
    old=['']*20
    old[0]=1;old[1]='Reviewer';old[2]=2025;old[3]='Article Already Reviewed';old[16]='Verified by human'
    old[19]='https://doi.org/10.5555/exists'
    for c,value in enumerate(old,1):main.cell(3,c,value)
    other=b.create_sheet('Penjelasan Kolom')
    other['A1']='KEEP_THIS'
    path=tmp_path/'original.xlsx'; b.save(path)
    return path


def candidate(title, doi, year=2025):
    return {'article_id':doi,'doi':doi,'title':title,'year':year,'authors':'Synthetic',
            'reading_level':'not_read'}


def test_real_style_existing_doi_never_duplicated(tmp_path):
    t=make_mock(tmp_path)
    x=synthia.export([candidate('Article Already Reviewed','10.5555/exists')],tmp_path/'out',template_xlsx=t)
    assert x['xlsx_status']=='created'
    wb=load_workbook(tmp_path/'out'/'database_literatur.xlsx',data_only=False)
    sheet=wb['Database Literatur']
    assert sheet['D3'].value=='Article Already Reviewed'
    assert sheet['Q3'].value=='Verified by human'
    assert sheet['D4'].value in ('',None)
    merge=json.loads((tmp_path/'out'/'template_merge_audit.json').read_text())
    assert merge['appended_count']==0 and len(merge['skipped_existing'])==1


def test_conflicting_doi_blocks_not_overwrites(tmp_path):
    t=make_mock(tmp_path)
    x=synthia.export([candidate('Article Already Reviewed','10.5555/different')],tmp_path/'out',template_xlsx=t)
    assert x['xlsx_status']=='created'
    merge=json.loads((tmp_path/'out'/'template_merge_audit.json').read_text())
    assert merge['appended_count']==0 and len(merge['conflicting_identity'])==1


def test_new_title_added_with_next_number_and_preserves_prior(tmp_path):
    t=make_mock(tmp_path)
    x=synthia.export([candidate('New Paper','10.5555/new')],tmp_path/'out',template_xlsx=t)
    assert x['xlsx_status']=='created'
    w=load_workbook(tmp_path/'out'/'database_literatur.xlsx',data_only=False)
    sh=w['Database Literatur']
    assert sh['A4'].value==2
    assert sh['D4'].value=='New Paper'
    assert w['Penjelasan Kolom']['A1'].value=='KEEP_THIS'


def test_retho_access_observation_never_grants_fulltext(tmp_path):
    doi='10.5555/test-abstract'
    obs={doi:{'access_state':'abstract_visible_restricted_fulltext',
          'source_url':'https://example.org/article/abs','observed_at':'2026-11-03',
          'observation_source':'publisher_webpage_review'}}
    rows=retho.build([{'doi':doi,'title':'Example','has_abstract':True}],tmp_path/'r',publisher_observations=obs,download=True)
    r=rows[0]
    assert r['status']=='abstract_only' and not r['fulltext_available'] and not r['fulltext_read']
    assert r['automatic_download_enabled'] is False
    assert not r['publisher_access_observation']['rights_proven']
    assert r['publisher_access_observation']['access_state']=='abstract_visible_restricted_fulltext'


def test_retho_url_full_segment_is_not_fulltext_proof(tmp_path):
    doi='10.5555/full-url'
    rows=retho.build([{'doi':doi,'title':'Example'}],tmp_path/'r',publisher_observations={doi:{
        'access_state':'fulltext_link_not_access_verified',
        'source_url':'https://example.org/doi/full/10.5555/full-url'}})
    assert rows[0]['status']=='metadata_only'
    assert not rows[0]['fulltext_available']


def test_gold_page_parser_ranges():
    assert parse_pdf_pages('Metode (PDF hlm. 2, 7–9; cek lagi)')=={2,7,8,9}
    assert parse_pdf_pages('Temuan (PDF hlm. 5-6, 9)')=={5,6,9}
    assert parse_pdf_pages('Tanpa penanda')==set()


def test_gold_validation_reports_page_overlap_not_semantic_pass(tmp_path):
    from epistarium.gold_validation import compare_gold
    wb=Workbook();s=wb.active;s.title='Database Literatur'
    for c,h in enumerate(synthia.HEADERS,1):s.cell(2,c,h)
    vals=['']*20; vals[0]=1; vals[3]='Example Article';vals[7]='Case study (PDF hlm. 2–3)';vals[19]='https://doi.org/10.5555/a'
    for c,value in enumerate(vals,1):s.cell(3,c,value)
    goldfile=tmp_path/'gold.xlsx'; wb.save(goldfile)
    reads=[{'doi':'10.5555/a','reported_by_author':{'desain':[{'pdf_page':3,'excerpt':'case study'}]},'reading_level':'machine_fulltext_extracted'}]
    result=compare_gold(reads,goldfile,tmp_path/'eval')
    assert result['status_counts']['PAGE_OVERLAP']==1
    assert result['semantic_accuracy']=='NOT MEASURED'
    assert result['fields_evaluated']==8
