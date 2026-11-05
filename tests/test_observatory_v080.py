"""No network or data access beyond loopback; all fixtures synthetic."""
import hashlib
import socket
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
import time
from urllib.parse import urlencode
import pytest
from epistarium.observatory.store import ObservatoryStore, PERSONAS, read_json
from epistarium.observatory.runner import ObservatoryRunner
from epistarium.observatory.server import ObservatoryServer

ORIGINAL_SOCKET_CONNECT=socket.socket.connect
ORIGINAL_SOCKET_CONNECT_EX=socket.socket.connect_ex

@pytest.fixture(autouse=True)
def allow_only_loopback(monkeypatch,prevent_external_connections):
    def local_connect(sock,address):
        if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1'):
            raise AssertionError('External network is prohibited in this test')
        return ORIGINAL_SOCKET_CONNECT(sock,address)
    def local_connect_ex(sock,address):
        if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1'):
            raise AssertionError('External network is prohibited in this test')
        return ORIGINAL_SOCKET_CONNECT_EX(sock,address)
    monkeypatch.setattr(socket.socket,'connect',local_connect)
    monkeypatch.setattr(socket.socket,'connect_ex',local_connect_ex)

FIXTURE=Path(__file__).resolve().parents[1]/'examples/f4_synthetic/pathfinder_cases.json'

@pytest.fixture
def store(tmp_path):return ObservatoryStore(tmp_path/'observatory')

@pytest.fixture
def service(tmp_path):
    server=ObservatoryServer(tmp_path/'service',0)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    yield server
    server.shutdown();server.server_close();thread.join(timeout=3)

def request(server,method,path,payload=None,token=None,host=None,origin=None,content_type='application/json'):
    headers={'Host':host or '127.0.0.1:'+str(server.server_port)}
    if token:headers['X-Observatory-Token']=token
    if origin:headers['Origin']=origin
    if payload is not None:
        headers['Content-Type']=content_type
        body=json.dumps(payload).encode()
    else:body=None
    conn=HTTPConnection('127.0.0.1',server.server_port,timeout=5)
    conn.request(method,path,body,headers)
    resp=conn.getresponse();data=resp.read();status=resp.status;conn.close()
    return status,json.loads(data) if data and b'json' in resp.getheader('Content-Type','').encode() else data

def wait_status(store,run_id,expected,timeout=15):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        state=store.get(run_id)
        if state['status']==expected:return state
        time.sleep(.03)
    raise AssertionError(f'Expected {expected}, observed {store.get(run_id)["status"]}')

def test_personas_exactly_ten():
    assert list(PERSONAS)==['Jorhas','Ideon','Liora','Agresa','Retho','Domares','Synthia','Vanlan','Quilo','Huxley']

def test_persisted_run_and_events(store):
    r=store.create('Digital crisis research',fixture=str(FIXTURE))
    assert len(r['personas'])==10 and r['synthetic'] and r['status']=='QUEUED'
    assert store.events(r['id'])[0]['kind']=='run_created'
    reopened=ObservatoryStore(store.root)
    assert reopened.get(r['id'])['idea']==r['idea']
    assert reopened.events(r['id'])[0]['run_id']==r['id']

def test_run_id_and_path_traversal_rejected(store):
    r=store.create('Digital crisis research')
    for invalid in ('../'+r['id'],'X'*32,'/etc/passwd',r['id']+'/extra',''):
        with pytest.raises(ValueError):store.get(invalid)

