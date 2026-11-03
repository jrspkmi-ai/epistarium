"""Pathfinder Data Ledger: provenance-preserving checks, not statistical inference."""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from datetime import date
import math
from .common import normalize, EXECUTION_STATUSES, require_unique_ids

SCHEMA='epistarium.pathfinder.data.v1'
DATA_TYPES={'statistik resmi','survei','dataset','proksi digital','dokumentasi kasus','literatur'}
FIELDS=[
 'record_id','source_id','jenis_data','kelompok_bukti','indikator','definisi_operasional','nilai','satuan','pembilang','penyebut',
 'organisasi_penerbit','produsen_asli','judul_sumber','url','doi','file_sha256','versi',
 'tanggal_peristiwa','tanggal_observasi','periode_referensi','tanggal_publikasi','tanggal_pengambilan',
 'geografi','populasi','unit_analisis','cakupan','sampel','metode_sampling','metode_pengumpulan',
 'metode_perhitungan','representativitas','level_estimasi','bias','tipe_akses','lisensi','penilaian_mutu',
 'status_verifikasi','cuplikan','lokasi_bukti','kaitan_klaim','batas_generalisasi','asal_record',
 'synthetic','issue_codes','rights_note','source_claimed_status','nilai_raw','nilai_parse_error'
]
SOURCE_FIELDS=['source_id','provider','title','url','doi','source_type','access_status','execution_status',
 'evidence_level','rights','license','attempted_at','retrieved_at','response_code','failure_reason',
 'query','sha256','synthetic','notes','source_aliases','access_attempts']
STATUS={'terverifikasi','didukung sebagian','bertentangan','tidak ditemukan','belum dapat diverifikasi','inferensi peneliti/AI','hipotesis atau rekomendasi'}
EXEC=EXECUTION_STATUSES

def source_row(src):
    out={k:None for k in SOURCE_FIELDS}
    out.update({k:v for k,v in src.items() if k in out})
    if out['execution_status'] not in EXEC:out['execution_status']='NOT_RUN'
    out['synthetic'] = src.get('synthetic', False)
    if not isinstance(out['synthetic'], bool):raise ValueError(tr('synthetic harus boolean'))
    out['source_aliases'] = src.get('source_aliases') or []
    out['access_attempts'] = src.get('access_attempts') or []
    return out

def normalize_record(raw, index, *, observed_on=None, synthetic=False):
    if not isinstance(raw,dict): raise ValueError(tr('Setiap rekaman ledger wajib objek JSON'))
    out={k:None for k in FIELDS}
    out.update({k:v for k,v in raw.items() if k in out})
    out['record_id']=out['record_id'] or f'PF-{index:04d}'
    # Every source-supplied assessment remains a claim, regardless of enum value.
    claimed = raw.get('source_claimed_status', raw.get('status_verifikasi'))
    out['source_claimed_status'] = claimed if isinstance(claimed, str) else None
    out['status_verifikasi']='belum dapat diverifikasi'
    out['tanggal_pengambilan']=out['tanggal_pengambilan'] or observed_on
    if not isinstance(raw.get('synthetic',False),bool) or not isinstance(synthetic,bool):
        raise ValueError(tr('synthetic harus boolean'))
    out['synthetic']=synthetic or raw.get('synthetic',False)
    issues=[]
    if claimed and claimed != 'belum dapat diverifikasi':issues.append('STATUS_SUMBER_BELUM_DIREVIEW')
    out['nilai_raw'] = raw.get('nilai_raw', raw.get('nilai'))
    value = out['nilai']
    if value is not None:
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
            out['nilai']=None
            out['nilai_raw']=str(value)
            out['nilai_parse_error']=tr('Nilai tidak berupa angka hingga yang valid')
            issues.append('NILAI_BUKAN_ANGKA')
    if out['nilai_parse_error']:issues.append('NILAI_BUKAN_ANGKA')
    t=normalize(out['jenis_data']);group=normalize(out['kelompok_bukti'])
    if out['jenis_data'] not in DATA_TYPES:issues.append('JENIS_DATA_TIDAK_STANDAR')
    if not out['url'] and not out['doi'] and not out['file_sha256']:
        issues.append('PROVENANCE_SUMBERRAWAN')
    if out['nilai'] is not None:
        if isinstance(out['nilai'],bool) or not isinstance(out['nilai'],(int,float)):
            issues.append('NILAI_BUKAN_ANGKA')
        if not out['satuan']:issues.append('SATUAN_TIDAK_ADA')
    if out['nilai'] is not None and out['satuan'] in ('%','persen','persentase') and out['penyebut'] in (None,''):
        issues.append('PENYEBUT_TIDAK_TERSEDIA')
    if 'survei' in t or 'survei' in group:
        if not out['metode_sampling'] or not out['sampel'] or not out['populasi']:
            issues.append('METODE_SURVEI_TIDAK_LENGKAP')
        s=normalize(out['metode_sampling']); rep=normalize(out['representativitas'])
        if any(x in s for x in ('sukarela','nonprobabilitas','purposive','convenience','online terbuka','voluntary','nonprobability','non-probability','open online')):
            issues.append('TIDAK_DAPAT_DIGENERALISASI_PROBABILISTIK')
            if any(x in rep for x in ('nasional','representatif','mewakili populasi','national','representative','represents the population')):
                issues.append('KLAIM_REPRESENTATIVITAS_TIDAK_DIDUKUNG')
    if 'google trends' in normalize(out['organisasi_penerbit'] or out['judul_sumber']):
        issues.append('TRENDS_INDEKS_RELATIF_BUKAN_VOLUME')
        if out['satuan'] not in ('indeks 0-100','skala relatif 0-100'):
            issues.append('SATUAN_GOOGLE_TRENDS_PERLU_DIKOREKSI')
    if 'gdelt' in normalize(out['organisasi_penerbit'] or out['judul_sumber']):
        issues.append('GDELT_CAKUPAN_BERITA_BUKAN_JUMLAH_KEJADIAN')
    if out.get('tanggal_peristiwa') and out.get('tanggal_publikasi') and out['tanggal_peristiwa']!=out['tanggal_publikasi']:
        issues.append('TANGGAL_PERISTIWA_BERBEDA_DARI_PUBLIKASI')
    if not out['definisi_operasional']:issues.append('DEFINISI_BELUM_DIKETAHUI')
    if out['synthetic']:issues.append('DATA_SINTETIS_BUKAN_BUKTI_EMPIRIS')
    out['issue_codes']=sorted(set(issues))
    if not out['batas_generalisasi']:
        out['batas_generalisasi']=tr('Belum dapat ditetapkan; populasi, sampling, definisi dan konteks perlu diperiksa.')
    return out

