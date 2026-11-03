"""Regression and adversarial tests after ORIGO/Quilo/Huxley stabilization.
Fixtures are wholly synthetic; none prove semantic accuracy on real research.
"""
import json
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import pytest
from docx import Document
from docx.oxml import OxmlElement
from epistarium import origo, ideon, quilo, huxley
from epistarium.common import sha256


def docx(tmp_path,texts,refs=None,split=False):
    p=tmp_path/'input.docx'; d=Document()
    for t in texts:
        if isinstance(t,(list,tuple)):
            x=d.add_paragraph()
            for e in t:x.add_run(e)
        else:d.add_paragraph(t)
    if refs is not None:
        d.add_paragraph('Daftar Pustaka')
        for x in refs:d.add_paragraph(x)
    d.save(p);return p


def test_origo_minimal_quick_map_produces_docx_two_sections(tmp_path):
    r=origo.export({'ide_awal':'AI dalam proses diskusi akademik'},tmp_path)
    assert r['docx_status']=='CREATED_AND_REOPENED'
    assert len(r['titles'])==3 and len({x['fokus'] for x in r['titles']})==3
    p=Document(r['docx_path'])
    assert [x.text for x in p.paragraphs if x.style.name=='Heading 2']==origo.NODE_NAMES
    assert [x['id'] for x in r['questions']]==[f'Q{i:02}' for i in range(1,22)]
    assert all(x['answer']=='Belum dielaborasi.' for x in r['questions'])
    assert len(list(tmp_path.glob('*.docx')))==1


def test_origo_source_not_fabricated():
    r=origo.build({'ide_awal':'komunikasi krisis makanan dan minuman'})
    assert r['literature_status']=='NOT_RUN' and 'belum diperiksa' in r['nodes']['realitas_fenomena']
    assert 'belum' in r['nodes']['potensi_kebaruan'].casefold()


def test_origo_preserves_theory_paradigm_rq_method():
    spec={'ide_awal':'komunikasi krisis restoran', 'teori_pilihan':'SCCT (Coombs)',
       'paradigma':'post-positivisme','metode_pilihan':'mixed methods, analisis wacana dan wawancara',
       'pertanyaan_penelitian':'Bagaimana eskalasi percakapan terjadi?'}
    r=origo.build(spec)
    assert all(x in r['nodes']['landasan_teori'] for x in ('SCCT','post-positivisme'))
    assert 'mixed methods' in r['nodes']['arah_metodologi']
    assert 'Bagaimana eskalasi' in r['nodes']['fokus_penelitian']
    assert r['teori_pengguna']==spec['teori_pilihan']


def test_origo_disallows_data_access_conflict_as_unqualified_method():
    r=origo.build({'ide_awal':'percakapan digital', 'metode_pilihan':'analisis isi korpus',
       'akses_data':{'korpus':'tidak tersedia','informan':'tersedia'}})
    assert any(x['status']=='KONFLIK' for x in r['checks'])
    assert 'KONFLIK' in r['nodes']['arah_metodologi']
    assert r['preferred_title'] is None


def test_origo_missing_corpus_prefers_available_interviews():
    r=origo.build({'ide_awal':'komunikasi krisis',
     'akses_data':{'korpus':'tidak tersedia','informan':'tersedia'}})
    assert r['preferred_title']=='K2'
    assert r['titles'][0]['akses']=='tidak tersedia'


def test_origo_missing_corpus_still_unverified_not_available():
    r=origo.build({'ide_awal':'komunikasi krisis',
     'akses_data':{'korpus':'belum tersedia','informan':'belum dikonfirmasi'}})
    assert r['titles'][0]['akses']!='tersedia'


def test_origo_elaborate_21_and_docx(tmp_path):
    r=origo.export({'ide_awal':'komunikasi krisis', 'mode':'ELABORATE_21', 'paradigma':'post-positivisme'},tmp_path)
    assert len(r['questions'])==21 and all(q['status']=='DRAF_PERLU_REVIEW' for q in r['questions'])
    assert all(q['answer']!='Belum dielaborasi.' for q in r['questions'])
    assert all('Belum dapat disimpulkan' in r['questions'][i-1]['answer'] for i in (6,7,8,13))
    assert r['docx_status']=='CREATED_AND_REOPENED'


def test_origo_blueprint_does_not_pretend_tools_executed():
    r=origo.build({'ide_awal':'penelitian digital','mode':'BLUEPRINT'})
    assert r['blueprint']['status']=='DRAF_TANPA_EKSEKUSI' and not r['blueprint']['tools_called']


