"""Small, permission-conscious adapters. No login bypass, no broad crawler."""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl
from urllib.robotparser import RobotFileParser
from datetime import date
from pathlib import Path
import hashlib, json, ipaddress, socket, time, re
from defusedxml import ElementTree as ET
import requests
from .common import now_iso, sha256
from .pathfinder_ledger import source_row

from ._version import __version__
UA=f'EPISTARIUM/{__version__} (research; limited requests; respect robots)'
ALLOWED_PROVIDER_HOSTS={
  'worldbank':{'api.worldbank.org'},
  'crossref':{'api.crossref.org'},
  'who':{'ghoapi.azureedge.net'},
  'gdelt':{'api.gdeltproject.org'},
}

class HarvestBlocked(Exception): pass

def public_addresses(host, port=443):
    """Fail closed on mixed public/private DNS answers and resolution failures."""
    try:
        addresses=sorted({r[4][0] for r in socket.getaddrinfo(host,port,type=socket.SOCK_STREAM)})
    except OSError as exc:
        raise HarvestBlocked(tr('DNS tidak dapat diverifikasi')) from exc
    if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):
        raise HarvestBlocked(tr('DNS mengarah ke IP privat/reserved atau tidak memiliki alamat'))
    return addresses


def public_session():
    """Pin each TCP connection to checked public IPs; preserve hostname TLS/SNI."""
    from requests.adapters import HTTPAdapter
    from urllib3.connection import HTTPSConnection
    from urllib3.connectionpool import HTTPSConnectionPool
    from urllib3.exceptions import NewConnectionError

    class PublicConnection(HTTPSConnection):
        def _new_conn(self):
            last=None
            for address in public_addresses(self.host,self.port or 443):
                try:
                    return socket.create_connection((address,self.port or 443),self.timeout,self.source_address)
                except OSError as exc:last=exc
            raise NewConnectionError(self,tr('Koneksi ke IP publik gagal')) from last

    class PublicPool(HTTPSConnectionPool):
        ConnectionCls=PublicConnection

    class PublicAdapter(HTTPAdapter):
        def init_poolmanager(self,*args,**kwargs):
            super().init_poolmanager(*args,**kwargs)
            self.poolmanager.pool_classes_by_scheme=dict(self.poolmanager.pool_classes_by_scheme)
            self.poolmanager.pool_classes_by_scheme['https']=PublicPool

    session=requests.Session()
    session.trust_env=False
    session.mount('https://',PublicAdapter())
    return session


def safe_url(url, *, provider=None, allow_hosts=None, resolve_dns=False):
    p=urlparse(str(url))
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.port not in (None,443):
        raise HarvestBlocked(tr('Hanya URL HTTPS publik tanpa kredensial/port khusus diizinkan'))
    if any(k.casefold() in {'apikey','api_key','token','access_token','secret','password','key','authorization'} for k,v in parse_qsl(p.query,keep_blank_values=True)):
        raise HarvestBlocked(tr('URL memuat parameter kredensial; jangan disimpan ke ledger/log'))
    host=p.hostname.lower().rstrip('.')
    allowed=allow_hosts if allow_hosts is not None else (ALLOWED_PROVIDER_HOSTS.get(provider) if provider else None)
    if allowed is not None and host not in allowed:raise HarvestBlocked(tr('Host tidak sesuai whitelist penyedia'))
    if host in {'localhost','localhost.localdomain'} or host.endswith(('.local','.internal','.localhost')):
        raise HarvestBlocked(tr('Alamat internal tidak boleh dipanggil'))
    try:
        ip=ipaddress.ip_address(host)
        if not ip.is_global:raise HarvestBlocked(tr('IP privat/reserved ditolak'))
    except ValueError:pass
    if resolve_dns:public_addresses(host)
    return url