def test_lifecycle_and_authorization_not_semantic_verification(store):
    r=store.create('Research on digital consumer complaints',fixture=str(FIXTURE),language='en')
    runner=ObservatoryRunner(store);runner.launch(r['id'])
    state=wait_status(store,r['id'],'AWAITING_APPROVAL')
    assert state['execution_status']=='PARTIAL'
    assert state['evidence_status']=='belum dapat diverifikasi'
    assert state['personas']['Jorhas']=='PARTIAL'
    assert all(value=='NOT_RUN' for name,value in state['personas'].items() if name!='Jorhas')
    assert store.evidence_summary(r['id'])['synthetic'] is True
    assert (store.outputs/r['id']/'RUN_MANIFEST.json').is_file()
    assert any(event['kind']=='python_step' for event in store.events(r['id']))
    response=runner.decide(r['id'],'approve','Read the sample, acknowledge synthetic nature.')
    assert response['status']=='RELEASE_AUTHORIZED'
    auth=read_json(store.runs/r['id']/'release_authorization.json')
    assert auth['manifest_sha256']==hashlib.sha256((store.outputs/r['id']/'RUN_MANIFEST.json').read_bytes()).hexdigest()
    assert auth['evidence_status_unchanged']=='belum dapat diverifikasi'
    with pytest.raises(ValueError):runner.decide(r['id'],'approve')

def test_reject_requires_reason(store):
    r=store.create('Research on consumer trust',fixture=str(FIXTURE));runner=ObservatoryRunner(store)
    runner.launch(r['id']);wait_status(store,r['id'],'AWAITING_APPROVAL')
    with pytest.raises(ValueError):runner.decide(r['id'],'reject','')
    state=runner.decide(r['id'],'reject','The data are synthetic.')
    assert state['status']=='REJECTED'
    assert not (store.runs/r['id']/'release_authorization.json').exists()

def test_changes_requires_reason(store):
    r=store.create('Research on consumer trust',fixture=str(FIXTURE));runner=ObservatoryRunner(store)
    runner.launch(r['id']);wait_status(store,r['id'],'AWAITING_APPROVAL')
    with pytest.raises(ValueError):runner.decide(r['id'],'request_changes')
    assert runner.decide(r['id'],'request_changes','Need more sources')['status']=='NEEDS_CHANGES'

def test_online_gate_before_execution(store):
    r=store.create('Digital crisis research',fixture=str(FIXTURE),online=True)
    runner=ObservatoryRunner(store)
    assert r['status']=='AWAITING_APPROVAL' and r['pending_gate']=='ONLINE_ACCESS'
    assert not (store.outputs/r['id']/'SOURCE_LEDGER.json').exists()
    state=runner.decide(r['id'],'approve','Explicitly authorize future online calls')
    assert state['status'] in ('QUEUED','RUNNING','AWAITING_APPROVAL')
    wait_status(store,r['id'],'AWAITING_APPROVAL')
    assert store.get(r['id'])['pending_gate']=='FINAL_ARTIFACT'

def test_run_rejects_bad_user_inputs(store):
    for kw in ({'idea':'xx'},{'idea':'Topic','mode':'unknown'},{'idea':'Topic','language':'xx'},
               {'idea':'Topic','config':[]},{'idea':'Topic','fixture':'/nonexistent'},
               {'idea':'Topic','as_of':'not-a-date'}):
        with pytest.raises((ValueError,TypeError)):store.create(**kw)

def test_read_text_bounded_and_escaped_at_ui(store):
    r=store.create('Digital crisis research')
    out=store.outputs/r['id'];(out/'note.md').write_text('<script>alert(1)</script>',encoding='utf-8')
    assert store.artifact_text(r['id'],'note.md')=='<script>alert(1)</script>'
    with pytest.raises(FileNotFoundError):store.artifact_text(r['id'],'../../etc/passwd')
    (out/'note.pdf').write_bytes(b'%PDF-1.4')
    with pytest.raises(ValueError):store.artifact_text(r['id'],'note.pdf')

def test_symlink_artifact_rejected(store,tmp_path):
    r=store.create('Digital crisis research')
    private=tmp_path/'secret.md';private.write_text('private')
    link=store.outputs/r['id']/'link.md';link.symlink_to(private)
    assert all(x['path']!='link.md' for x in store.artifacts(r['id']))
    with pytest.raises(FileNotFoundError):store.artifact_text(r['id'],'link.md')