def test_origo_revision_updates_only_explicit_node(tmp_path):
    prior=origo.build({'ide_awal':'komunikasi krisis','teori_pilihan':'Teori A', 'fenomena':'Pernyataan fenomena asli.'})
    spec={'ide_awal':'komunikasi krisis','mode':'REVISION', 'revision_id':'REV001',
          'perubahan':{'landasan_teori':'Teori B atas permintaan pembimbing.'}}
    r=origo.build(spec,previous=prior)
    assert r['nodes']['realitas_fenomena']==prior['nodes']['realitas_fenomena']
    assert r['nodes']['landasan_teori']=='Teori B atas permintaan pembimbing.'
    assert r['changed_nodes']==['landasan_teori']
    r2=origo.export(spec,tmp_path,previous=prior)
    assert r2['docx_status']=='CREATED_AND_REOPENED'


def test_origo_revision_needs_previous():
    with pytest.raises(ValueError):origo.build({'ide_awal':'a topik','mode':'REVISION'})


def test_origo_invalid_input():
    for spec in ({}, {'ide_awal':'x'}, {'ide_awal':'good idea','mode':'FANTASY'},
                 {'ide_awal':'good idea','judul_count':0}, {'ide_awal':'good idea','akses_data':'bad'}):
        with pytest.raises(ValueError):origo.build(spec)


def test_origo_legacy_entry_remains_available():
    r=ideon.design({'ide':'komunikasi krisis','teori':'SCCT','akses_data':{'korpus':'tidak tersedia','informan':'tersedia'}})
    assert r['pilihan_sementara']=='K2' and 'SCCT' in r['rmc_2_0']['Teori']


def test_quilo_negative_word_removal_is_blocked():
    v=quilo.validate_revision('Organisasi tidak mengakui kesalahan.','Organisasi mengakui kesalahan.')
    assert not v['safe_to_propose'] and v['protected_tokens_unchanged'] is True
    assert v['semantic_validity']=='NOT_ASSESSED'


@pytest.mark.parametrize('a,b',[('Organisasi mungkin bertanggung jawab.','Organisasi pasti bertanggung jawab.'),
 ('Data meningkat.','Data menurun.'),('Semua informan hadir.','Sebagian informan hadir.'),
 ('Peneliti menjelaskan hasil.','Manajer menjelaskan hasil.')])
def test_quilo_unreviewed_changes_not_safe(a,b):
    v=quilo.validate_revision(a,b)
    assert v['safe_to_propose'] is False and v['semantic_validity']=='NOT_ASSESSED'


def test_quilo_filler_only_candidate_not_semantic_pass():
    v=quilo.validate_revision('Perlu diketahui bahwa 20 responden hadir.','20 responden hadir.')
    assert v['safe_to_propose'] and v['semantic_validity']=='NOT_ASSESSED'


def test_huxley_wrong_second_author(tmp_path):
    p=docx(tmp_path,['Smith and Lee (2023) menjelaskan.'],['Smith, J., & Park, P. (2023). Synthetic.'])
    r=huxley.audit(p,tmp_path/'out')
    assert r['citations'][0]['status']=='UNMATCHED_CITATION'


def test_huxley_multiple_years(tmp_path):
    p=docx(tmp_path,['Smith (2023, 2024) menjelaskan.'],['Smith, J. (2023). A.','Smith, J. (2024). B.'])
    r=huxley.audit(p,tmp_path/'out')
    assert len(r['citations'])==2 and all(c['status']=='MATCHED' for c in r['citations'])


def test_huxley_duplicate_occurrences_highlighted_twice(tmp_path):
    p=docx(tmp_path,['(Ramos, 2025) dan (Ramos, 2025) tertulis.'],['Smith, J. (2023). Synthetic.'])
    r=huxley.audit(p,tmp_path/'out',annotate=True)
    d=Document(r['annotation']['file'])
    high=''.join(x.text for x in d.paragraphs[0].runs if x.font.highlight_color is not None)
    assert high.count('(Ramos, 2025)')==2 and len(r['annotation']['highlighted_citation_ids'])==2


