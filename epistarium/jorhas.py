"""Jorhas: conservative orchestration with real step records. No autonomous LLM browsing."""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language, normalize_aliases, ORIGO_ALIASES, display_issue_codes, column_labels
import csv, json, os, platform, re, sys, time
from pathlib import Path
from datetime import date
from urllib.parse import urlparse
from .common import now_iso, save_json, save_csv, sha256, five_years_ago, today, prepare_run_directory, validate_schema, EXECUTION_STATUSES
from .pathfinder_harvest import (LimitedClient, HarvestBlocked, discover_plan, worldbank_url,
                                  worldbank_from_payload, rss_from_payload, safe_url)
from .pathfinder_ledger import (SCHEMA, FIELDS, SOURCE_FIELDS, normalize_record,
                                 source_row, deduplicate_sources, audit_aggregates, reconcile_sources)
from .outcomes import assess_stage

from ._version import __version__ as VERSION
RUN_STATES=EXECUTION_STATUSES


def _safe_idea(text):
    if not isinstance(text,str) or len(text.strip())<3:raise ValueError(tr('Masukkan ide/topik minimal 3 karakter'))
    if len(text)>1000:raise ValueError(tr('Panjang ide maksimal 1000 karakter'))
    return text.strip()


def _step(log,name,status,command,inputs=None,outputs=None,reason=None,seconds=None):
    if status not in RUN_STATES:raise ValueError(tr('Status eksekusi tidak dikenal'))
    row={'step':name,'status':status,'command':command,'inputs':[], 'outputs':[],
         'started_or_recorded_at':now_iso(),'duration_seconds':seconds,'reason':reason,
         'cost':None,'quota':None,'model_called':False}
    for p in inputs or []:
        if p and Path(p).is_file():row['inputs'].append({'path':str(p),'sha256':sha256(p)})
    for p in outputs or []:
        if p and Path(p).is_file():row['outputs'].append({'path':str(p),'sha256':sha256(p)})
    log.append(row);return row


def _report(path,idea,start,end,sources,records,opportunities,summary,missing):
    is_synthetic=summary['synthetic_count']>0
    lines=['# EPISTARIUM | Jorhas Path Finding Report','',
        tr('**SIMULASI: DATA SINTETIS, BUKAN BUKTI PENELITIAN**') if is_synthetic else tr('**Laporan eksplorasi awal, belum menjadi klaim ilmiah final.**'),'',
        tr('Ide awal: {v0}',v0=f'{idea}'), tr('Jendela fenomena default: {v0} sampai {v1} (bergulir tepat lima tahun).',v0=f'{start}', v1=f'{end}'),
        tr('Rekaman data: {v0}; sumber dicatat: {v1}; status verifikasi tidak diketahui: {v2}.',v0=f'{len(records)}', v1=f'{len(sources)}', v2=f"{summary['unknown_verification_count']}"),'',
        tr('## Lingkup dan bukti'),'',
        tr('Hanya sumber yang tercantum di SOURCE_LEDGER yang dicoba/diolah. Tanpa sumber yang berhasil diperiksa, tidak ada dukungan empiris otomatis.'),'',
        tr('## Rekaman data (bukan simpulan)'),'']
    if records:
        for r in records[:30]:
            v=tr('tidak tersedia') if r['nilai'] is None else str(r['nilai'])
            lines.append(tr('- {v0} | {v1} | nilai {v2} {v3}; periode {v4}; geografi {v5}; status {v6}; isu: {v7}.',v0=f"{r['record_id']}", v1=f"{r['indikator'] or tr('indikator belum didefinisikan')}", v2=f'{v}', v3=f"{r['satuan'] or tr('(unit belum diketahui)')}", v4=f"{r['periode_referensi'] or tr('belum diketahui')}", v5=f"{r['geografi'] or tr('belum diketahui')}", v6=f"{display_status(r['status_verifikasi'])}", v7=f"{display_issue_codes(r['issue_codes']) or tr('butuh penilaian manusia')}"))
    else:lines.append(tr('- Tidak ada data empiris yang berhasil diperoleh melalui sumber yang dijalankan. Ini tidak membuktikan fenomena tidak ada.'))
    lines+=['',tr('Lokasi pada sumber belum menetapkan lokasi penelitian.'),'']
    lines+=['',tr('## Tiga peluang fokus (bukan tiga temuan)'),'']
    for o in opportunities:
        lines.append(tr('- **{v0}: {v1}**. Unit: {v2}; opsi metode: {v3}; bukti: {v4}. Kebutuhan: {v5}.',v0=f"{o['id']}", v1=f"{o['judul_sementara']}", v2=f"{o['unit']}", v3=f"{o['metode_opsi']}", v4=f"{display_status(o['status_bukti'])}", v5=f"{o['syarat_kelayakan']}"))
    lines+=['',tr('## Kesalahan, keterbatasan, dan data yang belum tersedia'),'']
    lines+=['- '+x for x in missing]
    lines+=['',tr('## Pemeriksaan metodologis'),'',
           tr('- Statistik nasional tidak dapat digunakan sebagai ukuran dampak satu kasus lokal.'),
           tr('- Survei nonprobabilitas tidak secara otomatis mewakili populasi nasional.'),
           tr('- Google Trends adalah indeks relatif, GDELT adalah cakupan berita; keduanya bukan data prevalensi atau jumlah kejadian.'),
           tr('- Research gap dan novelty memerlukan penelusuran literatur sistematis dan audit manusia; belum ditetapkan otomatis.'),
           tr('- Hasil pengolahan mekanis tidak menggantikan interpretasi disipliner.')]
    path.write_text('\n'.join(lines)+'\n',encoding='utf8')


