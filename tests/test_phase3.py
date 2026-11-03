"""F3 local controlled fixtures: synthetic text and DOCX; no external articles."""
from __future__ import annotations
from pathlib import Path
import copy
import json
import pytest
from docx import Document
from docx.oxml import OxmlElement
from epistarium import ideon, quilo, huxley
from epistarium.common import sha256


def docx_file(tmp_path, paragraphs, references, *, table=False, dynamic=False, split_run=False):
    p=tmp_path/'synthetic.docx'
    d=Document()
    for x in paragraphs:
        if split_run:
            a=x.find('(')
            if a>0:
                d.add_paragraph(x[:a]).add_run(x[a:])  # rest of string present in one paragraph
            else:d.add_paragraph(x)
        else:d.add_paragraph(x)
    if table:
        t=d.add_table(rows=1,cols=1)
        t.cell(0,0).text='Dokumen tambahan (Ramos, 2023).'
    d.add_paragraph('Daftar Pustaka')
    for r in references:d.add_paragraph(r)
    if dynamic:
        p0=d.paragraphs[0]
        run=p0.add_run()
        f=OxmlElement('w:fldChar');run._r.append(f)
    d.save(p);return p


def ideon_input():return {'ide':'penggunaan AI dalam komunikasi akademik','disiplin':'Ilmu Komunikasi'}

def test_ideon_minimal_has_three_distinct_titles():
    r=ideon.design(ideon_input());assert len(r['kandidat_judul'])==3
    assert len(set(x['judul'] for x in r['kandidat_judul']))==3
    assert len(set(x['metode'] for x in r['kandidat_judul']))==3

def test_ideon_has_21_questions_and_exact_canvas():
    r=ideon.design(ideon_input());assert len(r['jawaban_21'])==21
    assert list(r['rmc_2_0'])==ideon.CANVAS
    assert [x['nomor'] for x in r['jawaban_21']]==list(range(1,22))

def test_ideon_gap_stays_tentative():
    r=ideon.design(ideon_input());assert r['gap_status']=='sementara'
    assert any('State of the art' in x or 'novelty' in x for x in r['peringatan'])

def test_ideon_unverified_evidence_not_promoted():
    r=ideon.design({'ide':'kasus makanan','bukti':[{'claim':'angka 80%', 'status':'terverifikasi'}]})
    assert r['bukti'][0]['status']=='belum dapat diverifikasi'

def test_ideon_valid_but_doesnt_pretend_overall_verified():
    r=ideon.design({'ide':'riset','bukti':[{'status':'terverifikasi','sumber':'rekaman resmi','reviewer':'R1','alasan_verifikasi':'Diperiksa ulang'}]})
    assert r['bukti'][0]['status']=='terverifikasi'
    assert all(q['status'] != 'terverifikasi' for q in r['jawaban_21'])

def test_ideon_missing_topic():
    with pytest.raises(ValueError):ideon.design({'bukti':[]})

def test_ideon_invalid_status():
    with pytest.raises(ValueError):ideon.design({'ide':'x','bukti':[{'status':'kuat'}]})

def test_ideon_export(tmp_path):
    r=ideon.export(ideon_input(),tmp_path)
    assert (tmp_path/'rancangan_rmc.md').exists()
    assert len(json.loads((tmp_path/'ideon_rmc.json').read_text())['jawaban_21'])==21


def test_quilo_detects_slop():
    r=quilo.lint('Perlu diketahui bahwa ini sangat penting.');assert len(r)>=2

def test_quilo_removes_only_safe_phrase():
    s='Perlu diketahui bahwa sampel 200 responden (Smith, 2023) dilaporkan.'
    r,e,val=quilo.suggested_revision(s)
    assert 'Perlu diketahui' not in r and val['safe_to_propose']
    assert '200 responden' in r and '(Smith, 2023)' in r

def test_quilo_changed_numeral_rejected():
    assert not quilo.validate_revision('Jumlah 20 orang','Jumlah 200 orang')['safe_to_propose']

def test_quilo_changed_quote_rejected():
    assert not quilo.validate_revision('Penulis menyatakan “risiko meningkat”.','Penulis menyatakan “risiko berkurang”.')['safe_to_propose']

def test_quilo_changed_doi_rejected():
    assert not quilo.validate_revision('DOI 10.1000/abc','DOI 10.1000/xyz')['safe_to_propose']

def test_quilo_changed_citation_rejected():
    assert not quilo.validate_revision('Data (Sari, 2021).','Data (Sari, 2022).')['safe_to_propose']

def test_quilo_audit_files(tmp_path):
    out=quilo.audit('Perlu diketahui bahwa angka 20 orang dilaporkan.',tmp_path)
    assert out['semantic_validity']=='NOT_ASSESSED'
    assert (tmp_path/'perubahan.diff').exists()