def deduplicate_sources(rows):
    require_unique_ids(rows, 'source_id')
    seen={};out=[];duplicates=[]
    for src in rows:
        key=(normalize(src.get('doi')) or normalize(src.get('url')) or (normalize(src.get('provider'))+'|'+normalize(src.get('title'))))
        snapshot={k:v for k,v in src.items() if k not in ('source_aliases','access_attempts')}
        if key in seen:
            canonical=seen[key]
            duplicates.append(src['source_id'])
            canonical['source_aliases'].append(src['source_id'])
            canonical['source_aliases'].extend(src.get('source_aliases') or [])
            canonical['access_attempts'].append(snapshot)
            canonical['access_attempts'].extend(src.get('access_attempts') or [])
        else:
            item={**src,'source_aliases':list(src.get('source_aliases') or []),
                  'access_attempts':list(src.get('access_attempts') or []) or [snapshot]}
            seen[key]=item;out.append(item)
    return out,duplicates


def reconcile_sources(records, sources):
    """Resolve aliases; retain unmatched source claims as explicit imported sources."""
    ids={s['source_id']:s['source_id'] for s in sources}
    for source in sources:
        for alias in source.get('source_aliases') or []:ids[alias]=source['source_id']
    for record in records:
        original=record.get('source_id')
        if original in ids:
            record['source_id']=ids[original]
            continue
        matches=[s for s in sources if (record.get('url') and s.get('url')==record['url']) or
                 (record.get('doi') and normalize(s.get('doi'))==normalize(record['doi']))]
        if len(matches)==1:
            record['source_id']=matches[0]['source_id']
        else:
            sid=f'IMPORTED-{len(sources)+1:04d}'
            sources.append(source_row({'source_id':sid,'provider':'imported_record',
                'title':record.get('judul_sumber'),'url':record.get('url'),'doi':record.get('doi'),
                'sha256':record.get('file_sha256'),'execution_status':'NOT_RUN',
                'synthetic':record.get('synthetic',False),'access_status':'source_not_independently_checked',
                'notes':tr('Metadata asal rekaman; sumber belum diakses secara independen.')}))
            record['source_id']=sid
        if original and original not in ids:
            record['issue_codes']=sorted(set(record['issue_codes']+['SOURCE_ID_ASAL_TIDAK_DIKENAL']))
    require_unique_ids(records,'record_id')
    require_unique_ids(sources,'source_id')
    canonical_ids={s['source_id'] for s in sources}
    if any(r['source_id'] not in canonical_ids for r in records):raise ValueError(tr('Relasi source_id terputus'))
    return records,sources

def comparability_issues(records):
    """Flag competing definitions/sampling contexts; never sum incomparable figures."""
    issues=[]
    by_indicator={}
    for r in records:
        if r.get('indikator'):
            by_indicator.setdefault(normalize(r['indikator']),[]).append(r)
    keys=['definisi_operasional','geografi','populasi','satuan','metode_sampling']
    for indicator,rows in by_indicator.items():
        if len(rows)<2:continue
        for k in keys:
            vals={str(r.get(k)) for r in rows if r.get(k) not in (None,'')}
            if len(vals)>1:issues.append({'indikator':indicator,'type':'TIDAK_SEBANDING','field':k,'record_ids':[r['record_id'] for r in rows],'values':sorted(vals)})
    return issues

def audit_aggregates(records):
    return {'total':len(records),'synthetic_count':sum(bool(r.get('synthetic')) for r in records),
       'unknown_verification_count':sum(r.get('status_verifikasi')=='belum dapat diverifikasi' for r in records),
       'comparability_issues':comparability_issues(records)}