class LimitedClient:
    def __init__(self, *, session=None, timeout=7, max_requests=6, retry=1, backoff=0.2, cache_dir=None,
                 allowed_hosts=None, robots_checker=None, max_bytes=2_000_000, cache_ttl_seconds=86400,
                 user_agent=None):
        self.session=session if session is not None else public_session();self.timeout=timeout;self.max_requests=max_requests
        self.retry=min(max(0,int(retry)),2);self.backoff=max(0,min(float(backoff),2));self.count=0
        self.cache_dir=Path(cache_dir) if cache_dir else None;self.allowed_hosts=allowed_hosts
        self.robots_checker=robots_checker;self.max_bytes=max_bytes;self.cache_ttl_seconds=cache_ttl_seconds
        self.user_agent=user_agent or UA
        if any(c in self.user_agent for c in ('\r','\n')):raise ValueError(tr('User-Agent tidak valid'))
    def _read_bounded(self,response):
        chunks=[];size=0
        for chunk in response.iter_content(chunk_size=65536):
            size+=len(chunk)
            if size>self.max_bytes:raise HarvestBlocked(tr('Ukuran respons melewati batas aman'))
            chunks.append(chunk)
        return b''.join(chunks)
    @staticmethod
    def _close(response):
        close=getattr(response,'close',None)
        if close:close()
    def _robots_allowed(self,url):
        if self.robots_checker is not None:return bool(self.robots_checker(url,self.user_agent))
        # Explicit robot check, no aggressive crawling on failure.
        p=urlparse(url);robot_url=f'{p.scheme}://{p.netloc}/robots.txt'
        if self.count>=self.max_requests:raise HarvestBlocked(tr('Kuota request habis sebelum robots.txt'))
        self.count+=1
        try:
            safe_url(robot_url)
            r=self.session.get(robot_url,timeout=self.timeout,headers={'User-Agent':self.user_agent},allow_redirects=False,stream=True)
            try:
                if r.status_code==404:return True
                if r.status_code!=200:raise HarvestBlocked(tr('Robots tidak dapat dipastikan: HTTP {v0}',v0=f'{r.status_code}'))
                raw=self._read_bounded(r)
                rp=RobotFileParser();rp.parse(raw.decode('utf8',errors='replace').splitlines())
                return rp.can_fetch(self.user_agent,url)
            finally:self._close(r)
        except requests.RequestException as ex:raise HarvestBlocked(tr('Robots tidak dapat diperiksa: ')+type(ex).__name__) from ex
    def get(self,url,*,provider=None,robots=False):
        safe_url(url,provider=provider,allow_hosts=self.allowed_hosts)
        if robots and not self._robots_allowed(url):raise HarvestBlocked(tr('robots.txt melarang akses sumber'))
        key=hashlib.sha256(url.encode()).hexdigest()
        if self.cache_dir:
            cache=self.cache_dir/(key+'.json')
            if cache.is_file() and time.time()-cache.stat().st_mtime<=self.cache_ttl_seconds:
                if cache.stat().st_size>self.max_bytes:raise HarvestBlocked(tr('Ukuran cache melewati batas aman'))
                return cache.read_bytes(),{'cache':True,'status_code':200,'url':url,'hash':sha256(cache),'requests':0}
        if self.count>=self.max_requests:raise HarvestBlocked(tr('Kuota request telah tercapai'))
        for attempt in range(self.retry+1):
            if self.count>=self.max_requests:raise HarvestBlocked(tr('Kuota request habis pada retry'))
            self.count+=1
            res=None
            try:
                res=self.session.get(url,timeout=self.timeout,headers={'User-Agent':self.user_agent,'Accept':'application/json, application/rss+xml, application/xml'},allow_redirects=False,stream=True)
                if res.status_code in (301,302,303,307,308):raise HarvestBlocked(tr('Redirect tidak diikuti otomatis demi keamanan host/izin'))
                if res.status_code in (401,403,429):raise HarvestBlocked('HTTP '+str(res.status_code)+tr('; akses, kuota atau izin memerlukan pemeriksaan'))
                if res.status_code in (500,502,503,504) and attempt<self.retry:
                    if self.count>=self.max_requests:break
                    if self.backoff:time.sleep(self.backoff*(attempt+1))
                    continue
                res.raise_for_status()
                raw=self._read_bounded(res)
                if self.cache_dir:
                    self.cache_dir.mkdir(parents=True,exist_ok=True)
                    cache.write_bytes(raw)
                return raw,{'cache':False,'status_code':res.status_code,'url':url,'hash':hashlib.sha256(raw).hexdigest(),'requests':attempt+1}
            except requests.RequestException as ex:
                if attempt==self.retry:raise HarvestBlocked(tr('Akses gagal: ')+type(ex).__name__) from ex
                if self.backoff:time.sleep(self.backoff*(attempt+1))
            finally:
                if res is not None:self._close(res)
        raise HarvestBlocked(tr('Batas retry/kuota tercapai'))

def worldbank_url(indicator,country,start_year,end_year):
    if not re.fullmatch(r'[A-Z0-9.]{4,32}',indicator):raise ValueError(tr('Kode indikator World Bank tidak valid'))
    if not re.fullmatch(r'[A-Z]{2,3}',country):raise ValueError(tr('Kode negara tidak valid'))
    return f'https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?'+urlencode({'format':'json','date':f'{start_year}:{end_year}','per_page':100})