def _opportunities(idea,records):
    tags=[tr('pola dan perkembangan'),tr('pemaknaan aktor'),tr('respons dan keputusan organisasi')]
    methods=[tr('analisis dokumen atau jejak digital yang diizinkan'),tr('wawancara kualitatif dengan persetujuan'),
             tr('studi kasus dan analisis dokumen organisasi yang berizin')]
    units=[tr('dokumen atau peristiwa yang terlacak'),tr('partisipan yang ditetapkan purposif'),tr('organisasi atau unit kasus yang mempunyai akses sah')]
    context={'indikator':sorted({r['indikator'] for r in records if r.get('indikator')}),
             'geografi':sorted({r['geografi'] for r in records if r.get('geografi')}),
             'periode':sorted({r['periode_referensi'] for r in records if r.get('periode_referensi')}),
             'issue_codes':sorted({c for r in records for c in r.get('issue_codes',[])})}
    out=[]
    for i,(tag,method,unit) in enumerate(zip(tags,methods,units),1):
        out.append({'id':f'OP{i:02}', 'fokus':tag,
           'judul_sementara':tr('{v0} terkait {v1}',v0=f'{tag.title()}', v1=f'{idea}')+(tr(' di {v0}',v0=f"{', '.join(context['geografi'][:3])}") if context['geografi'] else ''),
           'generation_method':'ledger_contextual_scaffold' if records else 'scaffold_template', 'ledger_context':context, 'unit':unit,'metode_opsi':method,
           'status_bukti':'hipotesis atau rekomendasi',
           'bukti_terkait':[r['record_id'] for r in records if not r.get('synthetic')][:10],
           'akses_data':'belum dapat diverifikasi','teori':tr('perlu kajian primer yang sesuai'),
           'etika':tr('perlu pemeriksaan izin, privasi, dan dampak terhadap subjek'),
           'syarat_kelayakan':tr('Konfirmasi bukti fenomena, pertanyaan ilmiah, unit analisis, periode, kecocokan teori, dan akses data.'),
           'keputusan_manusia':'PENDING','penilaian':'BELUM_MEMADAI_UNTUK_RANKING'})
    return out


