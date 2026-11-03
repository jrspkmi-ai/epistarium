"""Synthetic only: no paywalled publisher PDFs or personal interview files."""
from pathlib import Path
import csv
import json
import fitz
import pytest
from epistarium import retho, domares, synthia

DOI='10.1234/example.f2.2026'

def make_pdf(path, doi=DOI, has_text=True):
    d=fitz.open()
    pg=d.new_page()
    if has_text:
        pg.insert_text((60,70), 'Synthetic Research on Digital Communication',fontsize=13)
        pg.insert_text((60,95),'DOI: '+doi,fontsize=10)
        lines=[
         'The research problem is how AI-generated content influences trust.',
         'The purpose of this study is to describe communication practices.',
         'The theoretical framework involves social communication theory.',
         'The research question asks how users respond to synthetic news.',
         'The study used a qualitative case study research design.',
         'Data collection used semi-structured interviews with participants.',
         'Purposive sampling recruited twenty participants for this project.',
         'The questionnaire instrument was checked before collection.',
         'Thematic analysis and coding procedure were used in this study.',
         'Results suggest variation in how participants interpret sources.',
         'Limitations include a convenience sample and limited generalizability.',
         'Future research should compare multiple national settings.',
        ]
        for i,line in enumerate(lines):pg.insert_text((60,125+i*20),line,fontsize=9)
        pg.insert_text((300,805),'7',fontsize=9)
    else:
        pg.draw_rect(fitz.Rect(70,100,350,250),color=(.3,.3,.3),fill=(.3,.3,.3))
    d.save(path);d.close(); return path


def candidate(doi=DOI,abstract=None):
    return {'article_id':'art1','doi':doi,'title':'Synthetic Research on Digital Communication',
       'authors':'A. Example','year':2026,'type':'journal-article','available_level':'metadata+abstract_metadata' if abstract else 'metadata',
       'abstract':abstract,'query_url':'https://api.crossref.org/works?x=1'}


def test_retho_verified_pdf(tmp_path):
    p=make_pdf(tmp_path/'paper.pdf');o=retho.build([candidate()],tmp_path/'output',{DOI:{'pdf_path':str(p),'version':'publishedVersion','rights_basis':'user_supplied_private'}})
    assert o[0]['status']=='fulltext_local'
    assert o[0]['document_version']=='published'
    assert o[0]['fulltext_read'] is False
    assert o[0]['source_identity_status']=='doi_matched'
    assert o[0]['pdf_sha256']
    assert o[0]['rights_for_redistribution']=='not_established'

def test_retho_detects_conflicting_doi(tmp_path):
    p=make_pdf(tmp_path/'wrong.pdf','10.5678/different')
    row=retho.build([candidate()],tmp_path/'out',{DOI:{'pdf_path':str(p),'version':'acceptedVersion'}})[0]
    assert row['status']=='identity_conflict'
    assert row['fulltext_available'] is False

def test_retho_abstract_is_not_fulltext(tmp_path):
    row=retho.build([candidate(abstract='Results are promising.')],tmp_path/'out')[0]
    assert row['status']=='abstract_only' and not row['fulltext_available']

def test_retho_metadata_only_not_fulltext(tmp_path):
    row=retho.build([candidate()],tmp_path/'out')[0]
    assert row['status']=='metadata_only' and row['document_version']=='unknown'

def test_retho_missing_file(tmp_path):
    row=retho.build([candidate()],tmp_path/'out',{DOI:{'pdf_path':str(tmp_path/'nonexistent.pdf')}})[0]
    assert row['status']=='pdf_invalid_or_missing' and not row['fulltext_available']

def test_retho_oa_metadata_does_not_grant_licence(tmp_path):
    rec={DOI:{'oa_locations':[{'url_for_pdf':'https://public.example.org/a.pdf','version':'submittedVersion','license':'cc-by-4.0'}]}}
    row=retho.build([candidate()],tmp_path/'out',oa_records=rec,download=True)[0]
    assert row['status']=='metadata_only' and row['download_status']=='blocked_rights_not_confirmed'
    assert row['oa_candidates'][0]['version']=='preprint'

def test_retho_invalid_https_internal():
    with pytest.raises(ValueError):retho._validate_remote_url('https://127.0.0.1/private.pdf')
    with pytest.raises(ValueError):retho._validate_remote_url('http://example.org/public.pdf')

