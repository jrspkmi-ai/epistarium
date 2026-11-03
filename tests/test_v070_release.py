"""Release preparation behaviors. All inputs are local and synthetic."""
from pathlib import Path
import importlib.util
import json
import shutil
import zipfile
import pytest
from epistarium import jorhas,synthia
from epistarium.pathfinder_harvest import rss_from_payload
from defusedxml.common import EntitiesForbidden

ROOT=Path(__file__).resolve().parents[1]


def load_script(name):
    spec=importlib.util.spec_from_file_location('v070_'+name,ROOT/'scripts'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


@pytest.fixture
def adapter(tmp_path):
    project=tmp_path/'project';project.mkdir()
    shutil.copytree(ROOT/'.agents/skills',project/'.agents/skills')
    return load_script('sync_host_skills'),project


def test_adapter_sync_update_and_removal_preserve_unrelated_skills(adapter):
    tool,project=adapter
    assert tool.sync(project)['status']=='NOT_INSTALLED'
    assert tool.sync(project,'apply')['status']=='PASS'
    for source in (project/'.agents/skills').rglob('*'):
        if source.is_file():assert source.read_bytes()==(project/'.claude/skills'/source.relative_to(project/'.agents/skills')).read_bytes()
    entry=next((project/'.agents/skills').glob('*/references/guide.en.md'))
    entry.write_text(entry.read_text()+'\nCanonical update.\n')
    assert tool.sync(project)['status']=='STALE'
    assert tool.sync(project,'apply')['status']=='PASS'
    unrelated=project/'.claude/skills/my-other-skill/SKILL.md';unrelated.parent.mkdir();unrelated.write_text('keep')
    assert tool.sync(project,'remove')['status']=='REMOVED'
    assert unrelated.read_text()=='keep'
    assert len(list((project/'.agents/skills').glob('*/SKILL.md')))==10


@pytest.mark.parametrize('action',['apply','remove'])
def test_adapter_refuses_modified_managed_files(adapter,action):
    tool,project=adapter;tool.sync(project,'apply')
    path=next((project/'.claude/skills').glob('*/references/guide.en.md'));path.write_text('user edit')
    with pytest.raises(ValueError,match='Modified adapter'):tool.sync(project,action)
    assert path.read_text()=='user edit'


def test_adapter_refuses_unmanaged_collision(adapter):
    tool,project=adapter
    name=next((project/'.agents/skills').iterdir()).name
    path=project/'.claude/skills'/name/'SKILL.md';path.parent.mkdir(parents=True);path.write_text('keep')
    with pytest.raises(ValueError,match='Unmanaged|unmanaged'):tool.sync(project,'apply')
    assert path.read_text()=='keep'


@pytest.mark.parametrize('where',['source','target','manifest'])
def test_adapter_refuses_symlink_redirection(adapter,tmp_path,where):
    tool,project=adapter;outside=tmp_path/'outside';outside.mkdir()
    if where=='source':
        entry=next((project/'.agents/skills').iterdir());shutil.rmtree(entry);entry.symlink_to(outside,target_is_directory=True)
    elif where=='target':
        (project/'.claude').mkdir();(project/'.claude/skills').symlink_to(outside,target_is_directory=True)
    else:
        (project/'.claude').mkdir();outsidefile=outside/'manifest';outsidefile.write_text('{}');(project/'.claude/epistarium-skills.json').symlink_to(outsidefile)
    with pytest.raises(ValueError):tool.sync(project,'apply')
    assert not list(outside.glob('*/SKILL.md'))


def test_adapter_rejects_manifest_traversal(adapter):
    tool,project=adapter;tool.sync(project,'apply')
    manifest=project/'.claude/epistarium-skills.json';data=json.loads(manifest.read_text());data['files']['../../../outside']='bad';manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='Unsafe'):tool.sync(project,'remove')


def test_adapter_preflights_temporary_collision(adapter):
    tool,project=adapter;tool.sync(project,'apply')
    paths=sorted((project/'.claude/skills').rglob('guide.id.md'));collision=paths[-1].with_name('guide.id.md.epistarium-tmp');collision.write_text('keep')
    old=paths[0].read_bytes()
    with pytest.raises(ValueError):tool.sync(project,'apply')
    assert paths[0].read_bytes()==old and collision.read_text()=='keep'


@pytest.mark.parametrize('relative',['private/draft.docx','userdata/a.csv','interviews/a.txt','respondent-identities/a.csv','licensed-pdfs/paper.pdf',
 'raw-data/a.csv','.env','credentials.json','secrets.json','a.pem','.venv/lib/a.py','.claude/skills/a/SKILL.md','build/file','.cache/a','reports/private-run/a.csv'])
