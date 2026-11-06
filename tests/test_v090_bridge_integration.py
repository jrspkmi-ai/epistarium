"""Synthetic-only security and workflow tests, using loopback networking."""
import hashlib
from http.client import HTTPConnection
import json
from pathlib import Path
import socket
from threading import Thread
import time

import pytest
from docx import Document

from epistarium import domares, huxley, jorhas, origo
from epistarium.observatory import agent_adapter
from epistarium.observatory.bridge import SCHEMA, ingest
from epistarium.observatory.runner import ObservatoryRunner
from epistarium.observatory.server import ObservatoryServer
from epistarium.observatory.store import ObservatoryStore, read_json
from epistarium.observatory.verify_approval import verify

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'examples/f4_synthetic/pathfinder_cases.json'
ORIGINAL_CONNECT=socket.socket.connect
ORIGINAL_CONNECT_EX=socket.socket.connect_ex


@pytest.fixture(autouse=True)
def allow_only_loopback(monkeypatch,prevent_external_connections):
    def connect(sock,address):
        if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1'):
            raise AssertionError('External networking is prohibited')
        return ORIGINAL_CONNECT(sock,address)
    def connect_ex(sock,address):
        if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1'):
            raise AssertionError('External networking is prohibited')
        return ORIGINAL_CONNECT_EX(sock,address)
    monkeypatch.setattr(socket.socket,'connect',connect)
    monkeypatch.setattr(socket.socket,'connect_ex',connect_ex)


@pytest.fixture
def service(tmp_path):
    server=ObservatoryServer(tmp_path/'observatory',0,review_secret='review-secret-synthetic')
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    yield server
    server.shutdown();server.server_close();thread.join(timeout=3)


def request(server,route,payload,*,agent_token=None,session_token=None,host=None,origin=None):
    headers={'Host':host or f'127.0.0.1:{server.server_port}','Content-Type':'application/json'}
    if agent_token:headers['X-Agent-Token']=agent_token
    if session_token:headers['X-Observatory-Token']=session_token
    if origin:headers['Origin']=origin
    conn=HTTPConnection('127.0.0.1',server.server_port,timeout=4)
    conn.request('POST',route,json.dumps(payload).encode('utf-8'),headers)
    response=conn.getresponse();body=response.read();status=response.status;conn.close()
    return status,json.loads(body)


def event(run_id,**changes):
    value={'schema_version':SCHEMA,'event_id':'event-000001','run_id':run_id,'step_id':'liora',
           'persona':'Liora','actor':'opencode','operation':'run','status':'RUNNING'}
    value.update(changes);return value


def capability(server,run_id):return (server.store.runs/run_id/'bridge.token').read_text().strip()
def endpoint(run_id):return f'/api/runs/{run_id}/events/agent'


def test_scoped_capability_and_duplicate_after_restart(service):
    one=service.store.create('Synthetic research topic');two=service.store.create('Other synthetic topic')
    rid=one['id'];token=capability(service,rid);e=event(rid)
    assert request(service,endpoint(rid),e)[0]==403
    assert request(service,endpoint(rid),e,agent_token=capability(service,two['id']))[0]==403
    assert request(service,endpoint(rid),e,agent_token=token)[0]==201
    assert request(service,endpoint(rid),e,agent_token=token)[1]['duplicate'] is True
    assert request(service,endpoint(rid),event(rid,status='FAILED'),agent_token=token)[0]==400
    plan_path=service.store.runs/rid/'WORKFLOW_PLAN.json'
    plan=read_json(plan_path);plan.pop('agent_reported_steps',None)
    plan_path.write_text(json.dumps(plan),encoding='utf-8')
    restored=ObservatoryStore(service.store.root)
    assert ingest(restored,rid,e)['duplicate'] is True
    assert read_json(plan_path)['agent_reported_steps']['liora']['provenance']=='SELF_REPORTED'
    assert len([x for x in restored.events(rid) if x['kind']=='agent_event'])==1
    assert restored.get(rid)['personas']['Liora']=='NOT_RUN'


@pytest.mark.parametrize('change',[
    {'persona':'Unknown'}, {'status':'VERIFIED'}, {'actor':'runtime'},
    {'operation':'approve'}, {'reviewer':'local-user'}, {'evidence_status':'VERIFIED'},
    {'artifact_ref':{'path':'../secret.txt','sha256':'0'*64}},
    {'artifact_ref':{'path':'C:/secret.txt','sha256':'0'*64}},
])
def test_invalid_or_spoofed_event_rejected(service,change):
    state=service.store.create('Synthetic research topic');rid=state['id']
    assert request(service,endpoint(rid),event(rid,**change),agent_token=capability(service,rid))[0]==400
    assert service.store.get(rid)['evidence_status']=='belum dapat diverifikasi'