def test_huxley_single_parenthetical_matches(tmp_path):
    p=docx_file(tmp_path,['Hal ini dilaporkan (Smith, 2023).'],['Smith, J. (2023). Article A.'])
    r=huxley.audit(p,tmp_path/'out')
    assert r['citations'][0]['status']=='MATCHED'
    assert r['references'][0]['status']=='MATCHED'

def test_huxley_narrative_matches(tmp_path):
    p=docx_file(tmp_path,['Smith (2023) menjelaskan.'],['Smith, J. (2023). Article A.'])
    r=huxley.audit(p,tmp_path/'out'); assert r['citations'][0]['kind']=='narrative'
    assert r['citations'][0]['status']=='MATCHED'

def test_huxley_group_and_two_authors(tmp_path):
    p=docx_file(tmp_path,['Temuan (Smith & Lee, 2023; Ramos, 2022) relevan.'],[
        'Smith, J., & Lee, P. (2023). Article A.','Ramos, T. (2022). Article B.'])
    r=huxley.audit(p,tmp_path/'out')
    assert len(r['citations'])==2 and {x['status'] for x in r['citations']}=={'MATCHED'}

def test_huxley_et_al_matches_three_authors(tmp_path):
    p=docx_file(tmp_path,['(Brown et al., 2026a).'],['Brown, J., Lee, K., & Park, P. (2026a). Article A.'])
    r=huxley.audit(p,tmp_path/'out')
    assert r['citations'][0]['status']=='MATCHED'

def test_huxley_year_suffix_distinguishes(tmp_path):
    p=docx_file(tmp_path,['Smith (2026a) dan Smith (2026b).'],[
        'Smith, J. (2026a). A.','Smith, J. (2026b). B.'])
    r=huxley.audit(p,tmp_path/'out');assert [c['status'] for c in r['citations']]==['MATCHED','MATCHED']

def test_huxley_year_without_suffix_ambiguous(tmp_path):
    p=docx_file(tmp_path,['Smith (2026) menulis.'],[
        'Smith, J. (2026a). A.','Smith, J. (2026b). B.'])
    r=huxley.audit(p,tmp_path/'out');assert r['citations'][0]['status']=='AMBIGUOUS'
    assert all(x['status']=='MANUAL_REVIEW' for x in r['references'])

def test_huxley_ambiguous_duplicate_author_year(tmp_path):
    p=docx_file(tmp_path,['Smith (2026) menulis.'],[
        'Smith, J. (2026). A.','Smith, K. (2026). B.'])
    r=huxley.audit(p,tmp_path/'out');assert r['citations'][0]['status']=='AMBIGUOUS'

def test_huxley_unmatched_and_uncited(tmp_path):
    p=docx_file(tmp_path,['(Ramos, 2022) berbeda.'],['Smith, J. (2023). Article A.'])
    r=huxley.audit(p,tmp_path/'out')
    assert r['citations'][0]['status']=='UNMATCHED_CITATION'
    assert r['references'][0]['status']=='UNCITED_REFERENCE'

def test_huxley_missing_references_header(tmp_path):
    p=tmp_path/'x.docx'; d=Document();d.add_paragraph('Smith (2023) menulis.');d.save(p)
    r=huxley.audit(p,tmp_path/'out');assert not r['coverage']['reference_heading_found']
    assert r['citations'][0]['status']=='MANUAL_REVIEW'  # insufficient basis to claim missing

def test_huxley_unparsed_reference_flag(tmp_path):
    p=docx_file(tmp_path,['(Smith, 2023)'],['Sumber tanpa tahun.'])
    r=huxley.audit(p,tmp_path/'out');assert len(r['coverage']['unparsed_references'])==1

def test_huxley_table_citation(tmp_path):
    p=docx_file(tmp_path,['Penelitian pendukung'],['Ramos, T. (2023). A.'],table=True)
    r=huxley.audit(p,tmp_path/'out');assert r['citations'][0]['status']=='MATCHED'
    assert r['citations'][0]['location'].startswith('table:')

def test_huxley_annotates_exact_text_and_preserves_original(tmp_path):
    p=docx_file(tmp_path,['Tinjauan (Ramos, 2025) relevan.'],['Smith, J. (2023). A.'])
    before=sha256(p);r=huxley.audit(p,tmp_path/'out',annotate=True)
    assert sha256(p)==before
    out=Path(r['annotation']['file']);assert out.exists()
    d=Document(out)
    assert d.paragraphs[0].text=='Tinjauan (Ramos, 2025) relevan.'
    assert any(run.font.highlight_color is not None for run in d.paragraphs[0].runs)
    assert r['annotation']['native_comments']=='CREATED_AND_ANCHORED'  # upgraded native comment capability

