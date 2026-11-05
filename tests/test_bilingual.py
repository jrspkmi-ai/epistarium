"""Language tests use synthetic sources and make no external requests."""
import ast
from concurrent.futures import ThreadPoolExecutor
import csv
import json
from pathlib import Path
import re
import string
import subprocess
import sys
import copy
import pytest
from docx import Document
from openpyxl import load_workbook
from epistarium import agresa,domares,synthia,jorhas,origo,liora,retho,vanlan,quilo,huxley
from epistarium.common import sha256,validate_schema,save_csv
from epistarium.cli import main,_selected_language
from epistarium.i18n import get_language,language_context,resolve_language,english_catalog,tr
from epistarium.gold_validation import compare_gold,parse_pdf_pages

ROOT=Path(__file__).resolve().parents[1]
FX=ROOT/'examples/f4_synthetic/pathfinder_cases.json'
COMMANDS=['doctor','vanlan-extract','vanlan-audit','liora-search','agresa-audit','retho-retrieve','domares-read',
          'synthia-review','f2-gold-evaluate','ideon-design','ideon-origo','quilo-audit','huxley-audit','jorhas-pathfind','jorhas-full']


@pytest.mark.parametrize('command',COMMANDS)
@pytest.mark.parametrize('lang',['id','en'])
def test_help_accepts_language_after_every_command(command,lang,capsys):
    with pytest.raises(SystemExit) as exc:main([command,'--lang',lang,'--help'])
    assert exc.value.code==0
    assert '--lang' in capsys.readouterr().out


@pytest.mark.parametrize('lang',['id','en'])
def test_language_works_before_subcommand(lang,capsys):
    assert main(['--lang',lang,'doctor'])==0
    assert json.loads(capsys.readouterr().out)['language']==lang


@pytest.mark.parametrize('locale_name,expected',[('id_ID','id'),('en_US','en'),('de_DE','en'),(None,'en')])
def test_auto_language_has_predictable_fallback(monkeypatch,locale_name,expected):
    import locale
    monkeypatch.setattr(locale,'getlocale',lambda:(locale_name,None))
    monkeypatch.delenv('LANG',raising=False);monkeypatch.delenv('LC_ALL',raising=False)
    assert resolve_language('auto')==expected


@pytest.mark.parametrize('value',['fr','ENGLISH','../en',''])
def test_explicit_unsupported_language_rejected(value):
    if value=='':assert resolve_language(value)=='id'
    else:
        with pytest.raises(ValueError):resolve_language(value)


def test_flag_env_config_priority(tmp_path,monkeypatch):
    path=tmp_path/'config.json';path.write_text('{"language":"en"}')
    monkeypatch.setenv('EPISTARIUM_LANG','id')
    assert _selected_language(['doctor','--config',str(path)])=='id'
    assert _selected_language(['doctor','--config',str(path),'--lang','en'])=='en'
    monkeypatch.delenv('EPISTARIUM_LANG')
    assert _selected_language(['doctor','--config',str(path)])=='en'


def test_python_default_and_explicit_language_do_not_leak(tmp_path):
    en=origo.build({'idea':'University communication'},lang='en')
    id_result=origo.build({'ide_awal':'Komunikasi kampus'})
    assert en['language']=='en' and id_result['language']=='id'
    assert get_language()=='id'
    with pytest.raises(ValueError):origo.build({'idea':'x'},lang='en')
    assert get_language()=='id'


def test_concurrent_language_contexts_are_separate():
    def task(lang):
        with language_context(lang):
            return origo.build({'idea':'University communication'})['questions'][0]['question']
    with ThreadPoolExecutor(4) as pool:
        result=list(pool.map(task,['en','id']*5))
    assert all(result[i].startswith('Why') for i in range(0,10,2))
    assert all(result[i].startswith('Mengapa') for i in range(1,10,2))
    assert get_language()=='id'


def test_config_language_is_inherited_by_nested_stages(tmp_path,monkeypatch):
    monkeypatch.chdir(ROOT)
    cfg=json.loads((ROOT/'examples/bilingual/full.en.json').read_text())
    result=jorhas.full_research('University communication',tmp_path/'out',config=cfg,as_of='2026-11-03')
    assert result['language']=='en'
    assert json.loads((tmp_path/'out/ideon/ideon_origo.json').read_text())['language']=='en'
    assert json.loads((tmp_path/'out/synthia/export_status.json').read_text())['language']=='en'
    assert get_language()=='id'


