"""v0.5.0 regressions from audit evidence; synthetic fixtures, no external calls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
from unittest.mock import patch
import pytest
from openpyxl import Workbook, load_workbook
from epistarium import jorhas, liora, retho, origo, synthia, quilo
from epistarium import pathfinder_ledger as ledger, pathfinder_harvest as harvest
from epistarium.common import validate_schema, sha256

ROOT=Path(__file__).resolve().parents[1]
FX=ROOT/'examples/f4_synthetic/pathfinder_cases.json'


@pytest.mark.parametrize('status',sorted(ledger.STATUS))
def test_every_source_assessment_remains_unreviewed(status):
    r=ledger.normalize_record({'status_verifikasi':status},1)
    assert r['status_verifikasi']=='belum dapat diverifikasi'
    assert r['source_claimed_status']==status


@pytest.mark.parametrize('value',['false','true',0,1,[],{}])
def test_synthetic_flag_must_be_boolean(value):
    with pytest.raises(ValueError):ledger.normalize_record({'synthetic':value},1)


@pytest.mark.parametrize('value',[True,float('nan'),float('inf'),'many'])
def test_invalid_numbers_keep_raw_text_instead_of_non_json_numbers(value):
    r=ledger.normalize_record({'nilai':value},1)
    assert r['nilai'] is None and r['nilai_raw'] is not None and r['nilai_parse_error']
    json.dumps(r,allow_nan=False)


def test_dedup_maps_alias_keeps_both_attempts_and_record_reference(tmp_path):
    fx=tmp_path/'fixture.json'
    fx.write_text(json.dumps({'sources':[{'source_id':'A','provider':'test','url':'https://example.org/a'},
      {'source_id':'B','provider':'test','url':'https://example.org/a'}],
      'records':[{'record_id':'R1','source_id':'B','jenis_data':'dataset','url':'https://example.org/a'}]}))
    r=jorhas.pathfind('uji provenance',tmp_path/'out',fixture=fx)
    rec=r['records'][0];source=next(s for s in r['sources'] if s['source_id']==rec['source_id'])
    assert rec['source_id']=='A' and 'B' in source['source_aliases']
    assert len(source['access_attempts'])==2


def test_fixture_sources_always_resolve_even_when_original_omits_ids(tmp_path):
    r=jorhas.pathfind('uji provenance',tmp_path/'out',fixture=FX)
    ids={s['source_id'] for s in r['sources']}
    assert all(rec['source_id'] in ids for rec in r['records'])
    for name in ('DATA_LEDGER','SOURCE_LEDGER'):
        payload=json.loads((tmp_path/'out'/f'{name}.json').read_text())
        validate_schema(payload,'pathfinder_data_ledger' if name=='DATA_LEDGER' else 'pathfinder_sources')


def test_duplicate_record_id_rejected(tmp_path):
    fx=tmp_path/'fx.json';fx.write_text(json.dumps({'records':[{'record_id':'A'},{'record_id':'A'}]}))
    with pytest.raises(ValueError,match='record_id'):jorhas.pathfind('uji duplikat',tmp_path/'out',fixture=fx)


def test_completed_outputs_cannot_be_reused_as_new_run(tmp_path):
    output=tmp_path/'out'
    jorhas.pathfind('uji run',output,fixture=FX)
    before=sha256(output/'RUN_MANIFEST.json')
    with pytest.raises(ValueError,match='Folder keluaran'):jorhas.pathfind('uji run kedua',output)
    assert sha256(output/'RUN_MANIFEST.json')==before


def test_docx_failure_blocks_stage_and_quilo(tmp_path,monkeypatch):
    monkeypatch.setattr(origo,'_doc',lambda _:(_ for _ in ()).throw(RuntimeError('forced failure')))
    r=jorhas.full_research('rancangan uji',tmp_path/'out')
    assert r['stage_statuses']['Ideon ORIGO']=='BLOCKED'
    assert r['stage_statuses']['Quilo']=='NOT_RUN'
    assert r['stage_results']['Ideon ORIGO']['deliverable_status']=='INCOMPLETE'
    assert r['deliverable_status']=='INCOMPLETE'


def test_xlsx_failure_cannot_be_success_in_full_research(tmp_path,monkeypatch):
    monkeypatch.chdir(ROOT)
    cfg=json.loads((ROOT/'examples/f4_synthetic/full_config.json').read_text());cfg['synthia_xlsx']=True
    monkeypatch.setattr(synthia,'_export_xlsx',lambda *a,**kw:(_ for _ in ()).throw(OSError('forced')))
    r=jorhas.full_research('riset uji',tmp_path/'out',config=cfg)
    assert r['stage_statuses']['Synthia']=='BLOCKED'
    assert r['stage_results']['Synthia']['errors']
    assert r['stage_results']['Ideon ORIGO']['execution_status']=='SUCCESS'


def test_distinct_no_doi_articles_keep_distinct_identity(tmp_path):
    fx=tmp_path/'meta.json';fx.write_text(json.dumps({'message':{'items':[
        {'title':['Study One'],'published':{'date-parts':[[2025]]}},
        {'title':['Study Two'],'published':{'date-parts':[[2025]]}}]}}))
    cfg={'liora_fixture':str(fx)}
    out=tmp_path/'out';jorhas.full_research('study',out,config=cfg)
    rows=json.loads((out/'EVIDENCE_CROSSWALK.json').read_text())['literature']
    assert len(rows)==2 and rows[0]['article_id']!=rows[1]['article_id']
    assert all(r['article_id']==r['retho_article_id'] for r in rows)


def test_article_ids_are_order_independent(tmp_path):
    records=[{'doi':'10.5555/x','title':'One'},{'title':'Two','year':2025}]
    one=retho.build(records,tmp_path/'one');two=retho.build(list(reversed(records)),tmp_path/'two')
    assert {r['title']:r['article_id'] for r in one}=={r['title']:r['article_id'] for r in two}


def test_no_empty_doi_library_fallback(tmp_path):
    r=retho.build([{'title':'Study without DOI'}],tmp_path/'out',library={'':{'pdf_path':'unrelated.pdf'}})[0]
    assert r['pdf_path'] is None


def test_origo_receives_ledger_provenance_without_claiming_verified_literature(tmp_path):
    cfg={'pathfinder_fixture':str(FX)}
    jorhas.full_research('rancangan uji',tmp_path/'out',config=cfg)
    result=json.loads((tmp_path/'out/ideon/ideon_origo.json').read_text())
    assert result['provenance_context']['data_record_ids']
    assert result['provenance_context']['human_review']=='PENDING'
    assert result['literature_status']=='NOT_RUN'
    assert 'belum dapat diverifikasi' in result['nodes']['realitas_fenomena']


def test_full_manifest_hashes_current_summary(tmp_path):
    out=tmp_path/'out';r=jorhas.full_research('rancangan uji',out)
    assert r['artifacts']['FULL_RESEARCH_SUMMARY.md']==sha256(out/'FULL_RESEARCH_SUMMARY.md')


def test_ledger_schema_rejects_permissive_legacy_types(tmp_path):
    r=jorhas.pathfind('uji schema',tmp_path/'out',fixture=FX)
    payload=json.loads((tmp_path/'out/DATA_LEDGER.json').read_text());payload['records'][0]['synthetic']='false'
    with pytest.raises(ValueError,match='synthetic'):validate_schema(payload,'pathfinder_data_ledger')
    assert r['manifest']['evidence_status']=='belum dapat diverifikasi'


def test_dns_mixed_public_private_answers_blocked(monkeypatch):
    monkeypatch.setattr(socket,'getaddrinfo',lambda *a,**kw:[(socket.AF_INET,socket.SOCK_STREAM,6,'',('93.184.216.34',443)),
                                                         (socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',443))])
    with pytest.raises(harvest.HarvestBlocked):harvest.public_addresses('test.invalid')


def test_transport_connects_numeric_validated_ip_and_keeps_tls_host(monkeypatch):
    session=harvest.public_session()
    cls=session.get_adapter('https://').poolmanager.pool_classes_by_scheme['https'].ConnectionCls
    monkeypatch.setattr(harvest,'public_addresses',lambda *a:['93.184.216.34'])
    calls=[];sentinel=object()
    monkeypatch.setattr(socket,'create_connection',lambda address,*a:(calls.append(address) or sentinel))
    connection=cls('test.example',port=443,timeout=2)
    assert connection._new_conn() is sentinel
    assert calls==[('93.184.216.34',443)] and connection.host=='test.example'
    assert session.trust_env is False


@pytest.mark.parametrize('path',['robots','cache'])
def test_limits_cover_robots_and_cache(tmp_path,path):
    class Response:
        status_code=200
        def iter_content(self,**kw):yield b'x'*100
        def close(self):pass
    class Session:
        def get(self,*a,**kw):return Response()
    url='https://example.org/feed'
    client=harvest.LimitedClient(session=Session(),max_bytes=10,cache_dir=tmp_path)
    if path=='cache':
        (tmp_path/(hashlib.sha256(url.encode()).hexdigest()+'.json')).write_bytes(b'x'*100)
    with pytest.raises(harvest.HarvestBlocked):client.get(url,robots=path=='robots')


@pytest.mark.parametrize('text',['=SUM(1,2)','+SUM(1,2)','-1+2','@SUM(1,2)','\t=1+2'])
def test_xlsx_untrusted_cells_are_text(text,tmp_path):
    synthia.export([{'title':text,'authors':text,'reading_level':'not_read'}],tmp_path/'out')
    book=load_workbook(tmp_path/'out/database_literatur.xlsx',data_only=False)
    assert book['Database Literatur']['D2'].value==text
    assert book['Database Literatur']['D2'].data_type=='s'


def test_template_beyond_1000_rows_and_formula_style_preserved(tmp_path):
    from openpyxl.styles import Font
    wb=Workbook();sheet=wb.active;sheet.title='Database Literatur';sheet.append(synthia.HEADERS)
    sheet.cell(1205,1,9000);sheet.cell(1205,4,'Keep this');sheet.cell(1205,17,'=1+2')
    sheet.cell(1205,4).font=Font(bold=True)
    source=tmp_path/'source.xlsx';wb.save(source);before=sha256(source)
    r=synthia.export([{'title':'New','reading_level':'not_read'}],tmp_path/'out',template_xlsx=source)
    result=load_workbook(tmp_path/'out/database_literatur.xlsx',data_only=False)
    assert r['xlsx_status']=='created' and sha256(source)==before
    assert result['Database Literatur']['D1205'].font.bold
    assert result['Database Literatur']['Q1205'].value=='=1+2'
    assert result['Database Literatur']['A1206'].value==9001


def test_quilo_docx_does_not_modify_source(tmp_path):
    from docx import Document
    doc=Document();doc.add_paragraph('Sebanyak 20 responden belum setuju.');doc.add_table(rows=1,cols=1).cell(0,0).text='Data 2025'
    path=tmp_path/'source.docx';doc.save(path);before=sha256(path)
    text=quilo.read_manuscript(path)
    assert '20 responden' in text and 'Data 2025' in text and sha256(path)==before


@pytest.mark.parametrize('old,new,tier',[
    ('Hasil pada 20 responden.','Hasil pada 25 responden.','HARD_BLOCK'),
    ('Responden tidak setuju.','Responden setuju.','HARD_BLOCK'),
    ('Peneliti membaca dokumen.','Dokumen dibaca peneliti.','EDITORIAL_REVIEW'),
    ('Perlu diketahui bahwa data tersedia.','data tersedia.','TRIVIAL_SAFE')])
def test_quilo_revision_tiers_never_certify_meaning(old,new,tier):
    r=quilo.validate_revision(old,new)
    assert r['revision_tier']==tier and r['semantic_validity']=='NOT_ASSESSED'


def test_doctor_runs_when_persona_dependency_is_missing(tmp_path):
    code="""import importlib.abc,sys
