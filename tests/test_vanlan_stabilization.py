from pathlib import Path
import json
import fitz
import pytest
from reportlab.pdfgen import canvas
from epistarium import vanlan


def pdf_fixture(path, lines, footer=None, doi=None):
    c=canvas.Canvas(str(path),pagesize=(595,842))
    for i, txt in enumerate(lines):
        c.drawString(40,710,txt)
        if doi and i==0:
            c.drawString(40,680,'https://doi.org/'+doi)
        if footer:
            c.drawString(295,22,str(footer[i]))
        c.showPage()
    c.save()


def claim(text='Valid evidence phrase is present here.',cid='K1',kind='kutipan_langsung',name='src.pdf'):
    c={'id':cid,'text':text,'jenis':kind,'source_pdf':name}
    if kind=='kutipan_langsung': c['kutipan_asli']=text
    else: c['evidence_anchor']='Valid evidence phrase is present here.'
    return c


def test_numeric_year_in_footer_is_not_page_number(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.'],footer=[2026])
    r=vanlan.audit([claim()],tmp_path,tmp_path/'out')[0]
    assert r['printed_page'] is None
    assert r['literal_match_status']=='cocok'


def test_isolated_footer_sequence_is_confirmed(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.','Another page of evidence.'],footer=[79,80])
    r=vanlan.audit([claim()],tmp_path,tmp_path/'out')[0]
    assert r['printed_page']=='79'


def test_pdf_page_labels_not_blindly_misused(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.','Second page content.'],footer=[1,2])
    doc=fitz.open(tmp_path/'src.pdf')
    doc.set_page_labels([{'startpage':0,'prefix':'','style':'D','firstpagenum':100418}])
    doc.save(tmp_path/'labelled.pdf')
    doc.close()
    (tmp_path/'src.pdf').unlink()
    (tmp_path/'labelled.pdf').rename(tmp_path/'src.pdf')
    r=vanlan.audit([claim()],tmp_path,tmp_path/'out')[0]
    assert r['printed_page']=='1'
    assert r['pdf_page_label']=='100418'


def test_unique_doi_discovery_without_filename(tmp_path):
    doi='10.5555/vanlan.unique'
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.'],doi=doi)
    c=claim();c['source_pdf']='';c['source_doi']=doi
    r=vanlan.audit([c],tmp_path,tmp_path/'out')[0]
    assert r['source_pdf']=='src.pdf'
    assert r['source_match_status']=='dipetakan'


def test_doi_collision_blocks_selection(tmp_path):
    doi='10.5555/vanlan.unique'
    pdf_fixture(tmp_path/'a.pdf',['Valid evidence phrase is present here.'],doi=doi)
    pdf_fixture(tmp_path/'b.pdf',['Valid evidence phrase is present here.'],doi=doi)
    c=claim();c['source_pdf']='';c['source_doi']=doi
    r=vanlan.audit([c],tmp_path,tmp_path/'out')[0]
    assert r['source_match_status']=='belum dipetakan'
    assert len(r['source_candidates'])==2
    assert not r['highlight']


def test_wrong_doi_blocks_wrong_pdf(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.'],doi='10.5555/correct')
    c=claim();c['source_doi']='10.5555/wrong'
    r=vanlan.audit([c],tmp_path,tmp_path/'out')[0]
    assert r['source_match_status']=='belum dipetakan'
    assert not r['highlight']


def test_multi_anchor_unique_and_duplicate_highlight_dedup(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.','Another unique supporting sentence on second page.'],footer=[1,2])
    c=claim(kind='parafrasa');c['evidence_anchors']=['Valid evidence phrase is present here.','Another unique supporting sentence on second page.']
    c2=claim(cid='K2',kind='parafrasa')
    result=vanlan.audit([c,c2],tmp_path,tmp_path/'out')
    assert len(result[0]['evidence_locations'])==2
    assert result[1]['highlight']
    doc=fitz.open(tmp_path/'out'/'src_annotated.pdf')
    assert sum(len(list(page.annots() or [])) for page in doc)==2
    doc.close()


def test_same_phrase_on_multiple_pages_not_highlighted(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.','Valid evidence phrase is present here.'])
    r=vanlan.audit([claim()],tmp_path,tmp_path/'out')[0]
    assert not r['highlight']
    assert r['literal_match_status']=='ambigu atau koordinat tidak valid'


def test_review_does_not_contaminate_machine_evidence(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.'])
    c=claim(kind='parafrasa')
    rev={'K1': {'status':'didukung sebagian','reason':'Bagian kesimpulan terlalu luas','reviewer':'Penilai manusia'}}
    r=vanlan.audit([c],tmp_path,tmp_path/'out',reviews=rev)[0]
    assert r['semantic_support_status']=='didukung sebagian'
    assert r['literal_match_status']=='cocok'
    assert r['cakupan_keputusan'].startswith('penilaian manusia')


def test_bad_claims_schema_is_rejected(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.'])
    for claims in [dict(),[{},{}],[{'id':'dup','text':'A'}, {'id':'dup','text':'B'}]]:
        with pytest.raises(ValueError):
            vanlan.audit(claims,tmp_path,tmp_path/'out')


def test_path_traversal_and_input_source_conflict(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.'])
    c=claim(name='../src.pdf')
    assert vanlan.audit([c],tmp_path,tmp_path/'out')[0]['source_match_status']=='belum dipetakan'


def test_no_review_can_assert_semantic_support(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.'])
    r=vanlan.audit([claim()],tmp_path,tmp_path/'out')[0]
    assert r['status']=='belum dapat diverifikasi'
    assert r['literal_match_status']=='cocok'
    assert r['semantic_support_status']=='belum dinilai'


def test_auto_doi_discovery_ignores_annotated_copies(tmp_path):
    doi='10.5555/vanlan.duplicated.file'
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.'],doi=doi)
    (tmp_path/'src_annotated.pdf').write_bytes((tmp_path/'src.pdf').read_bytes())
    c=claim();c['source_doi']=doi;c['source_pdf']=''
    r=vanlan.audit([c],tmp_path,tmp_path/'out')[0]
    assert r['source_match_status']=='dipetakan'
    assert r['source_pdf']=='src.pdf'


def test_annotated_file_integrity_is_recorded(tmp_path):
    pdf_fixture(tmp_path/'src.pdf',['Valid evidence phrase is present here.'])
    vanlan.audit([claim()],tmp_path,tmp_path/'out')
    record=json.loads((tmp_path/'out'/'audit.json').read_text())
    assert record['annotation_integrity'][0]['text_preserved']
    assert record['annotation_integrity'][0]['status'].startswith('lulus')