@pytest.mark.parametrize('lang',['id','en'])
def test_ledger_decisions_and_sources_keep_the_same_contract(lang,tmp_path):
    result=jorhas.pathfind('University communication',tmp_path/lang,fixture=FX,lang=lang,as_of='2026-11-03')
    assert all(r['status_verifikasi']=='belum dapat diverifikasi' and r['synthetic'] for r in result['records'])
    assert result['manifest']['language']==lang
    validate_schema(json.loads((tmp_path/lang/'DATA_LEDGER.json').read_text()),'pathfinder_data_ledger')
    validate_schema(json.loads((tmp_path/lang/'SOURCE_LEDGER.json').read_text()),'pathfinder_sources')
    assert all(r['source_id'] in {s['source_id'] for s in result['sources']} for r in result['records'])


def test_output_language_cannot_change_evidence_flags(tmp_path):
    a=jorhas.pathfind('The same idea',tmp_path/'a',fixture=FX,lang='id',as_of='2026-11-03')
    b=jorhas.pathfind('The same idea',tmp_path/'b',fixture=FX,lang='en',as_of='2026-11-03')
    keys=['record_id','source_id','jenis_data','nilai','satuan','status_verifikasi','synthetic','issue_codes','indikator','cuplikan']
    assert [{k:r[k] for k in keys} for r in a['records']]==[{k:r[k] for k in keys} for r in b['records']]


def test_external_status_is_not_promoted_in_english(tmp_path):
    fx=tmp_path/'fx.json';fx.write_text(json.dumps({'records':[{'record_id':'A','status_verifikasi':'terverifikasi','cuplikan':'Do not change this quote.'}]}))
    result=jorhas.pathfind('Source status test',tmp_path/'out',fixture=fx,lang='en')
    row=result['records'][0]
    assert row['source_claimed_status']=='terverifikasi'
    assert row['status_verifikasi']=='belum dapat diverifikasi'
    assert row['cuplikan']=='Do not change this quote.'


def test_display_csv_does_not_replace_the_canonical_file(tmp_path):
    row={'record_id':'A','indikator':'Belum dielaborasi.','status_verifikasi':'belum dapat diverifikasi'}
    with language_context('en'):save_csv(tmp_path/'data.csv',[row],list(row))
    with (tmp_path/'data.csv').open(encoding='utf-8-sig') as f:canonical=list(csv.DictReader(f))[0]
    with (tmp_path/'data_display.csv').open(encoding='utf-8-sig') as f:display=list(csv.DictReader(f))[0]
    assert canonical==row
    assert display['Indicator']==row['indikator']
    assert display['Evidence status']=='not yet verifiable'


def test_english_origo_fields_and_user_text_remain_intact():
    source={'language':'en','idea':'University communication','theory':'Teori pilihan pengguna',
            'method':'content analysis','data_access':{'corpus':'not yet available'},
            'answers':{'Q01':'A source answer in Indonesian: belum dapat diverifikasi.'}}
    original=copy.deepcopy(source)
    result=origo.build(source,lang='en')
    assert source==original
    assert result['teori_pengguna']=='Teori pilihan pengguna'
    assert result['metode_pengguna']=='content analysis'
    assert result['preferred_title'] is None
    assert any(c['status']=='KONFLIK' for c in result['checks'])
    assert result['questions'][0]['question'].startswith('Why')


@pytest.mark.parametrize('alias,canonical',[('idea','ide_awal'),('method','metode_pilihan'),('theory','teori_pilihan')])
def test_conflicting_aliases_fail_instead_of_silently_replacing(alias,canonical):
    with pytest.raises(ValueError,match='Conflicting fields'):origo.build({'idea':'University communication',alias:'A',canonical:'B'},lang='en')


def test_english_answer_list_is_accepted_without_translation():
    text='Jawaban sumber yang tetap asli.'
    result=origo.build({'idea':'University communication','mode':'ELABORATE_21','answers':[{'id':'Q01','answer':text}]},lang='en')
    assert result['questions'][0]['answer']==text


def test_revision_node_alias_keeps_unchanged_nodes_and_previous_input():
    previous=origo.build({'idea':'University communication'},lang='id');original=copy.deepcopy(previous)
    result=origo.build({'idea':'University communication','mode':'REVISION','changes':{'research_focus':'The changed focus.'}},previous=previous,lang='en')
    assert previous==original
    assert result['nodes']['fokus_penelitian']=='The changed focus.'
    assert result['changed_nodes']==['fokus_penelitian']
    for key in previous['nodes']:
        if key!='fokus_penelitian':assert result['nodes'][key]==previous['nodes'][key]


@pytest.mark.parametrize('lang,heading',[('en','01. Empirical Context'),('id','01. Realitas Fenomena')])
def test_origo_docx_has_six_localized_nodes_and_21_questions(tmp_path,lang,heading):
    result=origo.export({'idea':'University communication'},tmp_path/lang,lang=lang)
    assert result['docx_status']=='CREATED_AND_REOPENED'
    doc=Document(result['docx_path']);text='\n'.join(p.text for p in doc.paragraphs)
    assert heading in text
    assert len([p for p in doc.paragraphs if re.match(r'^Q\d\d\s',p.text)])==21
    if lang=='en':assert 'Why did you select this topic?' in text and 'Belum dielaborasi' not in text