@localized
def pathfind(idea,out_dir,*,fixture=None,config=None,as_of=None,timezone='Asia/Jakarta',allow_live=False,client=None):
    """Path Finding actual execution. An offline fixture is always marked synthetic."""
    idea=_safe_idea(idea); cfg=config or {}
    if not isinstance(cfg,dict):raise ValueError(tr('config harus objek JSON'))
    out=prepare_run_directory(out_dir)
    end=date.fromisoformat(as_of) if as_of else today(timezone)
    start=five_years_ago(end)
    start_clock=time.monotonic();sources=[];records=[];log=[];missing=[]
    plan=discover_plan(idea,country=cfg.get('country','IDN'))
    save_json(out/'SOURCE_PLAN.json',{'schema':'epistarium.pathfinder.source_plan.v1','idea':idea,'start':start.isoformat(),
              'end':end.isoformat(),'sources':plan,'automatic_discovery_exhaustive':False})
    for i,p in enumerate(plan,1):
        sources.append(source_row({'source_id':f'PLAN{i:02}','provider':p['provider'],'title':p.get('plan'),
            'source_type':p.get('source_type'),'execution_status':'NOT_RUN','access_status':'not_attempted',
            'notes':tr('Sumber kandidat, tidak otomatis dimintai data; ')+p.get('plan',''),'synthetic':False}))
    _step(log,'source_discovery','SUCCESS','discover_plan(idea)',outputs=[out/'SOURCE_PLAN.json'])
    if fixture:
        path=Path(fixture); f=json.loads(path.read_text('utf8'))
        if not isinstance(f,dict):raise ValueError(tr('Fixture harus objek JSON'))
        for i,r in enumerate(f.get('records') or [],1):
            rr=dict(r);rr['file_sha256']=rr.get('file_sha256') or sha256(path)
            rr['asal_record']='fixture_synthetic';records.append(normalize_record(rr,i,observed_on=now_iso(),synthetic=True))
        for i,s in enumerate(f.get('sources') or [],1):
            src={**s,'source_id':s.get('source_id',f'FIX{i:02}'),'execution_status':'SUCCESS',
                 'access_status':'local_fixture','synthetic':True,'sha256':sha256(path),
                 'notes':tr('FIxture sintetis. Tidak ada jaringan atau verifikasi sumber live.')}
            sources.append(source_row(src))
        _step(log,'fixture_ingest','SUCCESS','read_local_fixture',inputs=[fixture],
              reason=tr('Data tes sintetis; bukan pengambilan empiris'))
    else:
        _step(log,'fixture_ingest','NOT_RUN','read_local_fixture',reason=tr('Tanpa fixture'))
    tasks=cfg.get('sources') or []
    if not isinstance(tasks,list):raise ValueError(tr('config.sources harus array'))
    if any(not isinstance(t,dict) for t in tasks):raise ValueError(tr('Setiap config.sources harus objek JSON'))
    http=client or LimitedClient(cache_dir=cfg.get('cache_dir'),max_requests=int(cfg.get('max_requests',5)),
                                 timeout=float(cfg.get('timeout_seconds',7)))
    for i,t in enumerate(tasks,1):
        name=str(t.get('provider','unknown')).lower();label='harvest_'+name+'_'+str(i);ts=now_iso();t0=time.monotonic()
        row=source_row({'source_id':f'ACTIVE{i:02}','provider':name,'title':t.get('title') or name,
           'url':t.get('url'),'source_type':t.get('source_type'),
           'execution_status':'NOT_RUN','access_status':'not_attempted','attempted_at':None,
           'query':str(t.get('indicator') or idea)[:200]})
        if name!='local_csv' and not allow_live:
            row.update(execution_status='NOT_RUN',failure_reason=tr('Live harvesting tidak diizinkan (--online tidak aktif)'))
            sources.append(row);_step(log,label,'NOT_RUN',name,reason=row['failure_reason']);continue
        record_offset=len(records)
        try:
            if name=='local_csv':
                path=Path(t['path']);max_size=int(t.get('max_bytes',2_000_000))
                if not path.is_file() or path.stat().st_size>max_size:raise HarvestBlocked(tr('File CSV tidak tersedia atau melampaui batas ukuran'))
                if t.get('rights_confirmed') is not True:raise HarvestBlocked(tr('Hak pengolahan berkas belum dikonfirmasi'))
                with path.open('r',encoding='utf-8-sig',newline='') as f:
                    reader=csv.DictReader(f)
                    if not reader.fieldnames:raise HarvestBlocked(tr('CSV tidak memiliki header'))
                    for j,rawrow in enumerate(reader):
                        if j>=int(t.get('max_rows',1000)):break
                        source_mapping=t.get('field_mapping') or {}
                        fields={k:rawrow.get(source_mapping.get(k,k)) for k in ['indikator','nilai','satuan','periode_referensi','geografi','populasi','definisi_operasional','metode_sampling']}
                        val=fields.get('nilai')
                        if val not in (None,''):
                            try:fields['nilai']=float(str(val).replace(',','.'))
                            except ValueError:fields['nilai']=val
                        fields['nilai_raw']=val
                        fields.update({'jenis_data':t.get('jenis_data','dataset'), 'organisasi_penerbit':t.get('organization'),
                              'judul_sumber':t.get('title'), 'url':t.get('url'),'file_sha256':sha256(path),
                              'tipe_akses':tr('file milik pengguna'), 'lisensi':t.get('license'),
                              'metode_pengumpulan':t.get('collection_method'),'asal_record':'local_csv'})
                        records.append(normalize_record(fields,len(records)+1,observed_on=now_iso(),synthetic=t.get('synthetic',False)))
                row.update(execution_status='SUCCESS',access_status='local_file_authorized',sha256=sha256(path),retrieved_at=now_iso(),
                           notes=tr('CSV diproses; kebenaran metode dan isi masih perlu audit'))
            elif name=='worldbank':
                url=worldbank_url(t['indicator'],t.get('country','IDN'),start.year,end.year)
                raw,meta=http.get(url,provider='worldbank')
                parsed=worldbank_from_payload(raw,indicator=t['indicator'],country=t.get('country','IDN'),
                                               source_url=url,observed_at=now_iso())
                for p in parsed:records.append(normalize_record(p,len(records)+1))
                row.update(url=url,execution_status='SUCCESS',access_status='api_responded',response_code=meta['status_code'],sha256=meta['hash'],retrieved_at=now_iso(),rights='metadata only; terms and reuse must be checked',notes=f'{len(parsed)} records; full metadata still pending')
            elif name=='rss':
                if t.get('terms_reviewed') is not True or t.get('rights_confirmed') is not True:
                    raise HarvestBlocked(tr('RSS memerlukan pemeriksaan syarat penggunaan secara manual sebelum fetching'))
                url=t['url'];safe_url(url,allow_hosts={urlparse(url).hostname})
                raw,meta=http.get(url,robots=True)
                feed=rss_from_payload(raw,url)
                # No assumption: each news article is a real event. News entries are source records only.
                for j,e in enumerate(feed,1):
                    sources.append(source_row({'source_id':f'NEWS{i:02}-{j:03}','provider':'rss','title':e['title'],
                        'url':e['link'] or url,'source_type':'news_article','execution_status':'PARTIAL',
                        'access_status':'rss_metadata_only','evidence_level':tr('berita belum diverifikasi'),'retrieved_at':now_iso(),
                        'notes':tr('Teks feed tidak dipromosikan menjadi fakta peristiwa; potensi sindikasi.')}))
                row.update(url=url,execution_status='SUCCESS',access_status='rss_metadata',response_code=meta['status_code'],sha256=meta['hash'],retrieved_at=now_iso(),notes=f'{len(feed)} RSS entries, not event counts')
            else:raise HarvestBlocked(tr('Adapter belum tersedia; sumber hanya ada dalam catalog discovery'))
            for rec in records[record_offset:]:rec['source_id']=row['source_id']
            _step(log,label,'SUCCESS',name,outputs=[],reason=tr('Provider {v0} benar-benar dipanggil',v0=f'{name}'),seconds=round(time.monotonic()-t0,4))
        except (HarvestBlocked,ValueError,KeyError,TypeError,RuntimeError,OSError) as exc:
            row.update(execution_status='BLOCKED',access_status='unavailable',failure_reason=f'{type(exc).__name__}: {str(exc)[:200]}')
            missing.append(f'{name}: {row["failure_reason"]}')
            _step(log,label,'BLOCKED',name,reason=row['failure_reason'],seconds=round(time.monotonic()-t0,4))
        row['attempted_at']=ts if row['execution_status']!='NOT_RUN' else None
        sources.append(row)
    sources,dups=deduplicate_sources(sources)
    records,sources=reconcile_sources(records,sources)
    target_geo=str(cfg.get('target_geography') or '').strip()
    target_pop=str(cfg.get('target_population') or '').strip()
    for rec in records:
        for field,target,code in [('geografi',target_geo,'CAKUPAN_GEOGRAFI_BERBEDA'),('populasi',target_pop,'POPULASI_TIDAK_SAMA')]:
            observed=str(rec.get(field) or '').strip()
            if target and observed and observed.casefold()!=target.casefold():
                rec['issue_codes']=sorted(set(rec['issue_codes']+[code]))
    summary=audit_aggregates(records)
    opportunities=_opportunities(idea,records)
    save_csv(out/'DATA_LEDGER.csv',records,FIELDS)
    save_json(out/'DATA_LEDGER.json',validate_schema({'schema_version':SCHEMA,'records':records,'summary':summary},'pathfinder_data_ledger'))
    save_csv(out/'SOURCE_LEDGER.csv',sources,SOURCE_FIELDS)
    save_json(out/'SOURCE_LEDGER.json',validate_schema({'schema_version':'epistarium.pathfinder.sources.v1','records':sources,'duplicate_source_ids':dups},'pathfinder_sources'))
    events=[]
    for r in records:
        if r.get('tanggal_peristiwa'):
            events.append({'record_id':r['record_id'],'date':r['tanggal_peristiwa'],'actor':r['produsen_asli'],
                           'event':r['indikator'],'geography':r['geografi'],'source':r['url'],'verified':r['status_verifikasi']})
    save_json(out/'PHENOMENON_TIMELINE.json',events)
    save_csv(out/'PHENOMENON_TIMELINE.csv',events,['record_id','date','actor','event','geography','source','verified'])
    save_json(out/'RESEARCH_OPPORTUNITIES.json',{'schema_version':'epistarium.pathfinder.opportunities.v1','records':opportunities})
    if not records:missing.append(tr('Tidak ada rekaman statistik/survei/dokumentasi yang berhasil dikumpulkan oleh adapter yang dijalankan; bukan bukti ketiadaan fenomena.'))
    for x in summary['comparability_issues']:
        detail=(tr('Indikator: {v0}. Field berbeda: {v1}. Rekaman: {v2}. Nilai sumber: {v3}.',
                   v0=x['indikator'],v1=column_labels().get(x['field'],x['field']),
                   v2=', '.join(x['record_ids']),v3=str(x['values'])) if get_language()=='en' else str(x))
        missing.append(tr('Data tidak sebanding: ')+detail)
    if any(r['issue_codes'] for r in records):missing.append(tr('Sebagian rekaman belum memiliki definisi, penyebut, satuan, atau bukti tingkat representativitas yang memadai; lihat issue_codes.'))
    if any(r['synthetic'] for r in records):missing.append(tr('Seluruh data fixture diberi label sintetis; tidak boleh dipakai dalam proposal sebagai hasil empiris.'))
    missing+=[tr('BPS WebAPI memerlukan registrasi; integrasi dan indikator domain khusus NOT_RUN tanpa konfigurasi.'),
              tr('Provenance record belum cukup untuk mengesahkan novelty, prevalensi atau hubungan sebab-akibat.'),
              tr('Tidak ada model bahasa yang dipanggil untuk menyimpulkan temuan; sintesis ilmiah memerlukan peneliti.')]
    (out/'DATA_GAPS.md').write_text(tr('# Kesenjangan data dan akses\n\n')+'\n'.join('- '+x for x in missing)+'\n',encoding='utf8')
    _report(out/'PATH_FINDING_REPORT.md',idea,start.isoformat(),end.isoformat(),sources,records,opportunities,summary,missing)
    for p in ['DATA_LEDGER.csv','DATA_LEDGER.json','SOURCE_LEDGER.csv','SOURCE_LEDGER.json',
              'PHENOMENON_TIMELINE.csv','PHENOMENON_TIMELINE.json','RESEARCH_OPPORTUNITIES.json','DATA_GAPS.md','PATH_FINDING_REPORT.md']:
        _step(log,'artifact_'+p,'SUCCESS','write_artifact',outputs=[out/p])
    any_live=any(s['execution_status']=='SUCCESS' and s['source_id'].startswith('ACTIVE') for s in sources)
    run_status='PARTIAL' if records or any_live else 'BLOCKED'
    _step(log,'pathfinding_result',run_status,'pathfind',reason=tr('Kandidat penelitian belum lolos review semantik dan sumber; capaian empiris terbatas'))
    save_json(out/'RUN_LOG.json',log)
    manifest={'language':get_language(),'schema_version':'epistarium.pathfinder.run.v1','version':VERSION,'mode':'PATH_FINDING',
      'idea':idea,'run_date':end.isoformat(),'timezone':timezone,'phenomenon_start':start.isoformat(),
      'phenomenon_end':end.isoformat(),'status':run_status,'fixture':bool(fixture),'allow_live':bool(allow_live),
      'coverage':tr('Hanya adapter yang dijalankan dan sumber pada ledger, bukan seluruh web.'),
      'retrieval_requests':getattr(http,'count',0),'runtime_seconds':round(time.monotonic()-start_clock,3),
      'python':platform.python_version(),'operating_system':platform.platform(),
      'model_inference':'NOT_RUN','evidence_status':'belum dapat diverifikasi',
      'cost':'unknown / no paid API invoked by built-in adapters',
      'artifacts':{p.name:sha256(p) for p in out.iterdir() if p.is_file() and p.name!='RUN_MANIFEST.json'}}
    save_json(out/'RUN_MANIFEST.json',manifest)
    return {'manifest':manifest,'sources':sources,'records':records,'opportunities':opportunities,'log':log,'directory':str(out)}