def test_retho_scanned_pdf_flag(tmp_path):
    p=make_pdf(tmp_path/'scan.pdf',has_text=False)
    row=retho.build([candidate()],tmp_path/'out',{DOI:{'pdf_path':str(p),'version':'preprint'}})[0]
    assert row['status']=='pdf_needs_ocr' and row['document_version']=='preprint'

def test_domares_fulltext_and_page_provenance(tmp_path):
    p=make_pdf(tmp_path/'paper.pdf')
    row=retho.build([candidate()],tmp_path/'ret',{DOI:{'pdf_path':str(p),'version':'published'}})[0]
    out=domares.analyze([row],tmp_path/'dom')[0]
    assert out['reading_level']=='machine_fulltext_extracted'
    assert out['reported_by_author']['hasil']
    assert out['reported_by_author']['hasil'][0]['pdf_page']==1
    assert out['reported_by_author']['hasil'][0]['verification_status'].startswith('kandidat')
    assert out['requires_human_review']
    assert out['ai_audit_observations']

def test_domares_will_not_populate_from_abstract(tmp_path):
    row=retho.build([candidate(abstract='Results from 200 participants')],tmp_path/'ret')[0]
    out=domares.analyze([row],tmp_path/'dom')[0]
    assert out['reading_level']=='not_read'
    assert all(not v for v in out['reported_by_author'].values())

def test_domares_conflict_not_read(tmp_path):
    p=make_pdf(tmp_path/'wrong.pdf','10.9999/wrong')
    row=retho.build([candidate()],tmp_path/'ret',{DOI:{'pdf_path':str(p)}})[0]
    out=domares.analyze([row],tmp_path/'dom')[0]
    assert out['reading_level']=='not_read' and not out['reported_by_author']['hasil']

def test_domares_scanned_pdf_does_not_infer(tmp_path):
    p=make_pdf(tmp_path/'scan.pdf',has_text=False)
    row=retho.build([candidate()],tmp_path/'ret',{DOI:{'pdf_path':str(p)}})[0]
    out=domares.analyze([row],tmp_path/'dom')[0]
    assert out['reading_level']=='pdf_without_sufficient_machine_text'
    assert all(not v for v in out['reported_by_author'].values())

def test_synthia_matrix_headers_and_audit(tmp_path):
    p=make_pdf(tmp_path/'article.pdf')
    row=retho.build([candidate()],tmp_path/'ret',{DOI:{'pdf_path':str(p)}})[0]
    parsed=domares.analyze([row],tmp_path/'dom')
    result=synthia.export(parsed,tmp_path/'syn',xlsx=False)
    assert len(result['rows'])==1 and len(result['rows'][0])==20
    assert result['audit'] and result['audit'][0]['pdf_page']==1
    with (tmp_path/'syn'/'database_literatur.csv').open(encoding='utf-8-sig') as f:
        rd=csv.reader(f); assert next(rd)==synthia.HEADERS
    assert 'Kandidat teks PDF hlm.' in result['rows'][0]['Temuan']
    assert 'Belum diverifikasi' in result['rows'][0]['Jumlah']

def test_synthia_abstract_does_not_fake_findings(tmp_path):
    row=retho.build([candidate(abstract='An effective method was used.')],tmp_path/'ret')[0]
    parsed=domares.analyze([row],tmp_path/'dom')
    result=synthia.export(parsed,tmp_path/'syn',xlsx=False)
    assert 'Belum dinilai' in result['rows'][0]['Temuan']
    assert 'Belum cukup bukti' in (tmp_path/'syn'/'sintesis_sementara.md').read_text(encoding='utf8')

def test_synthia_csv_formula_injection_protection(tmp_path):
    bad={'article_id':'a','title':'=HYPERLINK("http://evil")','year':2025,'reading_level':'not_read'}
    synthia.export([bad],tmp_path/'syn',xlsx=False)
    with (tmp_path/'syn'/'database_literatur.csv').open(encoding='utf-8-sig') as f:
        rd=list(csv.DictReader(f))
    assert rd[0]['Judul'].startswith("'=")

def test_synthia_no_false_gap_even_without_fulltext(tmp_path):
    synthia.export([],tmp_path/'syn',xlsx=False)
    text=(tmp_path/'syn'/'sintesis_sementara.md').read_text(encoding='utf8')
    assert 'Belum cukup bukti' in text and 'bukan bukti' in text
