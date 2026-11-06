"""Loopback-only monitoring HTTP server; minimal dependencies, no third-party frontend."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs,quote,unquote
from pathlib import Path
from importlib.resources import files
from threading import Thread
from secrets import token_urlsafe
from collections import defaultdict, deque
from secrets import compare_digest
from .store import ObservatoryStore
from .runner import ObservatoryRunner
from .bridge import authorized as agent_authorized, ingest as ingest_agent_event
from .._version import __version__
import json
import mimetypes
import re
import time

SAFE_ASSET={'index.html','app.js','style.css'}
ID_RE=re.compile(r'^[0-9a-f]{32}$')

class ObservatoryServer(ThreadingHTTPServer):
    daemon_threads=True
    allow_reuse_address=True
    def __init__(self,root,port=4782,review_secret=None):
        self.store=ObservatoryStore(root)
        self.runner=ObservatoryRunner(self.store)
        self.token=token_urlsafe(32)
        if review_secret is not None and (not isinstance(review_secret,str) or not 12<=len(review_secret)<=256):
            raise ValueError('Review passphrase must contain 12 to 256 characters')
        self.review_secret=review_secret
        self.agent_rate=defaultdict(deque)
        super().__init__(('127.0.0.1',int(port)),ObservatoryHandler)

class ObservatoryHandler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    server_version='EPISTARIUMObservatory/0.9'
    def log_message(self,fmt,*args):
        # Do not print access paths, approval tokens or private research terms.
        return

    def _origin_host(self):
        host=self.headers.get('Host','').lower().strip()
        port=str(self.server.server_port)
        if host not in ('127.0.0.1:'+port,'localhost:'+port):return False
        origin=self.headers.get('Origin')
        return origin in (None,'http://127.0.0.1:'+port,'http://localhost:'+port)

    def _json(self,payload,status=200):
        data=json.dumps(payload,ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Length',str(len(data)))
        self.end_headers();self.wfile.write(data)

    def _error(self,status,message):
        self._json({'error':message},status)

    def _authorized(self):
        return compare_digest(self.headers.get('X-Observatory-Token','').encode('utf-8'),self.server.token.encode('utf-8'))

    def _segments(self):
        path=urlparse(self.path).path
        try:
            decoded=unquote(path,errors='strict')
            if any(c in decoded for c in ('\\','\0')):return []
            return [s for s in decoded.split('/') if s]
        except UnicodeError:
            return []

    def _serve_static(self,name):
        if name not in SAFE_ASSET:return self._error(404,'Not found')
        data=files('epistarium.observatory').joinpath('static',name).read_bytes()
        mime={'index.html':'text/html','style.css':'text/css','app.js':'application/javascript'}[name]
        self.send_response(200)
        self.send_header('Content-Type',mime+'; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-cache')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('X-Frame-Options','DENY')
        self.end_headers();self.wfile.write(data)

    def do_GET(self):
        if not self._origin_host():return self._error(403,'Loopback origin only')
        seg=self._segments();q=parse_qs(urlparse(self.path).query)
        try:
            if not seg or seg==['index.html']:return self._serve_static('index.html')
            if len(seg)==1 and seg[0] in SAFE_ASSET:return self._serve_static(seg[0])
            if seg==['api','health']:return self._json({'status':'ok','service':'EPISTARIUM Observatory','version':__version__})
            if seg==['api','boot']:
                return self._json({'token':self.server.token,'default_language':'en','default_theme':'dark','personas':list(self.server.store.get(q.get('run',[''])[0])['personas']) if q.get('run') and ID_RE.fullmatch(q['run'][0]) else list(__import__('epistarium.observatory.store',fromlist=['PERSONAS']).PERSONAS)})
            if len(seg)==4 and seg[:2]==['api','runs'] and ID_RE.fullmatch(seg[2]) and seg[3]=='events':
                if q.get('token',[''])[0]!=self.server.token:return self._error(403,'Invalid event token')
                return self._stream(seg[2])
            if not self._authorized():return self._error(403,'Invalid session token')
            if seg==['api','runs']:return self._json({'runs':self.server.store.list()})
            if len(seg)>=3 and seg[:2]==['api','runs'] and ID_RE.fullmatch(seg[2]):
                run_id=seg[2]
                if len(seg)==3:
                    state=self.server.store.get(run_id)
                    state={k:v for k,v in state.items() if k not in ('fixture','config')}
                    state['agent_reported_personas']=self.server.store.agent_reports(run_id)
                    return self._json({'run':state,'evidence':self.server.store.evidence_summary(run_id),
                                       'artifacts':self.server.store.artifacts(run_id),
                                       'recent_events':self.server.store.events(run_id)[-30:]})
                if len(seg)==4 and seg[3]=='history':return self._json({'events':self.server.store.events(run_id)})
                if len(seg)==4 and seg[3]=='preview':
                    name=q.get('path',[''])[0]
                    return self._json({'path':name,'text':self.server.store.artifact_text(run_id,name)})
            return self._error(404,'Not found')
        except (FileNotFoundError,ValueError):return self._error(404,'Unavailable run or artifact')

    def _stream(self,run_id):
        self.server.store._dir(run_id)
        try:
            cursor=int(self.headers.get('Last-Event-ID','0'))
        except ValueError:cursor=0
        cursor=max(0,cursor)
        self.send_response(200)
        self.send_header('Content-Type','text/event-stream; charset=utf-8')
        self.send_header('Cache-Control','no-cache, no-transform')
        self.send_header('Connection','keep-alive')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        try:
            while True:
                count=self.server.store.event_count(run_id)
                cursor=min(cursor,count)
                if count>cursor:
                    cursor=count
                    self.wfile.write(f'id: {cursor}\nevent: changed\ndata: {json.dumps({"count":cursor})}\n\n'.encode('utf-8'))
                else:
                    self.wfile.write(b': heartbeat\n\n')
                self.wfile.flush()
                self.server.store.wait(run_id,5)
        except (BrokenPipeError,ConnectionResetError,OSError):
            return

    def do_POST(self):
        if not self._origin_host():return self._error(403,'Loopback origin only')
        seg=self._segments()
        agent_route=(len(seg)==5 and seg[:2]==['api','runs'] and ID_RE.fullmatch(seg[2]) and seg[3:]==['events','agent'])
        if agent_route:
            if not agent_authorized(self.server.store,seg[2],self.headers.get('X-Agent-Token','')):
                return self._error(403,'Invalid run capability')
            with self.server.store.lock:
                queue=self.server.agent_rate[seg[2]]
                now=time.monotonic()
                while queue and queue[0]<now-60:queue.popleft()
                if len(queue)>=120:return self._error(429,'Event rate exceeded')
                queue.append(now)
        elif not self._authorized():return self._error(403,'Invalid session token')
        if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':return self._error(415,'JSON required')
        try:
            size=int(self.headers.get('Content-Length','0'))
        except ValueError:
            return self._error(400,'Invalid length')
        if not 0<size<=(8192 if agent_route else 32_768):
            self.close_connection=True
            return self._error(413,'Body exceeds permitted size')
        try:
            payload=json.loads(self.rfile.read(size))
            if not isinstance(payload,dict):raise ValueError('Expected a JSON object')
            if agent_route:
                result=ingest_agent_event(self.server.store,seg[2],payload)
                return self._json(result,200 if result['duplicate'] else 201)
            if seg==['api','runs']:
                # Browser UI intentionally disallows arbitrary filesystem fixture/config
                # references and online requests; CLI can explicitly allow those.
                if any(k in payload for k in ('fixture','config','online')):raise ValueError('Use CLI for fixture, config and online operations')
                state=self.server.store.create(payload.get('idea',''),payload.get('mode','pathfind'),
                                               language=payload.get('language','en'))
                self.server.runner.launch(state['id'])
                return self._json({'run_id':state['id']},201)
            if len(seg)==4 and seg[:2]==['api','runs'] and ID_RE.fullmatch(seg[2]) and seg[3]=='decide':
                secret=payload.pop('review_secret',None)
                if (not self.server.review_secret or not isinstance(secret,str) or len(secret)>256 or
                        not compare_digest(secret.encode('utf-8'),self.server.review_secret.encode('utf-8'))):
                    return self._error(403,'Review passphrase required')
                result=self.server.runner.decide(seg[2],payload.get('decision'),payload.get('reason',''))
                return self._json({'run_id':result['id'],'status':result['status']})
            return self._error(404,'Unknown endpoint')
        except (ValueError,TypeError) as exc:return self._error(400,str(exc)[:170])
        except FileNotFoundError:return self._error(404,'Run not found')


def serve(root,port=4782,open_browser=False,initial_run=None):
    import sys
    secret=None
    if sys.stdin.isatty():
        import getpass
        secret=getpass.getpass('Set a private review passphrase (12+ characters; blank disables approvals): ')
        if secret and not 12<=len(secret)<=256:raise ValueError('Review passphrase must contain 12 to 256 characters')
        secret=secret or None
    if not secret:print('Review approvals disabled for this session; restart in a terminal to set a passphrase.',flush=True)
    server=ObservatoryServer(root,port,review_secret=secret)
    if initial_run:
        state=server.store.create(**initial_run)
        if state['status']=='QUEUED':server.runner.launch(state['id'])
        selected_id=state['id']
    else:selected_id=None
    endpoint=f'http://127.0.0.1:{server.server_port}/'
    if selected_id:endpoint+='?run='+selected_id
    if open_browser:
        import webbrowser
        webbrowser.open(endpoint)
    print('EPISTARIUM Observatory at '+endpoint,flush=True)
    print('Loopback only. Press Ctrl+C to stop.',flush=True)
    try:server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:pass
    finally:server.server_close()
    return 0