@pytest.mark.parametrize('lang,expected',[('id','Tujuan'),('en','Aim / Research problem')])
def test_new_workbook_headers_follow_language(tmp_path,lang,expected):
    result=synthia.export([{'article_id':'A','title':'Raw title =SUM(1,2)','reading_level':'not_read'}],tmp_path/lang,lang=lang)
    assert result['xlsx_status']=='created'
    wb=load_workbook(tmp_path/lang/'database_literatur.xlsx',data_only=False)
    sheet=synthia.literature_sheet(wb)
    assert sheet.max_column==20
    assert sheet.cell(2,4).value=='Raw title =SUM(1,2)'
    if lang=='en':assert sheet.cell(1,7).value==expected
    else:assert sheet.cell(1,7).value.startswith(expected)


@pytest.mark.parametrize('template_lang,output_lang',[('id','en'),('en','id'),('en','en'),('id','id')])
def test_template_language_and_existing_source_content_are_preserved(tmp_path,template_lang,output_lang):
    original_dir=tmp_path/'original'
    synthia.export([{'title':'Original source title','reading_level':'not_read'}],original_dir,lang=template_lang)
    template=original_dir/'database_literatur.xlsx';before=sha256(template)
    wb=load_workbook(template);sheet=synthia.literature_sheet(wb);headers=[c.value for c in sheet[1]]
    result=synthia.export([{'title':'New source title','reading_level':'not_read'}],tmp_path/'new',template_xlsx=template,lang=output_lang)
    assert result['xlsx_status']=='created' and sha256(template)==before
    actual=synthia.literature_sheet(load_workbook(tmp_path/'new/database_literatur.xlsx'))
    assert [c.value for c in actual[1]]==headers
    assert actual['D2'].value=='Original source title' and actual['D3'].value=='New source title'


@pytest.mark.parametrize('source',['=SUM(1,2)','+SUM(1,2)','@SUM(1,2)','-1+2','Belum dielaborasi.'])
def test_source_strings_never_use_the_translation_catalog(source,tmp_path):
    synthia.export([{'title':source,'authors':source,'reading_level':'not_read'}],tmp_path/'out',lang='en')
    wb=load_workbook(tmp_path/'out/database_literatur.xlsx',data_only=False);sheet=synthia.literature_sheet(wb)
    assert sheet['D2'].value==source and sheet['D2'].data_type=='s'
    assert sheet['B2'].value==source


@pytest.mark.parametrize('scope',['phenomenon','empirical','theory','method','concept'])
def test_english_search_scopes_preserve_the_policy(scope):
    mapping={'phenomenon':'fenomena','empirical':'empiris','theory':'teori','method':'metode','concept':'konsep'}
    result=liora.query_plan('communication',scope,lang='en')
    assert result['scope']==mapping[scope]
    assert 'Crossref' in result['coverage_warning']


@pytest.mark.parametrize('note,expected',[('Method (PDF page 2-3)',{2,3}),('Result (PDF pages 4, 7)',{4,7}),('Metode (PDF hlm. 2, 5)',{2,5})])
def test_gold_page_notes_support_both_languages(note,expected):
    assert parse_pdf_pages(note)==expected


@pytest.mark.parametrize('text,new',[('The result does not support the claim.','The result does support the claim.'),
                                     ('The score increased.','The score decreased.'),
                                     ('The sample had 20 respondents.','The sample had 25 respondents.')])
def test_english_revision_guard_keeps_direction_and_negation(text,new):
    result=quilo.validate_revision(text,new,lang='en')
    assert result['revision_tier']=='HARD_BLOCK' and result['semantic_validity']=='NOT_ASSESSED'


def test_english_preset_flags_prose_without_automatic_rewriting(tmp_path):
    text='The robust method may improve trust in 20 respondents (Smith, 2025).'
    result=quilo.audit(text,tmp_path/'out',style=quilo.ENGLISH_STYLE,lang='en')
    assert result['style']=='academic-en' and result['issues']
    assert (tmp_path/'out/usulan_sunting.txt').read_text()==text
    assert result['automated_edits']==[]
    assert result['semantic_validity']=='NOT_ASSESSED'


def test_both_languages_keep_export_failure_blocked(tmp_path,monkeypatch):
    monkeypatch.setattr(origo,'_doc',lambda *a:(_ for _ in ()).throw(RuntimeError('synthetic failure')))
    for lang in ['id','en']:
        result=jorhas.full_research('University communication',tmp_path/lang,lang=lang)
        assert result['stage_statuses']['Ideon ORIGO']=='BLOCKED'
        assert result['stage_statuses']['Quilo']=='NOT_RUN'
        assert result['deliverable_status']=='INCOMPLETE'


