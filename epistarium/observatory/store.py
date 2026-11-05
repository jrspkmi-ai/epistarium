"""Local, append-only run/event persistence and bounded, gated decisions."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from threading import Condition, RLock
from typing import Any
import hashlib
import json
import os
import re
import uuid

PERSONAS = {
    'Jorhas':'Path Finder', 'Ideon':'Research Architect', 'Liora':'Literature Scout',
    'Agresa':'Index Sentinel', 'Retho':'Paper Retriever', 'Domares':'Critical Reader',
    'Synthia':'Knowledge Weaver', 'Vanlan':'Evidence Guardian',
    'Quilo':'Academic Scribe', 'Huxley':'Citation Cartographer',
}
RUN_ID = re.compile(r'^[0-9a-f]{32}$')
ALLOWED_MODES = {'pathfind', 'full'}
STATES = {'QUEUED','RUNNING','AWAITING_APPROVAL','RELEASE_AUTHORIZED','REJECTED','NEEDS_CHANGES','FAILED','BLOCKED'}
STAGES = {'NOT_RUN','QUEUED','RUNNING','SUCCESS','PARTIAL','BLOCKED','FAILED'}


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def atomic_json(path:Path, payload:dict):
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    target=path.with_suffix(path.suffix+'.tmp-'+uuid.uuid4().hex)
    try:
        with target.open('x',encoding='utf-8') as stream:
            json.dump(payload,stream,ensure_ascii=False,indent=2)
            stream.write('\n');stream.flush();os.fsync(stream.fileno())
        os.replace(target,path)
    finally:
        target.unlink(missing_ok=True)


def read_json(path:Path, fallback:Any=None):
    try:
        if path.stat().st_size>2_000_000: return fallback
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError,ValueError,UnicodeError):
        return fallback


class ObservatoryStore:
    def __init__(self,root):
        self.root=Path(root).expanduser().resolve()
        self.runs=self.root/'runs'
        self.outputs=self.root/'outputs'
        self.runs.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.outputs.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.lock=RLock()
        self.conditions={}
        # A process crash must not leave a stale RUNNING badge on restart.
        # Authorization pending after a finished run remains pending.
        for candidate in self.runs.iterdir():
            if candidate.is_symlink() or not candidate.is_dir() or not RUN_ID.fullmatch(candidate.name):
                continue
            previous=read_json(candidate/'run.json')
            if isinstance(previous,dict) and previous.get('status') in ('RUNNING','QUEUED'):
                previous['status']='BLOCKED'
                previous['updated_at']=utcnow()
                previous['interruption_reason']='LOCAL_PROCESS_RESTARTED'
                atomic_json(candidate/'run.json',previous)
                self._append(candidate.name,'interrupted',message='The prior local process stopped; no resumed execution is claimed.')

    def _dir(self,run_id):
        if not isinstance(run_id,str) or not RUN_ID.fullmatch(run_id):
            raise ValueError('Invalid run identifier')
        path=self.runs/run_id
        if path.is_symlink() or not path.is_dir():
            raise FileNotFoundError('Run not found')
        return path

    def _output(self,run_id):
        self._dir(run_id)
        return self.outputs/run_id

    def create(self,idea,mode='pathfind',*,fixture=None,config=None,online=False,language='en',as_of=None,timezone_name='Asia/Jakarta'):
        if not isinstance(idea,str) or not 3<=len(idea.strip())<=1000:
            raise ValueError('Idea must contain 3 to 1000 characters')
        if mode not in ALLOWED_MODES:raise ValueError('Unsupported mode')
        if language not in ('en','id'):raise ValueError('Unsupported language')
        if config is not None and not isinstance(config,dict):raise ValueError('Config must be an object')
        if fixture is not None and (not isinstance(fixture,str) or not Path(fixture).is_file()):raise ValueError('Fixture not found')
        if as_of is not None:
            from datetime import date
            date.fromisoformat(as_of)
        if not isinstance(timezone_name,str) or len(timezone_name)>80:raise ValueError('Invalid time zone')
        run_id=uuid.uuid4().hex
        with self.lock:
            base=self.runs/run_id
            base.mkdir(mode=0o700)
            (self.outputs/run_id).mkdir(mode=0o700)
            state={'schema':'epistarium.observatory.run.v1','id':run_id,'idea':idea.strip(),
                'mode':mode,'language':language,'status':'AWAITING_APPROVAL' if online else 'QUEUED',
                'created_at':utcnow(),'updated_at':utcnow(),'synthetic':bool(fixture),
                'online_requested':bool(online),'fixture':str(Path(fixture).resolve()) if fixture else None,
                'config':config or {},'as_of':as_of,'timezone':timezone_name,
                'execution_status':'NOT_RUN','evidence_status':'belum dapat diverifikasi',
                'deliverable_status':'NOT_RUN','approval':None,
                'pending_gate':'ONLINE_ACCESS' if online else None,
                'personas':{name:'NOT_RUN' for name in PERSONAS},
                'outputs_relative':f'outputs/{run_id}'}
            atomic_json(base/'run.json',state)
            self.conditions[run_id]=Condition(self.lock)
            self._append(run_id,'run_created',message='Run created; no evidence has yet been verified.')
            if online:self._append(run_id,'approval_requested',gate='ONLINE_ACCESS',message='External access requires explicit consent.')
        return self.get(run_id)

    def get(self,run_id):
        data=read_json(self._dir(run_id)/'run.json')
        if not isinstance(data,dict):raise FileNotFoundError('Run state unavailable')
        return data

    def list(self,limit=50):
        rows=[]
        for path in sorted(self.runs.iterdir(),reverse=True):
            if len(rows)>=limit:break
            if path.is_dir() and not path.is_symlink() and RUN_ID.fullmatch(path.name):
                data=read_json(path/'run.json')
                if isinstance(data,dict):
                    # Strip paths and configs that may reveal local study data.
                    rows.append({k:data.get(k) for k in ('id','idea','mode','status','language','created_at','updated_at','synthetic','pending_gate')})
        return sorted(rows,key=lambda r:r['created_at'],reverse=True)

    def _append(self,run_id,kind,**payload):
        d=self._dir(run_id);events=d/'events.jsonl'
        record={'schema':'epistarium.observatory.event.v1','event_id':uuid.uuid4().hex,
                'run_id':run_id,'time':utcnow(),'kind':kind,**payload}
        serialized=json.dumps(record,ensure_ascii=False,separators=(',',':'))
        if len(serialized)>16_384:raise ValueError('Event exceeds permitted size')
        with events.open('a',encoding='utf-8') as stream:
            stream.write(serialized+'\n');stream.flush();os.fsync(stream.fileno())
        condition=self.conditions.get(run_id)
        if condition:condition.notify_all()
        return record

    def append(self,run_id,kind,**payload):
        with self.lock:
            return self._append(run_id,kind,**payload)

    def update(self,run_id,**changes):
        with self.lock:
            state=self.get(run_id)
            if 'status' in changes and changes['status'] not in STATES:raise ValueError('Invalid run status')
            state.update(changes)
            state['updated_at']=utcnow()
            atomic_json(self._dir(run_id)/'run.json',state)
            self._append(run_id,'run_updated',status=state['status'],message='Run state changed.')
            return state

    def persona(self,run_id,name,status,*,detail=None):
        if name not in PERSONAS or status not in STAGES:raise ValueError('Invalid persona or stage status')
        with self.lock:
            state=self.get(run_id)
            state['personas'][name]=status
            state['updated_at']=utcnow()
            atomic_json(self._dir(run_id)/'run.json',state)
            self._append(run_id,'persona',persona=name,status=status,message=(detail or f'{name}: {status}')[:500])

    def events(self,run_id):
        path=self._dir(run_id)/'events.jsonl'
        if not path.is_file():return []
        rows=[]
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                try:
                    entry=json.loads(line)
                    if isinstance(entry,dict):rows.append(entry)
                except json.JSONDecodeError:
                    continue
        return rows[-1000:]

    def wait(self,run_id,seconds=10):
        with self.lock:
            self._dir(run_id)
            condition=self.conditions.setdefault(run_id,Condition(self.lock))
            condition.wait(timeout=min(float(seconds),15))

    def record_decision(self,run_id,decision,reason='',reviewer='local-user'):
        if decision not in ('approve','reject','request_changes'):raise ValueError('Unsupported decision')
        if not isinstance(reason,str) or len(reason)>1000:raise ValueError('Invalid reason')
        if decision!='approve' and not reason.strip():raise ValueError('A reason is required')
        with self.lock:
            state=self.get(run_id)
            if state['status']!='AWAITING_APPROVAL' or state.get('pending_gate') not in ('ONLINE_ACCESS','FINAL_ARTIFACT'):
                raise ValueError('No approval is currently pending')
            gate=state['pending_gate']
            # A record of authorization does not establish claim support or source verification.
            record={'decision':decision,'gate':gate,'reviewer':reviewer,'reason':reason.strip(),
                    'time':utcnow(),'evidence_status_unchanged':state['evidence_status']}
            if gate=='FINAL_ARTIFACT':
                report=self._output(run_id)/('RUN_MANIFEST.json' if state['mode']=='pathfind' else 'FULL_RESEARCH_MANIFEST.json')
                if report.is_file():record['manifest_sha256']=hashlib.sha256(report.read_bytes()).hexdigest()
            d=self._dir(run_id)
            approvals=read_json(d/'approvals.json',[]) or []
            approvals.append(record)
            atomic_json(d/'approvals.json',approvals)
            state['approval']=record
            state['pending_gate']=None
            if decision=='approve':
                if gate=='FINAL_ARTIFACT':
                    state['status']='RELEASE_AUTHORIZED'
                    atomic_json(d/'release_authorization.json',{
                        'schema':'epistarium.observatory.authorization.v1',**record,
                        'disclaimer':'Authorization to release artifacts, not semantic verification.'})
                else:state['status']='QUEUED'
            elif decision=='reject':state['status']='REJECTED'
            else:state['status']='NEEDS_CHANGES'
            state['updated_at']=utcnow()
            atomic_json(d/'run.json',state)
            self._append(run_id,'decision',gate=gate,decision=decision,message='Human decision recorded; evidence status unchanged.')
            return {'record':record,'state':state}

    def artifacts(self,run_id):
        root=self._output(run_id)
        if not root.exists():return []
        found=[]
        for path in sorted(root.rglob('*')):
            if path.is_symlink() or not path.is_file():continue
            if root.resolve() not in path.resolve().parents:continue
            if len(found)>=150:break
            rel=path.relative_to(root).as_posix()
            found.append({'name':path.name,'path':rel,'bytes':path.stat().st_size})
        return found

    def artifact_text(self,run_id,relative):
        if not isinstance(relative,str) or not relative or len(relative)>280:raise ValueError('Invalid path')
        root=self._output(run_id).resolve()
        dest=(root/relative).resolve()
        if root not in dest.parents or not dest.is_file() or dest.is_symlink():raise FileNotFoundError('Artifact unavailable')
        if dest.suffix.lower() not in ('.md','.txt','.json','.csv') or dest.stat().st_size>150_000:
            raise ValueError('Preview is limited to small text artifacts')
        return dest.read_text(encoding='utf-8')[:12000]

    def evidence_summary(self,run_id):
        root=self._output(run_id)
        src=read_json(root/'SOURCE_LEDGER.json',{})
        data=read_json(root/'DATA_LEDGER.json',{})
        return {'source_records':len(src.get('records',[])) if isinstance(src,dict) else None,
                'data_records':len(data.get('records',[])) if isinstance(data,dict) else None,
                'synthetic':self.get(run_id)['synthetic'],
                'warning':'Counts are records, not independently verified findings.'}