def test_loopback_server_endpoints_and_host_guard(service):
    status,data=request(service,'GET','/api/health');assert status==200 and data['status']=='ok'
    status,boot=request(service,'GET','/api/boot');assert status==200 and len(boot['token'])>25
    status,_=request(service,'GET','/api/runs');assert status==403
    status,_=request(service,'GET','/api/runs',token=boot['token'],host='research.evil.test');assert status==403
    status,_=request(service,'POST','/api/runs',{'idea':'Research question'},boot['token'],origin='http://evil.example');assert status==403
    status,_=request(service,'POST','/api/runs',{'idea':'Research question','online':True},boot['token']);assert status==400
    status,response=request(service,'POST','/api/runs',{'idea':'Research question'},boot['token']);assert status==201
    run_id=response['run_id'];wait_status(service.store,run_id,'AWAITING_APPROVAL')
    status,summary=request(service,'GET','/api/runs/'+run_id,token=boot['token']);assert status==200
    assert summary['run']['evidence_status']=='belum dapat diverifikasi' and len(summary['run']['personas'])==10
    assert 'fixture' not in summary['run'] and 'config' not in summary['run']
    status,_=request(service,'POST','/api/runs/'+run_id+'/decide',{'decision':'approve'},boot['token']);assert status==200
    assert service.store.get(run_id)['status']=='RELEASE_AUTHORIZED'

def test_wrong_content_type_and_id(service):
    token=request(service,'GET','/api/boot')[1]['token']
    status,_=request(service,'POST','/api/runs',{'idea':'Topic'},token,content_type='text/plain')
    assert status==415
    status,_=request(service,'GET','/api/runs/../../etc/passwd',token=token)
    assert status==404

def test_sse_stream_emits_actual_change(service):
    token=request(service,'GET','/api/boot')[1]['token']
    state=service.store.create('Research about digital F&B')
    client=HTTPConnection('127.0.0.1',service.server_port,timeout=4)
    client.request('GET','/api/runs/'+state['id']+'/events?token='+token,headers={'Host':'127.0.0.1:'+str(service.server_port)})
    response=client.getresponse()
    assert response.status==200 and 'event-stream' in response.getheader('Content-Type')
    lines=[]
    for i in range(4):
        lines.append(response.fp.readline().decode('utf-8').strip())
        if 'event: changed' in lines:break
    assert 'event: changed' in lines
    client.close()

@pytest.mark.parametrize('resource', ['index.html','style.css','app.js'])
def test_statics_ship_with_package(service,resource):
    status,content=request(service,'GET','/'+resource)
    assert status==200 and len(content)>100

def test_ui_translation_and_icons_static():
    from importlib.resources import files
    js=files('epistarium.observatory').joinpath('static','app.js').read_text(encoding='utf-8')
    html=files('epistarium.observatory').joinpath('static','index.html').read_text(encoding='utf-8')
    assert 'id:{' in js and 'en:{' in js
    for name in PERSONAS:assert name in js
    assert 'innerHTML=icon(r.name)' in js
    assert 'textContent=data.text' in js
    assert "<html lang=\"en\" data-theme=\"dark\">" in html

def test_json_schemas_validate_real_run_and_human_decision(store):
    from jsonschema import Draft202012Validator
    project=Path(__file__).resolve().parents[1]
    run=store.create('Digital consumer trust',fixture=str(FIXTURE))
    runner=ObservatoryRunner(store);runner.launch(run['id'])
    wait_status(store,run['id'],'AWAITING_APPROVAL')
    runner.decide(run['id'],'approve','Synthetic fixture review recorded.')
    objects=[(store.get(run['id']),'observatory_run'),
             (store.events(run['id'])[0],'observatory_event'),
             (read_json(store.runs/run['id']/'approvals.json')[0],'observatory_approval')]
    for obj,name in objects:
        schema=json.loads((project/'schemas'/f'{name}.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(obj)


def test_restarted_store_does_not_claim_stale_run_active(store):
    r=store.create('Research about crisis case')
    store.update(r['id'],status='RUNNING')
    restored=ObservatoryStore(store.root)
    state=restored.get(r['id'])
    assert state['status']=='BLOCKED'
    assert state['interruption_reason']=='LOCAL_PROCESS_RESTARTED'
    assert any(event['kind']=='interrupted' for event in restored.events(r['id']))