def test_release_selection_excludes_private_material(tmp_path,relative):
    tool=load_script('package_release');p=tmp_path/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('private')
    good=tmp_path/'examples/synthetic.pdf';good.parent.mkdir(exist_ok=True);good.write_bytes(b'synthetic fixture')
    assert p not in tool.selected_files(tmp_path)
    assert good in tool.selected_files(tmp_path)


def test_rss_rejects_xml_entities_before_expansion():
    payload=b'<!DOCTYPE rss [<!ENTITY x "private secret">]><rss><channel><item><title>&x;</title></item></channel></rss>'
    with pytest.raises(EntitiesForbidden):rss_from_payload(payload,'https://example.org/rss')


def test_shipped_real_metadata_config_does_not_grant_rights(tmp_path,monkeypatch):
    monkeypatch.chdir(ROOT)
    cfg=json.loads((ROOT/'examples/f4_public_metadata/bps_manual_config.json').read_text())
    assert cfg['sources'][0]['rights_confirmed'] is False
    result=jorhas.pathfind('Internet use in Indonesia',tmp_path/'out',config=cfg)
    assert result['records']==[]
    assert any(s['execution_status']=='BLOCKED' for s in result['sources'])


def test_untrusted_workbook_entity_does_not_become_created_output(tmp_path):
    from openpyxl import Workbook
    safe=tmp_path/'safe.xlsx';Workbook().save(safe)
    hostile=tmp_path/'hostile.xlsx'
    with zipfile.ZipFile(safe) as src,zipfile.ZipFile(hostile,'w') as dst:
        for name in src.namelist():
            data=src.read(name)
            if name=='xl/worksheets/sheet1.xml':
                data=b'<!DOCTYPE worksheet [<!ENTITY secret "sensitive">]><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>&secret;</t></is></c></row></sheetData></worksheet>'
            dst.writestr(name,data)
    result=synthia.export([],tmp_path/'out',template_xlsx=hostile)
    assert result['xlsx_status'].startswith('failed:')
    assert not (tmp_path/'out/database_literatur.xlsx').exists()


@pytest.mark.parametrize('lang',['en','id'])
@pytest.mark.parametrize('printed',[True,False])
def test_domares_printed_page_values_reach_synthia_without_dictionary_keys(tmp_path,lang,printed):
    import fitz
    from epistarium import domares
    from epistarium.common import sha256
    pdf=tmp_path/'synthetic.pdf'
    doc=fitz.open();page=doc.new_page(width=595,height=842)
    page.insert_text((50,60),'Introduction\nThe research problem concerns communication practices in a synthetic university.\nThis synthetic study describes a local case with uncertain transferability.\nThe purpose of the study is to examine communication routines and source limits.\nMethods\nA qualitative case study design used interviews as a synthetic example only.')
    if printed:page.insert_text((260,810),'Page 7')
    doc.save(pdf);doc.close()
    readings=domares.analyze([{'article_id':'synthetic-printed-page','pdf_path':str(pdf),'pdf_sha256':sha256(pdf),
                              'status':'fulltext_local','source_identity_status':'doi_matched','doi':'10.1234/synthetic',
                              'title':'Synthetic page provenance','authors':'Synthetic Author','year':2026}],tmp_path/'domares',lang=lang)
    candidates=readings[0]['reported_by_author']['masalah']
    assert candidates and candidates[0]['pdf_page']==1
    assert candidates[0]['printed_page']==('7' if printed else None)
    assert candidates[0]['printed_page_method'] not in ('printed_page','printed_page_method')
    result=synthia.export(readings,tmp_path/'synthia',lang=lang)
    assert result['xlsx_status']=='created'
    assert result['audit'] and all(row['printed_page']==('7' if printed else None) for row in result['audit'])
    from openpyxl import load_workbook
    book=load_workbook(tmp_path/'synthia/database_literatur.xlsx')
    audit=book['Evidence Audit' if lang=='en' else 'Audit F2']
    assert audit.cell(2,4).value==('7' if printed else None)
    book.close()


@pytest.mark.parametrize('lang',['en','id'])
def test_fresh_process_doctor_stdout_is_clean_json(lang):
    import subprocess,sys
    process=subprocess.run([sys.executable,'-I','-m','epistarium','doctor','--lang',lang],cwd=ROOT,capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    result=json.loads(process.stdout)
    assert result['version']=='0.7.1' and result['language']==lang
    assert result['checks']['pypdfium2']['ok'] is True
    assert result['checks']['pypdf']['ok'] is True