def worldbank_from_payload(payload,*,indicator,country,source_url,observed_at=None):
    if isinstance(payload,(bytes,str)):payload=json.loads(payload)
    if not isinstance(payload,list) or len(payload)<2 or not isinstance(payload[1],list):
        raise ValueError(tr('World Bank JSON tidak sesuai struktur API V2'))
    out=[]
    for x in payload[1]:
        if not isinstance(x,dict) or not str(x.get('date','')).isdigit() or x.get('value') is None:continue
        val=x['value']
        if isinstance(val,bool) or not isinstance(val,(int,float)):continue
        indic=x.get('indicator') or {};ct=x.get('country') or {}
        out.append({'jenis_data':'statistik resmi','kelompok_bukti':'statistik resmi atau survei probabilitas',
            'indikator':indic.get('value') or indicator,'definisi_operasional':None,
            'nilai':val,'satuan':None,'organisasi_penerbit':'World Bank','produsen_asli':None,
            'judul_sumber':indic.get('value') or indicator,'url':source_url,
            'periode_referensi':str(x['date']),'tanggal_observasi':None,'tanggal_publikasi':None,
            'geografi':ct.get('value') or country,'populasi':None,'unit_analisis':'negara/tahun',
            'level_estimasi':'nasional','tipe_akses':'API publik','lisensi':None,
            'status_verifikasi':'belum dapat diverifikasi',
            'batas_generalisasi':tr('Indikator level negara, bukan estimasi kasus lokal; metadata indikator dan sumber primer perlu diverifikasi.'),
            'cuplikan':None,'lokasi_bukti':f'World Bank API item date={x["date"]}',
            'kaitan_klaim':None,'asal_record':'worldbank_api','tanggal_pengambilan':observed_at})
    return out

def rss_from_payload(payload,source_url):
    if isinstance(payload,bytes):root=ET.fromstring(payload)
    else:root=ET.fromstring(payload.encode())
    entries=root.findall('.//item')
    if not entries:entries=root.findall('.//{http://www.w3.org/2005/Atom}entry')
    items=[]
    for e in entries[:30]:
        def x(name):
            t=e.findtext(name) or e.findtext('{http://www.w3.org/2005/Atom}'+name)
            return (t or '').strip()[:1000]
        link=x('link')
        if not link:
            ln=e.find('{http://www.w3.org/2005/Atom}link')
            if ln is not None:link=ln.get('href','')
        items.append({'title':x('title'),'link':link,'published':x('pubDate') or x('published'),
            'summary':x('description') or x('summary'),'source':source_url,'level':tr('berita/dokumen; bukan frekuensi kejadian')})
    return items

def discover_plan(idea,*,country='IDN'):
    lower=idea.casefold();rows=[]
    rows.append({'provider':'Crossref','source_type':'academic_metadata','plan':tr('lakukan Liora melalui FULL mode atau opsi eksplisit'),'status':'NOT_RUN'})
    if any(x in lower for x in ('internet','digital','online','akses internet','internet access')):
        rows.append({'provider':'World Bank','source_type':'official_statistics','indicator':'IT.NET.USER.ZS','country':country,
                     'plan':tr('indikator pengguna internet (%) sebagai konteks nasional, bukan ukuran kasus lokal'),'status':'NOT_RUN'})
    if any(x in lower for x in ('penduduk','populasi','population')):
        rows.append({'provider':'World Bank','source_type':'official_statistics','indicator':'SP.POP.TOTL','country':country,
                     'plan':tr('indikator jumlah penduduk nasional; periksa kesesuaian unit'),'status':'NOT_RUN'})
    rows.extend([
        {'provider':'BPS WebAPI','source_type':'official_statistics','status':'NOT_RUN','plan':tr('registrasi pengguna wajib; pilih tabel/indikator secara manual')},
        {'provider':'Satu Data Indonesia','source_type':'dataset','status':'NOT_RUN','plan':tr('pilih dataset berizin sesuai domain; validasi metadata')},
        {'provider':'WHO GHO','source_type':'official_statistics','status':'NOT_RUN','plan':tr('aktifkan adapter saat indikator kesehatan ditetapkan')},
        {'provider':'GDELT','source_type':'news_coverage','status':'NOT_RUN','plan':tr('rekam publikasi berita, bukan hitungan kejadian')},
        {'provider':'Google Trends','source_type':'relative_index','status':'NOT_RUN','plan':tr('indikator relatif 0-100; akses tunduk kebijakan provider')},
    ])
    return rows