def test_catalog_placeholders_match_and_all_used_messages_exist():
    catalog=english_catalog();formatter=string.Formatter()
    def fields(text):return {f for _,f,_,_ in formatter.parse(text) if f is not None}
    for source,target in catalog.items():assert fields(source)==fields(target),source
    missing=[]
    for path in (ROOT/'epistarium').glob('*.py'):
        if path.name=='i18n.py':continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='tr' and node.args:
                if isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str) and node.args[0].value not in catalog:
                    missing.append((path.name,node.lineno,node.args[0].value))
    assert not missing


def test_sampling_warnings_apply_to_english_source_descriptions():
    from epistarium.pathfinder_ledger import normalize_record
    row=normalize_record({'jenis_data':'survei','metode_sampling':'voluntary nonprobability',
      'sampel':'200 participants','populasi':'residents','representativitas':'nationally representative'},1)
    assert 'TIDAK_DAPAT_DIGENERALISASI_PROBABILISTIK' in row['issue_codes']
    assert 'KLAIM_REPRESENTATIVITAS_TIDAK_DIDUKUNG' in row['issue_codes']


def test_agresa_report_uses_english_without_promoting_index_evidence(tmp_path):
    journals=json.loads((ROOT/'examples/journals.json').read_text())
    evidence=json.loads((ROOT/'examples/index_evidence.json').read_text())
    rows=agresa.audit(journals,evidence,tmp_path/'out',lang='en')
    report=(tmp_path/'out/laporan.md').read_text()
    assert report.startswith('# Agresa report') and 'Identity:' in report
    assert 'Identitas:' not in report and 'Catatan:' not in report
    assert all(not r.get('independent_verification') for r in rows)


def test_vanlan_report_keeps_claims_and_does_not_approve_meaning(tmp_path):
    claim='Belum dielaborasi. This phrase is a source claim, not interface text.'
    rows=vanlan.audit([{'id':'C1','text':claim,'jenis':'parafrasa'}],tmp_path/'pdfs',tmp_path/'out',lang='en')
    report=(tmp_path/'out/laporan.md').read_text()
    assert claim in report and 'Claim:' in report and 'Support for meaning:' in report
    assert rows[0]['claim']==claim and rows[0]['status']=='belum dapat diverifikasi'
    assert '# Vanlan evidence report' in report


def test_english_xlsx_failure_still_reports_existing_csv_and_blocked_stage(tmp_path,monkeypatch):
    monkeypatch.chdir(ROOT)
    cfg=json.loads((ROOT/'examples/bilingual/full.en.json').read_text())
    monkeypatch.setattr(synthia,'_export_xlsx',lambda *a,**kw:(_ for _ in ()).throw(OSError('synthetic failure')))
    result=jorhas.full_research('University communication',tmp_path/'out',config=cfg,lang='en')
    assert result['stage_statuses']['Synthia']=='BLOCKED'
    assert (tmp_path/'out/synthia/database_literatur_display.csv').is_file()
    assert not (tmp_path/'out/synthia/database_literatur.xlsx').exists()


def test_english_gold_workbook_can_be_used_by_page_comparison(tmp_path):
    synthia.export([{'title':'Source','doi':'10.5555/a','reading_level':'not_read'}],tmp_path/'syn',lang='en')
    path=tmp_path/'syn/database_literatur.xlsx'
    book=load_workbook(path);sheet=synthia.literature_sheet(book);sheet['H2']='Method (PDF page 2)';book.save(path)
    result=compare_gold([{'doi':'10.5555/a','reported_by_author':{'desain':[{'pdf_page':2}]}}],path,tmp_path/'gold',lang='en')
    assert result['status_counts']['PAGE_OVERLAP']==1
    assert result['semantic_accuracy']=='NOT MEASURED'


def test_english_new_audit_sheet_has_readable_column_widths(tmp_path):
    synthia.export([{'title':'Source','reading_level':'not_read'}],tmp_path/'out',lang='en')
    book=load_workbook(tmp_path/'out/database_literatur.xlsx')
    assert book['Evidence Audit'].column_dimensions['E'].width>=60
    assert book['Evidence Audit'].freeze_panes=='A2'


def test_english_issue_explanations_do_not_rename_canonical_codes(tmp_path):
    result=jorhas.pathfind('University communication',tmp_path/'out',fixture=FX,lang='en')
    report=(tmp_path/'out/PATH_FINDING_REPORT.md').read_text()
    assert 'PENYEBUT_TIDAK_TERSEDIA' in report and 'The denominator is missing' in report
    assert 'PENYEBUT_TIDAK_TERSEDIA' in result['records'][1]['issue_codes']