@localized
def full_research(idea,out_dir,*,config=None,as_of=None,timezone='Asia/Jakarta',allow_live=False):
    """Invoke real local F1-F3 functions only when input contracts are met."""
    from . import liora,agresa,retho,domares,synthia,vanlan,origo,quilo,huxley
    cfg=config or {}
    if not isinstance(cfg,dict):raise ValueError(tr('config harus objek JSON'))
    cfg=normalize_aliases(cfg,ORIGO_ALIASES)
    if 'synthia_xlsx' in cfg and not isinstance(cfg['synthia_xlsx'],bool):raise ValueError(tr('synthia_xlsx harus boolean'))
    base=prepare_run_directory(out_dir)
    pf=pathfind(idea,base/'path_finding',fixture=cfg.get('pathfinder_fixture'),config=cfg,
                as_of=as_of,timezone=timezone,allow_live=allow_live)
    log=list(pf['log']);statuses={'Path Finding':pf['manifest']['status']}
    paths={};actual={};stage_results={}
    def invoke(name,fn,*,input_files=None):
        t0=time.monotonic()
        try:
            result=fn();actual[name]=result
            outcome=assess_stage(name,result,paths.get(name,[]))
            stage_results[name]=outcome
            status=outcome['execution_status']
            _step(log,name,status,'actual_python_function',inputs=input_files,
                  outputs=[x['path'] for x in outcome['artifacts']],reason='; '.join(outcome['errors']) or None,seconds=round(time.monotonic()-t0,4))
        except Exception as ex:
            status='BLOCKED' if isinstance(ex,(OSError,ValueError,RuntimeError,KeyError)) else 'FAILED'
            stage_results[name]={'execution_status':status,'deliverable_status':'INCOMPLETE',
                'evidence_status':'belum dapat diverifikasi','artifacts':[], 'warnings':[],
                'errors':[type(ex).__name__]}
            _step(log,name,status,'actual_python_function',inputs=input_files,
                  reason=f'{type(ex).__name__}: {str(ex)[:200]}',seconds=round(time.monotonic()-t0,4))
        statuses[name]=status
        return actual.get(name)
    def skip(name,reason):
        stage_results[name]={'execution_status':'NOT_RUN','deliverable_status':'NOT_REQUESTED','evidence_status':'belum dapat diverifikasi','artifacts':[],'warnings':[reason],'errors':[]}
        statuses[name]='NOT_RUN';_step(log,name,'NOT_RUN','not_invoked',reason=reason)
    liora_fixture=cfg.get('liora_fixture')
    if liora_fixture or allow_live:
        paths['Liora']=[base/'liora'/n for n in ('candidates.json','candidates.csv','candidates.ris','search_plan.json')]
        invoke('Liora',lambda:liora.search(idea,base/'liora',scope=cfg.get('literature_scope','empiris'),
                 rows=cfg.get('literature_rows',10),fixture=liora_fixture,
                 as_of=date.fromisoformat(as_of) if as_of else date.fromisoformat(pf['manifest']['run_date']),timezone_name=timezone),
               input_files=[liora_fixture])
    else:skip('Liora',tr('Tidak ada fixture akademik dan live access belum diizinkan'))
    if cfg.get('index_journals') and cfg.get('index_evidence'):
        paths['Agresa']=[base/'agresa'/n for n in ('index_audit.json','index_audit.csv','laporan.md')]
        invoke('Agresa',lambda:agresa.audit(json.loads(Path(cfg['index_journals']).read_text('utf8')),
             json.loads(Path(cfg['index_evidence']).read_text('utf8')),base/'agresa'),
               input_files=[cfg['index_journals'],cfg['index_evidence']])
    else:skip('Agresa',tr('Tidak ada daftar jurnal dan bukti indeks resmi; metadata Liora tidak cukup'))
    if statuses.get('Liora')=='SUCCESS':
        paths['Retho']=[base/'retho'/n for n in ('articles.json','retrieval_report.md')]
        invoke('Retho',lambda:retho.build(json.loads((base/'liora'/'candidates.json').read_text('utf8')),
                 base/'retho',library=json.loads(Path(cfg['retho_library']).read_text('utf8')) if cfg.get('retho_library') else None),
                 input_files=[base/'liora'/'candidates.json',cfg.get('retho_library')])
    else:skip('Retho',tr('Liora tidak menghasilkan kandidat pada run ini'))
    if statuses.get('Retho')=='SUCCESS':
        paths['Domares']=[base/'domares'/n for n in ('critical_readings.json','reading_report.md')]
        invoke('Domares',lambda:domares.analyze(json.loads((base/'retho'/'articles.json').read_text('utf8')),base/'domares'),
               input_files=[base/'retho'/'articles.json'])
    else:skip('Domares',tr('Retho tidak menghasilkan artikel pada run ini'))
    substantive=any(r.get('reading_level')=='machine_fulltext_extracted' for r in (actual.get('Domares') or []))
    if statuses.get('Domares')=='SUCCESS' and substantive:
        paths['Synthia']=[base/'synthia'/n for n in ('database_literatur.json','database_literatur.csv','audit_bukti.csv','sintesis_sementara.md','export_status.json')]
        if cfg.get('synthia_xlsx',False):paths['Synthia'].append(base/'synthia'/'database_literatur.xlsx')
        invoke('Synthia',lambda:synthia.export(actual['Domares'],base/'synthia',xlsx=bool(cfg.get('synthia_xlsx',False))),
               input_files=[base/'domares'/'critical_readings.json'])
    else:skip('Synthia',tr('Tidak ada full-text yang lolos ekstraksi; jangan membuat sintesis dari metadata saja'))
    if cfg.get('vanlan_claims') and cfg.get('vanlan_pdf_dir'):
        paths['Vanlan']=[base/'vanlan'/n for n in ('audit.json','audit.csv','laporan.md')]
        invoke('Vanlan',lambda:vanlan.audit(json.loads(Path(cfg['vanlan_claims']).read_text('utf8')),
                      cfg['vanlan_pdf_dir'],base/'vanlan'),input_files=[cfg['vanlan_claims']])
    else:skip('Vanlan',tr('Tidak ada pasangan klaim dan PDF untuk audit semantik/literal'))
    origo_spec={'ide_awal':idea,'mode':cfg.get('origo_mode','QUICK_MAP'),
                'catatan_pengguna':tr('Bukti Path Finding belum disahkan. Jangan menyatakan novelty terverifikasi.'),
                'akses_data':cfg.get('akses_data') or {}, 'judul_count':3}
    for k in ('teori_pilihan','paradigma','metode_pilihan','pertanyaan_penelitian'):
        if cfg.get(k):origo_spec[k]=cfg[k]
    origo_spec['fenomena']='\n'.join(tr('{v0}: {v1}; periode {v2}; geografi {v3}; status {v4}; sintetis={v5}',v0=f"{r['record_id']}", v1=f"{r.get('indikator') or tr('indikator belum diketahui')}", v2=f"{r.get('periode_referensi') or tr('belum diketahui')}", v3=f"{r.get('geografi') or tr('belum diketahui')}", v4=f"{display_status(r['status_verifikasi'])}", v5=f"{r['synthetic']}") for r in pf['records'][:20])
    origo_spec['provenance_context']={'data_record_ids':[r['record_id'] for r in pf['records']],
        'literature_article_ids':[r.get('article_id') for r in (actual.get('Liora') or [])],
        'evidence_status':'belum dapat diverifikasi','human_review':'PENDING'}
    paths['Ideon ORIGO']=[base/'ideon'/'ideon_origo.json',base/'ideon'/'ringkasan_origo.md']
    invoke('Ideon ORIGO',lambda:origo.export(origo_spec,base/'ideon'))
    if statuses.get('Ideon ORIGO')=='SUCCESS':
        draft=(base/'ideon'/'ringkasan_origo.md').read_text('utf8')
        paths['Quilo']=[base/'quilo'/n for n in ('audit_quilo.json','laporan_quilo.md','usulan_sunting.txt','perubahan.diff')]
        invoke('Quilo',lambda:quilo.audit(draft,base/'quilo'),input_files=[base/'ideon'/'ringkasan_origo.md'])
    else:skip('Quilo',tr('Tidak ada dokumen ORIGO untuk audit editorial'))
    if cfg.get('huxley_docx'):
        paths['Huxley']=[base/'huxley'/n for n in ('huxley_audit.json','sitasi.csv','daftar_pustaka.csv','laporan_huxley.md')]
        invoke('Huxley',lambda:huxley.audit(cfg['huxley_docx'],base/'huxley',annotate=False,online=False),
               input_files=[cfg['huxley_docx']])
    else:skip('Huxley',tr('Belum ada naskah DOCX pengguna; ORIGO bukan artikel final berdaftar pustaka'))
    for name in ['Liora','Agresa','Retho','Domares','Synthia','Vanlan','Ideon ORIGO','Quilo','Huxley']:
        if name not in statuses:skip(name,tr('Ketergantungan belum tersedia'))
    # Shared crosswalk: never infer claim-level support from matching identifiers.
    li_records=(actual.get('Liora') or []) if isinstance(actual.get('Liora'),list) else []
    re_records=(actual.get('Retho') or []) if isinstance(actual.get('Retho'),list) else []
    do_records=(actual.get('Domares') or []) if isinstance(actual.get('Domares'),list) else []
    by_re={r['article_id']:r for r in re_records}
    by_do={r['article_id']:r for r in do_records}
    crosswalk=[]
    for i,r in enumerate(li_records,1):
        doi=str(r.get('doi') or '').casefold();article_id=r['article_id'];re=by_re.get(article_id,{});dr=by_do.get(article_id,{})
        crosswalk.append({'crosswalk_id':f'LW-{i:04d}','article_id':article_id,'doi':doi or None,'title':r.get('title'),
                'liora_level':r.get('available_level'),'liora_origin':r.get('query_url'),
                'retho_article_id':re.get('article_id'),'retho_status':re.get('status'),
                'retho_pdf_sha256':re.get('pdf_sha256'),
                'domares_reading_level':dr.get('reading_level'),'domares_integrity_status':dr.get('integrity_status'),
                'semantic_verified':False,'research_gap_verified':False,'source_type':'academic_metadata'})
    save_json(base/'EVIDENCE_CROSSWALK.json',{'schema_version':'epistarium.jorhas.crosswalk.v1',
        'literature':crosswalk,'pathfinding_sources':[{'source_id':x.get('source_id'),
        'url':x.get('url'),'status':x.get('execution_status')} for x in pf['sources']],
        'linkage_caution':'DOI linkage not evidence of claim support; human review required.'})
    _step(log,'evidence_crosswalk','SUCCESS','write_artifact',outputs=[base/'EVIDENCE_CROSSWALK.json'])
    save_json(base/'FULL_RESEARCH_RUN_LOG.json',log)
    overview={'language':get_language(),'schema_version':'epistarium.jorhas.full.v1','mode':'FULL_RESEARCH','status':'PARTIAL',
       'version':VERSION,'idea':idea,'run_time':now_iso(),'stage_statuses':statuses,'stage_results':stage_results,
       'execution_status':'PARTIAL' if any(s in ('BLOCKED','FAILED','NOT_RUN') for s in statuses.values()) else 'SUCCESS',
       'deliverable_status':'INCOMPLETE' if any(v['deliverable_status']=='INCOMPLETE' for v in stage_results.values()) else 'COMPLETE_FOR_EXECUTED_STAGES',
       'evidence_status':'belum dapat diverifikasi',
       'claims_verification':'NO_AUTOMATIC_PROMOTION',
       'human_approval_required':True,'final_research_findings':'NOT_PRODUCED',
       'model_inference':'NOT_RUN','source_scope':'only recorded adapters/files',
       'stage_status_interpretation':'execution SUCCESS does not imply semantic verification or scientific validation',
       'artifacts':{p.relative_to(base).as_posix():sha256(p) for p in base.rglob('*') if p.is_file() and p.name not in ('FULL_RESEARCH_MANIFEST.json',)},
       'limitations':['ORIGO remains DRAFT_PERLU_REVIEW_MANUSIA','Quilo semantic_validity=NOT_ASSESSED',
         'Huxley MATCHED does not mean claim supported','Full text must be identity/integrity checked before Domares reading',
         'No final scholarly conclusions without human review']}
    # Include the summary in the manifest; hash only this fresh run directory.
    save_json(base/'FULL_RESEARCH_MANIFEST.json',validate_schema(overview,'jorhas_full_manifest'))
    (base/'FULL_RESEARCH_SUMMARY.md').write_text(tr('# Jorhas Full Research | Laporan eksekusi\n\n')+
      tr('**Status: PARTIAL, belum ada hasil penelitian final.**\n\n')+
      '\n'.join(tr('- {v0}: **{v1}**',v0=n,v1=s) for n,s in statuses.items())+'\n\n'+
      tr('Setiap status didukung `FULL_RESEARCH_RUN_LOG.json`. Langkah NOT_RUN tidak pernah dinyatakan dipanggil.\n'),encoding='utf8')
    overview['artifacts']['FULL_RESEARCH_SUMMARY.md']=sha256(base/'FULL_RESEARCH_SUMMARY.md')
    save_json(base/'FULL_RESEARCH_MANIFEST.json',validate_schema(overview,'jorhas_full_manifest'))
    return overview