class Missing(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname=='pypdfium2':raise ModuleNotFoundError('simulated missing pypdfium2')
sys.meta_path.insert(0,Missing())
from epistarium.cli import main
raise SystemExit(main(['doctor']))
"""
    r=subprocess.run([sys.executable,'-c',code],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==4 and json.loads(r.stdout)['checks']['pypdfium2']['ok'] is False


def test_cli_partial_and_invalid_input_have_distinct_exit_codes(tmp_path):
    code='from epistarium.cli import main; import sys; raise SystemExit(main(sys.argv[1:]))'
    a=subprocess.run([sys.executable,'-c',code,'jorhas-pathfind','--idea','riset uji','--fixture',str(FX),'--out',str(tmp_path/'out')],cwd=ROOT,capture_output=True)
    b=subprocess.run([sys.executable,'-c',code,'jorhas-pathfind','--idea','riset uji','--out',str(tmp_path/'out')],cwd=ROOT,capture_output=True)
    assert a.returncode==3 and b.returncode==2


def test_domares_prefers_method_section_and_excludes_reference_titles(tmp_path):
    import fitz
    from epistarium import domares
    doc=fitz.open()
    for lines in [
        ['Abstract','A qualitative study uses participants and thematic analysis.',
         'Another qualitative study discusses participants and sampling.',
         'The qualitative summary names participants and data collection.'],
        ['Methods','This qualitative case study recruited 15 participants using purposive sampling.',
         'Data analysis used thematic analysis on interview transcripts.'],
        ['References','Author. Theory and results in experimental survey research.']]:
        page=doc.new_page()
        for n,line in enumerate(lines):page.insert_text((40,50+n*35),line,fontsize=9)
    path=tmp_path/'paper.pdf';doc.save(path);doc.close()
    article={'article_id':'section-test','status':'fulltext_local','source_identity_status':'title_matched',
             'pdf_path':str(path),'pdf_sha256':sha256(path)}
    result=domares.analyze([article],tmp_path/'out')[0]
    assert result['reported_by_author']['desain'][0]['pdf_page']==2
    assert result['reported_by_author']['desain'][0]['detected_section']=='methods'
    assert not result['reported_by_author']['teori_konsep']
    assert all(x['pdf_page']!=3 for passages in result['reported_by_author'].values() for x in passages)


def test_missing_retho_library_is_logged_without_aborting_other_stages(tmp_path):
    cfg={'liora_fixture':str(ROOT/'examples/f4_synthetic/full_crossref.json'),
         'retho_library':str(tmp_path/'missing.json')}
    r=jorhas.full_research('uji library hilang',tmp_path/'out',config=cfg)
    assert r['stage_statuses']['Retho']=='BLOCKED'
    assert r['stage_statuses']['Domares']=='NOT_RUN'
    assert r['stage_statuses']['Ideon ORIGO']=='SUCCESS'


@pytest.mark.parametrize('flag',['false','true',1,0])
def test_rights_flag_requires_explicit_boolean_true(tmp_path,flag):
    path=tmp_path/'data.csv';path.write_text('indikator,nilai\nExample,10\n')
    cfg={'sources':[{'provider':'local_csv','path':str(path),'rights_confirmed':flag}]}
    r=jorhas.pathfind('uji hak pengolahan',tmp_path/'out',config=cfg)
    assert not r['records']
    assert next(s for s in r['sources'] if s['source_id']=='ACTIVE01')['execution_status']=='BLOCKED'


def test_liora_mailto_remains_in_user_agent_after_transport_change(monkeypatch):
    agents=[]
    def fake_get(self,*args,**kwargs):
        agents.append(self.user_agent)
        return b'{"message":{"items":[]}}',{}
    monkeypatch.setattr(harvest.LimitedClient,'get',fake_get)
    assert liora.fetch_crossref('https://api.crossref.org/works',mailto='researcher@example.org')==[]
    assert 'mailto:researcher@example.org' in agents[0]


def test_network_header_injection_rejected():
    with pytest.raises(ValueError):harvest.LimitedClient(user_agent='Research\r\nInjected: data')