def test_foreign_origin_host_and_oversized_payload_rejected(service):
    state=service.store.create('Synthetic research topic');rid=state['id'];token=capability(service,rid)
    assert request(service,endpoint(rid),event(rid),agent_token=token,origin='https://example.org')[0]==403
    assert request(service,endpoint(rid),event(rid),agent_token=token,host='remote.example')[0]==403
    oversized=event(rid,extra='x'*9000)
    assert request(service,endpoint(rid),oversized,agent_token=token)[0]==413


def test_artifact_hash_and_separate_agent_status(service):
    state=service.store.create('Synthetic research topic');rid=state['id'];token=capability(service,rid)
    root=service.store.outputs/rid;artifact=root/'synthetic.txt';artifact.write_text('dummy data')
    ref={'path':'synthetic.txt','sha256':hashlib.sha256(artifact.read_bytes()).hexdigest()}
    e=event(rid,status='SUCCESS',operation='finish',artifact_ref=ref)
    assert request(service,endpoint(rid),e,agent_token=token)[0]==201
    assert service.store.agent_reports(rid)['Liora']['provenance']=='SELF_REPORTED'
    assert service.store.get(rid)['personas']['Liora']=='NOT_RUN'
    plan=read_json(service.store.runs/rid/'WORKFLOW_PLAN.json')
    assert plan['agent_reported_steps']['liora']['artifact_ref']['hash_checked_at_ingestion']
    assert next(x for x in plan['steps'] if x['persona']=='Liora')['execution_status']=='NOT_RUN'
    ref['sha256']='0'*64
    assert request(service,endpoint(rid),event(rid,event_id='event-000002',status='SUCCESS',artifact_ref=ref),agent_token=token)[0]==400