def test_huxley_dynamic_field_byte_preserved(tmp_path):
    p=docx_file(tmp_path,['(Ramos, 2025).'],['Smith, J. (2023). A.'],dynamic=True)
    r=huxley.audit(p,tmp_path/'out',annotate=True)
    assert r['citation_fields_detected']
    assert r['annotation']['status'].startswith('SKIPPED_DYNAMIC')
    assert sha256(r['annotation']['file'])==sha256(p)

def test_huxley_offline_candidate_never_final(tmp_path):
    p=docx_file(tmp_path,['(Ramos, 2025).'],['Smith, J. (2023). A.'])
    fixture={'ramos|2025':[{'title':'Synthetic candidate','DOI':'10.0000/synthetic'}]}
    r=huxley.audit(p,tmp_path/'out',candidate_fixture=fixture)
    assert r['proposed_additions'][0]['status']=='DRAFT-PERLU-VERIFIKASI'
    assert len(r['references'])==1

def test_huxley_web_failure_explicit(tmp_path,monkeypatch):
    import requests
    def fail(*a,**kw):raise requests.ConnectionError('offline test')
    from epistarium.pathfinder_harvest import LimitedClient
    monkeypatch.setattr(LimitedClient,'get',fail)
    p=docx_file(tmp_path,['(Ramos, 2025).'],['Smith, J. (2023). A.'])
    r=huxley.audit(p,tmp_path/'out',online=True)
    assert r['metadata_search']['attempts'][0]['status']=='ACCESS_FAILED'
    assert r['citations'][0]['status']=='UNMATCHED_CITATION'

def test_huxley_ref_source_not_mutated_without_annotation(tmp_path):
    p=docx_file(tmp_path,['(Smith, 2023).'],['Smith, J. (2023). A.'])
    sha=sha256(p);r=huxley.audit(p,tmp_path/'out')
    assert sha256(p)==sha and r['annotation']['status']=='NOT_REQUESTED'

def test_huxley_non_docx_rejected(tmp_path):
    txt=tmp_path/'a.txt';txt.write_text('abc')
    with pytest.raises(ValueError):huxley.audit(txt,tmp_path/'out')

def test_huxley_organization_narrative(tmp_path):
    p=docx_file(tmp_path,['World Health Organization (2023) menyusun laporan.'],[
        'World Health Organization. (2023). Report title.'])
    r=huxley.audit(p,tmp_path/'out')
    assert len(r['citations'])==1
    assert r['citations'][0]['status']=='MATCHED'
    assert r['citations'][0]['kind']=='narrative_organization'

def test_huxley_nd_parenthetical(tmp_path):
    p=docx_file(tmp_path,['(Sari, n.d.) menjadi rujukan.'],['Sari, S. (n.d.). Document title.'])
    r=huxley.audit(p,tmp_path/'out')
    assert r['citations'][0]['status']=='MATCHED'

def test_huxley_highlight_exact_not_whole_paragraph(tmp_path):
    p=docx_file(tmp_path,['Awal paragraf (Ramos, 2025) dan akhir kalimat.'],['Smith, J. (2023). A.'])
    r=huxley.audit(p,tmp_path/'out',annotate=True)
    d=Document(r['annotation']['file'])
    highlighted=''.join(run.text for run in d.paragraphs[0].runs if run.font.highlight_color is not None)
    assert highlighted=='(Ramos, 2025)'

def test_huxley_multi_run_not_highlighted(tmp_path):
    p=tmp_path/'split.docx';d=Document();par=d.add_paragraph('Awal (Ramos, ');par.add_run('2025) akhir.')
    d.add_paragraph('Daftar Pustaka');d.add_paragraph('Smith, J. (2023). A.')
    d.save(p)
    r=huxley.audit(p,tmp_path/'out',annotate=True)
    assert r['annotation']['highlighted_citation_ids']==['C001']  # upgraded split-run support
    assert Document(r['annotation']['file']).paragraphs[0].text==Document(p).paragraphs[0].text

def test_huxley_group_highlight_only_unmatched_component(tmp_path):
    p=docx_file(tmp_path,['Temuan (Smith, 2023; Ramos, 2025) menguatkan diskusi.'],['Smith, J. (2023). A.'])
    r=huxley.audit(p,tmp_path/'out',annotate=True)
    d=Document(r['annotation']['file'])
    highlighted=''.join(run.text for run in d.paragraphs[0].runs if run.font.highlight_color is not None)
    assert highlighted=='Ramos, 2025'
    assert 'Smith, 2023' not in highlighted

def test_ideon_feasibility_access_is_discriminated():
    r=ideon.design({'ide':'komunikasi krisis','akses_data':{'korpus':'tersedia','informan':'tidak tersedia','organisasi':'terbatas'}})
    assert r['kandidat_judul'][0]['akses_data']=='tersedia'
    assert r['kandidat_judul'][1]['akses_data']=='tidak tersedia'
    assert r['kandidat_judul'][2]['akses_data']=='terbatas'
    assert len(r['kandidat_judul'][0]['pemeriksaan_kelayakan'])==6
