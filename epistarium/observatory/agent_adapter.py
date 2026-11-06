"""Send real host checkpoints or replay a private local spool.

This adapter does not observe the host by itself. The host must call it at the
time an action starts or ends. It cannot authorize research or verify evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

from .bridge import SCHEMA, EVENT_ID
from .store import RUN_ID


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _url(base, run_id):
    if not RUN_ID.fullmatch(run_id):raise ValueError('Invalid run identifier')
    parsed=urllib.parse.urlsplit(base)
    if (parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost') or
            parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment):
        raise ValueError('Only an explicit local HTTP Observatory is allowed')
    if not parsed.port:raise ValueError('An explicit local port is required')
    return f'http://{parsed.hostname}:{parsed.port}/api/runs/{run_id}/events/agent'


def send(base, run_id, token_file, event):
    path=Path(token_file)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>200:
        raise ValueError('Capability file unavailable')
    token=path.read_text(encoding='ascii').strip()
    request=urllib.request.Request(_url(base,run_id),data=json.dumps(event,ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type':'application/json','X-Agent-Token':token},method='POST')
    opener=urllib.request.build_opener(NoRedirect, urllib.request.ProxyHandler({}))
    with opener.open(request,timeout=5) as response:
        return json.loads(response.read(8192))


def spool_event(spool, event):
    if not EVENT_ID.fullmatch(event.get('event_id','')):raise ValueError('Invalid event identifier')
    directory=Path(spool);directory.mkdir(mode=0o700,parents=True,exist_ok=True)
    path=directory/(event['event_id']+'.json')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as stream:
        json.dump(event,stream,ensure_ascii=False)
    return path


def main(argv=None):
    parser=argparse.ArgumentParser(description='Report actual host activity; does not verify it')
    parser.add_argument('--server',required=True,help='e.g. http://127.0.0.1:4782')
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--token-file',required=True)
    parser.add_argument('--spool',required=True,help='Private directory, no capability is saved here')
    sub=parser.add_subparsers(dest='command',required=True)
    report=sub.add_parser('report')
    report.add_argument('--persona',required=True)
    report.add_argument('--actor',required=True,choices=('opencode','antigravity','cli','other'))
    report.add_argument('--step-id',required=True)
    report.add_argument('--parent-step-id')
    report.add_argument('--operation',required=True)
    report.add_argument('--status',required=True,choices=('RUNNING','SUCCESS','PARTIAL','BLOCKED','FAILED'))
    report.add_argument('--artifact-root',help='The local outputs/<run-id> directory')
    report.add_argument('--artifact',help='Relative path inside artifact-root')
    report.add_argument('--event-id',default=None,help='Stable identifier for retries')
    sub.add_parser('replay')
    args=parser.parse_args(argv)
    if args.command=='replay':
        failed=0
        for path in sorted(Path(args.spool).glob('*.json')):
            try:
                if path.is_symlink() or path.stat().st_size>8192:raise ValueError('Invalid spool item')
                event=json.loads(path.read_text(encoding='utf-8'))
                if event.get('run_id')!=args.run_id:continue
                send(args.server,args.run_id,args.token_file,event)
                path.unlink()
            except (OSError,ValueError,urllib.error.URLError):failed+=1
        print(json.dumps({'replay_failures':failed}));return 3 if failed else 0
    event={'schema_version':SCHEMA,'event_id':args.event_id or uuid.uuid4().hex,'run_id':args.run_id,
           'step_id':args.step_id,'persona':args.persona,'actor':args.actor,'operation':args.operation,'status':args.status}
    if args.parent_step_id:event['parent_step_id']=args.parent_step_id
    if args.artifact:
        if not args.artifact_root:parser.error('--artifact requires --artifact-root')
        relative=Path(args.artifact)
        if relative.is_absolute() or '..' in relative.parts:parser.error('Artifact must be relative')
        root=Path(args.artifact_root).resolve();target=root/relative
        if any((root.joinpath(*relative.parts[:n])).is_symlink() for n in range(1,len(relative.parts)+1)) or not target.is_file():
            parser.error('Artifact unavailable or is a symlink')
        h=hashlib.sha256()
        with target.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
        event['artifact_ref']={'path':relative.as_posix(),'sha256':h.hexdigest()}
    try:
        result=send(args.server,args.run_id,args.token_file,event)
        print(json.dumps(result));return 0
    except urllib.error.HTTPError as exc:
        if exc.code<500 and exc.code!=429:
            print(json.dumps({'status':'REJECTED','http_status':exc.code}));return 4
    except (OSError,urllib.error.URLError):
        pass
    path=spool_event(args.spool,event)
    print(json.dumps({'status':'SPOOLED','event_id':event['event_id']}));return 3


if __name__=='__main__':
    raise SystemExit(main())