def test_huxley_split_runs_and_native_comments_structural(tmp_path):
    p=docx(tmp_path,[['(Ramos, ','2025) belum ada.']],['Smith, J. (2023). Synthetic.'])
    before=sha256(p);r=huxley.audit(p,tmp_path/'out',annotate=True)
    assert sha256(p)==before
    assert r['annotation']['native_comments']=='CREATED_AND_ANCHORED'
    assert r['annotation']['highlighted_citation_ids'] and r['annotation']['highlighted_reference_ids']
    target=r['annotation']['file']
    d=Document(target)
    assert d.paragraphs[0].text=='(Ramos, 2025) belum ada.'
    with ZipFile(target) as z:
        assert 'word/comments.xml' in z.namelist()
        comments=z.read('word/comments.xml')
        assert comments.count(b'w:comment w:id')>=2
        xml=z.read('word/document.xml')
        assert b'commentRangeStart' in xml and b'commentRangeEnd' in xml and b'commentReference' in xml
        assert b'comments' in z.read('word/_rels/document.xml.rels')


def test_huxley_uncited_ref_note_is_precise(tmp_path):
    p=docx(tmp_path,['Tanpa sitasi.'],['Ramos, J. (2025). Synthetic.'])
    r=huxley.audit(p,tmp_path/'out',annotate=True)
    assert r['references'][0]['status']=='UNCITED_REFERENCE'
    assert r['annotation']['highlighted_reference_ids']
    assert any('Tidak ditemukan kutipan' in a['message'] for a in r['annotation']['comment_anchors'])


def test_huxley_no_bibliography_heading_manual_not_false_missing(tmp_path):
    p=docx(tmp_path,['Smith (2023) menjelaskan.'],refs=None)
    r=huxley.audit(p,tmp_path/'out')
    assert r['citations'][0]['status']=='MANUAL_REVIEW'


def test_huxley_dynamic_fields_file_byte_preserved(tmp_path):
    p=docx(tmp_path,['Ramos (2025) belum dikutip.'],['Smith, J. (2023). Article.'])
    d=Document(p);run=d.paragraphs[0].add_run();e=OxmlElement('w:fldChar');run._r.append(e);d.save(p)
    r=huxley.audit(p,tmp_path/'out',annotate=True)
    assert sha256(p)==sha256(r['annotation']['file'])
    assert r['annotation']['native_comments']=='SKIPPED_DYNAMIC_FIELDS'


def test_origo_user_supplied_answer_is_preserved_but_not_certified():
    r=origo.build({'ide_awal':'komunikasi krisis','mode':'ELABORATE_21',
        'jawaban_21':{'Q12':'Teori pilihan pengguna dipakai untuk menguji unit analisis.'}})
    assert r['questions'][11]['answer']=='Teori pilihan pengguna dipakai untuk menguji unit analisis.'
    assert r['questions'][11]['status']=='INPUT_PENGGUNA_BELUM_AUDIT'


def test_origo_revision_inherits_theory_access_metadata():
    before=origo.build({'ide_awal':'komunikasi krisis','teori_pilihan':'SMCC',
        'akses_data':{'korpus':'tersedia','informan':'terbatas'}})
    after=origo.build({'ide_awal':'komunikasi krisis','mode':'REVISION',
        'perubahan':{'potensi_kebaruan':'Hipotesis kontribusi baru menunggu bukti.'}},previous=before)
    assert after['teori_pengguna']=='SMCC' and after['akses_data']==before['akses_data']
    assert after['nodes']['landasan_teori']==before['nodes']['landasan_teori']


def test_origo_docx_failure_is_not_reported_as_success(tmp_path,monkeypatch):
    def fail_doc(_): raise RuntimeError('DOCX engine unavailable')
    monkeypatch.setattr(origo,'_doc',fail_doc)
    r=origo.export({'ide_awal':'komunikasi digital'},tmp_path)
    assert r['docx_status']=='DOCX_NOT_AVAILABLE/BLOCKED'
    assert not list(tmp_path.glob('*.docx'))


def test_huxley_unparsed_references_require_manual_review(tmp_path):
    p=docx(tmp_path,['(Smith, 2023).'],['Smith, John, 2023. Reference that parser cannot safely recognize.'])
    r=huxley.audit(p,tmp_path/'out')
    assert r['citations'][0]['status']=='MANUAL_REVIEW'


def test_huxley_page_number_field_in_footer_does_not_block_body_annotation(tmp_path):
    p=docx(tmp_path,['(Ramos, 2025).'],['Smith, J. (2023). Article.'])
    d=Document(p);run=d.sections[0].footer.paragraphs[0].add_run()
    node=OxmlElement('w:fldChar');run._r.append(node)
    d.save(p)
    r=huxley.audit(p,tmp_path/'out',annotate=True)
    assert not r['citation_fields_detected']
    assert r['annotation']['highlighted_citation_ids']