def test_symlink_artifact_rejected(service,tmp_path):
    state=service.store.create('Synthetic research topic');rid=state['id'];target=tmp_path/'outside.txt';target.write_text('outside')
    link=service.store.outputs/rid/'link.txt'
    try:link.symlink_to(target)
    except OSError:pytest.skip('Symlinks unavailable on this host')
    ref={'path':'link.txt','sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    assert request(service,endpoint(rid),event(rid,status='SUCCESS',artifact_ref=ref),agent_token=capability(service,rid))[0]==400


def test_agent_token_cannot_approve_even_if_session_token_obtained(service):
    state=service.store.create('Synthetic research topic');rid=state['id'];token=capability(service,rid)
    service.store.update(rid,status='AWAITING_APPROVAL',pending_gate='FINAL_ARTIFACT')
    (service.store.outputs/rid/'RUN_MANIFEST.json').write_text('{"synthetic":true}')
    route=f'/api/runs/{rid}/decide'
    assert request(service,route,{'decision':'approve'},agent_token=token)[0]==403
    assert request(service,route,{'decision':'approve'},session_token=service.token)[0]==403
    assert request(service,route,{'decision':'approve','review_secret':'incorrect-secret'},session_token=service.token)[0]==403
    assert request(service,route,{'decision':'approve','review_secret':'review-secret-synthetic'},session_token=service.token)[0]==200
    approval=read_json(service.store.runs/rid/'approvals.json')[0]
    assert approval['identity_assurance']=='LOCAL_SESSION_UNVERIFIED'
    assert approval['artifact_snapshot'] and 'review-secret-synthetic' not in json.dumps(approval)
    assert service.store.get(rid)['evidence_status']=='belum dapat diverifikasi'
    assert request(service,endpoint(rid),event(rid),agent_token=token)[0]==400
    assert verify(service.store.root,rid)['status']=='UNCHANGED'
    (service.store.outputs/rid/'RUN_MANIFEST.json').write_text('{"changed":true}')
    assert verify(service.store.root,rid)['status']=='CHANGED'


def test_rate_limit(service):
    state=service.store.create('Synthetic research topic');rid=state['id']
    service.agent_rate[rid].extend([time.monotonic()]*120)
    assert request(service,endpoint(rid),event(rid),agent_token=capability(service,rid))[0]==429


def test_spool_replay_is_idempotent(service,tmp_path,monkeypatch):
    state=service.store.create('Synthetic research topic');rid=state['id']
    token=service.store.runs/rid/'bridge.token';spool=tmp_path/'spool'
    e=event(rid)
    common=['--server',f'http://127.0.0.1:{service.server_port}','--run-id',rid,
          '--token-file',str(token),'--spool',str(spool)]
    import urllib.error
    def offline(*args,**kwargs):raise urllib.error.URLError('synthetic outage')
    with monkeypatch.context() as context:
        context.setattr(agent_adapter,'send',offline)
        assert agent_adapter.main(common+['report','--persona','Liora','--actor','opencode',
            '--step-id','liora','--operation','run','--status','RUNNING','--event-id','event-000001'])==3
    args=common+['replay']
    assert len(list(spool.glob('*.json')))==1
    assert agent_adapter.main(args)==0 and not list(spool.glob('*.json'))
    agent_adapter.spool_event(spool,e)
    assert agent_adapter.main(args)==0
    assert len([x for x in service.store.events(rid) if x['kind']=='agent_event'])==1
    with pytest.raises(ValueError):agent_adapter._url('https://example.org',rid)


def test_recovery_after_incomplete_event(tmp_path):
    store=ObservatoryStore(tmp_path/'store');rid=store.create('Synthetic topic')['id']
    path=store.runs/rid/'events.jsonl'
    with path.open('a',encoding='utf-8') as stream:stream.write('{"partial":')
    store.append(rid,'after_restart',message='valid checkpoint')
    assert store.events(rid)[-1]['kind']=='after_restart'


def test_sse_cursor_advances_after_one_thousand_events(service):
    rid=service.store.create('Synthetic topic')['id']
    path=service.store.runs/rid/'events.jsonl'
    with path.open('a',encoding='utf-8') as stream:
        for number in range(1002):stream.write(json.dumps({'kind':'synthetic','index':number})+'\n')
    client=HTTPConnection('127.0.0.1',service.server_port,timeout=4)
    client.request('GET',f'/api/runs/{rid}/events?token={service.token}',
       headers={'Host':f'127.0.0.1:{service.server_port}','Last-Event-ID':'1000'})
    response=client.getresponse();assert response.status==200
    assert response.fp.readline().decode().strip()=='id: 1003'
    client.close()


def test_full_run_correlates_events_and_plan(tmp_path):
    store=ObservatoryStore(tmp_path/'observatory')
    state=store.create('Synthetic communication research',mode='full',config={'pathfinder_fixture':str(FIXTURE)})
    rid=state['id'];runner=ObservatoryRunner(store);runner.launch(rid)
    deadline=time.monotonic()+20
    while time.monotonic()<deadline and store.get(rid)['status']=='RUNNING':time.sleep(.03)
    result=store.get(rid);assert result['status']=='AWAITING_APPROVAL'
    root=store.outputs/rid
    assert read_json(root/'FULL_RESEARCH_MANIFEST.json')['research_run_id']==rid
    assert read_json(root/'path_finding/RUN_MANIFEST.json')['research_run_id']==rid
    plan=read_json(root/'WORKFLOW_PLAN.json');assert plan['research_run_id']==rid
    assert len(plan['steps'])==10
    assert next(x for x in plan['steps'] if x['persona']=='Agresa')['execution_status']=='NOT_RUN'
    assert next(x for x in plan['steps'] if x['persona']=='Ideon')['execution_status']=='SUCCESS'
    assert all(x['event_source']=='runtime_observed' for x in store.events(rid) if x['kind']=='python_step')
    assert (root/'ideon/ideon_origo.json').exists()
    assert result['evidence_status']=='belum dapat diverifikasi'


def test_docx_sanitizes_copy_and_retains_input(tmp_path):
    idea='Synthetic topic\x0bwith control'
    result=origo.export({'ide_awal':idea,'mode':'ELABORATE_21'},tmp_path)
    assert result['docx_status']=='CREATED_AND_REOPENED'
    assert result['ide_awal']==idea
    audit=read_json(tmp_path/'sanitization_audit_docx.json')
    assert audit['total_replacements']>=1
    assert '\ufffd' in '\n'.join(p.text for p in Document(result['docx_path']).paragraphs)


def test_raw_excerpt_keeps_source_whitespace():
    page='The study purpose\nwas to evaluate a synthetic example.'
    result=domares._raw_excerpt(page,'The study purpose was to evaluate a synthetic example.')
    assert result==page and hashlib.sha256(result.encode()).hexdigest()==hashlib.sha256(page.encode()).hexdigest()
    assert domares._raw_excerpt(page,'a different statement') is None


def test_huxley_records_ambiguous_parentheses_and_nfc(tmp_path):
    assert huxley.classify_parenthetical('survei Juli 2023')=='NON_CITATION'
    assert huxley.classify_parenthetical('exposure 2023')=='AMBIGUOUS_REVIEW'
    assert huxley.classify_parenthetical('Data, 2023')=='CITATION'
    doc=Document();doc.add_paragraph('Unknown (exposure 2023); Martinčević (2023).')
    doc.add_paragraph('References');doc.add_paragraph('Martinc\u030cević, A. (2023). Synthetic article.')
    source=tmp_path/'synthetic.docx';doc.save(source)
    report=huxley.audit(source,tmp_path/'audit')
    assert report['classification_review'][0]['status']=='AMBIGUOUS_REVIEW'
    assert any(c['status']=='MATCHED' for c in report['citations'])
