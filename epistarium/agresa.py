"""Agresa 0.1.2: conservative, auditable reconciliation of journal evidence.

No official portal fetch is performed. A URL under an official domain is not
proof that a source is indexed. Journal presence != individual article record.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
import re
from .common import normalize, now_iso, save_json, save_csv

from ._version import __version__ as VERSION
OFFICIAL={
 "scopus":("scopus.com","elsevier.com","elsevier.support"),
 "wos":("mjl.clarivate.com","webofscience.com","clarivate.com","support.clarivate.com"),
 "sinta":("sinta.kemdiktisaintek.go.id","sinta.kemdikbud.go.id","arjuna.kemdikbud.go.id","arjuna.kemdiktisaintek.go.id")
}
WOS_COLLECTIONS={"SCIE","SSCI","AHCI","ESCI"}


def official_url(db,url):
    try:
        p=urlparse(str(url or ""))
        host=(p.hostname or "").lower()
        # Avoid userinfo-credential tricks and arbitrary ports in evidence links.
        return (p.scheme == "https" and not p.username and not p.password
                and p.port in (None,443) and bool(host)
                and any(host == suffix or host.endswith("."+suffix) for suffix in OFFICIAL[db]))
    except (KeyError,ValueError,TypeError):
        return False


def issn_norm(s):
    return "".join(c for c in str(s or "").upper() if c.isalnum())


def issn_set(record):
    values=[]
    for k in ("issn","eissn","print_issn","electronic_issn","issns"):
        v=record.get(k) if isinstance(record,dict) else None
        if isinstance(v,list):
            values.extend(v)
        elif v:
            values.extend(re.split(r"[;,\s]+",str(v)))
    return {n for v in values if (n:=issn_norm(v)) and len(n)==8}


def _identity_match(journal,evidence):
    ji,ei=issn_set(journal),issn_set(evidence)
    jt,et=normalize(journal.get("title")),normalize(evidence.get("title"))
    titles_agree=bool(jt and et and jt==et)
    if ji and ei:
        if ji.isdisjoint(ei):
            return "issn_conflict" if titles_agree else "not_same_source"
        if jt and et and not titles_agree:
            return "issn_match_title_conflict"
        return "issn_match" if titles_agree else "issn_match_title_missing"
    if titles_agree:
        return "title_only_missing_issn"
    return "not_same_source"


def _evidence_complete(e,db):
    if not e.get("reviewed_by") or not e.get("checked_at") or not e.get("evidence_note"):
        return False,tr('Tidak ada nama pemeriksa, tanggal, atau catatan sumber.')
    try:
        checked=date.fromisoformat(e["checked_at"])
        if checked > date.today():
            return False,tr('Tanggal pemeriksaan bukti berada di masa depan menurut mesin.')
    except (TypeError,ValueError):
        return False,tr('Tanggal pemeriksaan harus YYYY-MM-DD.')
    start,end=e.get("coverage_start"),e.get("coverage_end")
    if type(start) is not int or (end is not None and type(end) is not int):
        return False,tr('Periode cakupan harus memiliki tahun awal integer dan akhir integer atau null.')
    if end is not None and end<start:
        return False,tr('Periode cakupan terbalik.')
    if db=="sinta" and e.get("rank") not in ("S1","S2","S3","S4"):
        return False,tr('Peringkat SINTA S1-S4 belum jelas.')
    if db=="wos" and not (set(e.get("wos_collections") or ([e["wos_collection"]] if e.get("wos_collection") else [])) & WOS_COLLECTIONS):
        return False,tr('Koleksi WoS Core Collection belum diidentifikasi (SCIE/SSCI/AHCI/ESCI).')
    return True,tr('Bukti yang disuplai pengguna lengkap secara format; isi sumber belum diperiksa independen.')


def _sinta_period_for_year(e, year):
    """Identify rank applicable to article year; require accredited period evidence."""
    if e.get("period_type") != "accreditation":
        return None, tr('SINTA: periode pada catatan belum secara eksplisit dinyatakan masa akreditasi.')
    periods=e.get("rank_periods")
    if periods is None:
        return e, ""
    if not isinstance(periods,list) or not periods:
        return None, tr('SINTA: daftar riwayat peringkat/akreditasi tidak valid atau kosong.')
    matches=[]
    for period in periods:
        if not isinstance(period,dict):
            continue
        start,end=period.get("coverage_start"),period.get("coverage_end")
        if type(start) is not int or type(end) is not int or end < start or period.get("rank") not in ("S1","S2","S3","S4"):
            return None, tr('SINTA: periode riwayat peringkat tidak valid.')
        if type(year) is int and start<=year<=end:
            matches.append(period)
    if len(matches)>1:
        return None, tr('SINTA: beberapa riwayat akreditasi tumpang tindih pada tahun artikel.')
    if len(matches)==0:
        return None, tr('SINTA: tidak ada periode akreditasi yang cocok dengan tahun artikel dalam bukti input.')
    period=matches[0]
    enriched={**e,"rank":period["rank"],"coverage_start":period["coverage_start"],"coverage_end":period["coverage_end"]}
    return enriched,""


def _article_evidence(e,journal,db):
    record=e.get("article_record") or {}
    if not isinstance(record,dict):
        return "belum dapat diverifikasi"
    expected=str(journal.get("article_doi") or "").lower().removeprefix("https://doi.org/")
    actual=str(record.get("doi") or "").lower().removeprefix("https://doi.org/")
    if (expected and expected==actual and official_url(db,record.get("official_url"))
       and record.get("reviewed_by") and record.get("checked_at") and record.get("evidence_note")):
        return tr('ada catatan artikel resmi dalam bukti input; belum diverifikasi independen')
    return "belum dapat diverifikasi"


def verify_journal(journal,evidence):
    results=[]
    for db in ("scopus","wos","sinta"):
        candidates=[]
        conflicts=[]
        for e in evidence:
            if not isinstance(e,dict) or e.get("database")!=db:
                continue
            if not official_url(db,e.get("official_url")):
                continue
            match=_identity_match(journal,e)
            if match in ("issn_match","issn_match_title_missing","title_only_missing_issn","issn_match_title_conflict"):
                candidates.append((e,match))
            elif match=="issn_conflict":
                conflicts.append(e)
        result={"journal":journal.get("title", ""),"issn":journal.get("issn", ""),
                "article_doi":journal.get("article_doi", ""),"article_year":journal.get("year"),
                "database":db,"status_jurnal":"belum dapat diverifikasi",
                "status_artikel":"belum dapat diverifikasi","identity_match":"tidak ditemukan",
                "verification_level":tr('pemeriksaan catatan pengguna tanpa akses portal'), "independent_verification":False,
                "rank":"","wos_collection":"","coverage_start":"","coverage_end":"",
                "source_url":"","evidence_reviewed_by":"","evidence_checked_at":"",
                "checked_at":now_iso(),"requires_manual_confirmation":True,
                "note":tr('Tidak ada bukti identitas dan cakupan yang memadai dari input pengguna.')}
        if conflicts:
            result.update(identity_match="konflik ISSN/judul",note=tr('Judul yang sama muncul dengan ISSN yang bertentangan. Hentikan pencocokan otomatis dan periksa identitas jurnal.'))
            results.append(result)
            continue
        if len(candidates)>1:
            result.update(identity_match="ambigu beberapa catatan",note=tr('Lebih dari satu catatan resmi tampak cocok; konflik periode atau duplikasi harus diperiksa manusia.'))
            results.append(result)
            continue
        if len(candidates)==1:
            e,match=candidates[0]
            sinta_note=""
            if db=="sinta":
                prepared,sinta_note=_sinta_period_for_year(e,journal.get("year"))
                if prepared:
                    e=prepared
            result.update(identity_match=match,source_url=e.get("official_url", ""),
                          rank=e.get("rank", ""),
                          wos_collection="; ".join(e.get("wos_collections") or ([e["wos_collection"]] if e.get("wos_collection") else [])),
                          coverage_start=e.get("coverage_start") if e.get("coverage_start") is not None else "",
                          coverage_end=e.get("coverage_end") if e.get("coverage_end") is not None else "",
                          evidence_reviewed_by=e.get("reviewed_by", ""),
                          evidence_checked_at=e.get("checked_at", ""))
            if match in ("title_only_missing_issn","issn_match_title_conflict"):
                result["note"]=tr('Identitas jurnal belum cukup pasti: ')+match+tr('. Periksa ISSN dan riwayat perubahan judul.')
            elif sinta_note:
                result["note"]=sinta_note
            else:
                complete,why=_evidence_complete(e,db)
                y=journal.get("year")
                if not complete:
                    result["note"]=why
                elif type(y) is not int:
                    result["note"]=tr('Tahun artikel tidak tersedia atau tidak valid.')
                elif y < e["coverage_start"] or (e["coverage_end"] is not None and y > e["coverage_end"]):
                    result["status_jurnal"]="di luar periode yang tercatat"
                    result["note"]=tr('Tahun artikel di luar periode yang dicantumkan dalam bukti input; status artikel tetap belum dapat diverifikasi.')
                else:
                    result["status_jurnal"]="cocok dengan catatan indeks yang diinput"
                    result["note"]=(tr('Periode dan identitas cocok dengan catatan pengguna. URL resmi tidak membuktikan bahwa halaman tersebut telah diakses atau isinya benar. Periksa status aktif/discontinued/hold dan cakupan historis di portal terkait.'))
                # Article-level presence is only a record supplied by human, not live confirmation.
                if complete and type(y) is int:
                    result["status_artikel"]=_article_evidence(e,journal,db)
        results.append(result)
    return results


@localized
def audit(journals,evidence,out_dir):
    if not isinstance(journals,list) or not isinstance(evidence,list):
        raise ValueError(tr('journals dan evidence wajib berupa JSON array'))
    out=Path(out_dir)
    out.mkdir(parents=True,exist_ok=True)
    results=[r for j in journals for r in verify_journal(j,evidence)]
    save_json(out/"index_audit.json",{"tool":"Agresa","version":VERSION,
              "verification_mode":tr('rekonsiliasi bukti yang disediakan pengguna, bukan fetch resmi'),
              "records":results,
              "disclaimer":tr('Tidak ada verifikasi live dari Scopus/WoS/SINTA; jangan nyatakan artikel terindeks tanpa bukti rekam artikel yang langsung diperiksa.')})
    save_csv(out/"index_audit.csv",results,list(results[0]) if results else ["journal","database","status_jurnal"])
    lines=[tr('# Laporan Agresa'), "", tr('**Mode bukti:** catatan pengguna, bukan pemeriksaan live indeks.'), ""]
    for r in results:
        lines.extend([f"## {r['journal']} | {r['database']}",
                      tr('Identitas: {v0}',v0=display_status(r['identity_match'])),
                      tr('Jurnal: {v0}; artikel: {v1}',v0=f"{display_status(r['status_jurnal'])}", v1=f"{display_status(r['status_artikel'])}"),
                      tr('Bukti: {v0}; waktu sumber: {v1}',v0=f"{r['source_url'] or tr('tidak tersedia')}", v1=f"{r['evidence_checked_at'] or tr('tidak ada')}"),
                      tr('Catatan: {v0}',v0=f"{r['note']}"),""])
    (out/"laporan.md").write_text("\n".join(lines),encoding="utf-8")
    return results
