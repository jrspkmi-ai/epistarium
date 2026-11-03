"""Liora 0.1.2: conservative Crossref discovery with a transparent time policy.

Metadata != abstract != full text. Search coverage is not comprehensive.
Publication date does not establish the date of the event being studied.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
import re
import requests
from .common import now_iso, today, five_years_ago, normalize, save_json, save_csv, load_json, stable_article_id, require_unique_ids

from ._version import __version__ as VERSION
SCOPE_ALIASES={"phenomenon":"fenomena","empirical":"empiris","theory":"teori","method":"metode","concept":"konsep"}
SCOPES = ("fenomena", "empiris", "teori", "metode", "konsep")
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)


def normalize_doi(value):
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", str(value or "").strip(), flags=re.I).lower().rstrip(".,; )")


def _subtract_years(value: date, years: int):
    if not 1 <= years <= 100:
        raise ValueError(tr('years harus antara 1 dan 100'))
    try:
        return value.replace(year=value.year - years)
    except ValueError:
        return value.replace(year=value.year - years, day=28)


@localized
def query_plan(topic, scope="fenomena", as_of=None, years=5):
    scope=SCOPE_ALIASES.get(scope,scope)
    as_of = as_of or today()
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError(tr('Topik tidak boleh kosong'))
    if scope not in SCOPES:
        raise ValueError(tr('scope harus fenomena|empiris|teori|metode|konsep'))
    cutoff = _subtract_years(as_of, years).isoformat()
    # For empirical literature, five years is a *priority*, not an exclusion rule.
    # For historical theories and methods there is no automatic date cutoff.
    default_cutoff = cutoff if scope == "fenomena" else None
    priority_cutoff = cutoff if scope in ("fenomena", "empiris") else None
    policy = ("batas_default_fenomena" if scope == "fenomena" else
              "prioritas_lima_tahun_tanpa_eksklusi" if scope == "empiris" else "tanpa_batas_otomatis")
    return {
        "topic": topic.strip(), "scope": scope, "retrieved_at": now_iso(),
        "as_of_date": as_of.isoformat(), "default_cutoff": default_cutoff,
        "priority_cutoff": priority_cutoff, "time_policy": policy,
        "query_literal": topic.strip(),
        "bool_strategy_suggestion": f'("{topic.strip()}") AND (empirical OR qualitative OR quantitative)' if scope in ("fenomena","empiris") else f'("{topic.strip()}")',
        "executed_query_semantics": tr('Crossref query.bibliographic = pencocokan kata bibliografi, bukan Boolean penuh'),
        "date_basis_warning": tr('Filter tanggal metadata PUBLIKASI tidak membuktikan tanggal FENOMENA/peristiwa; periksa tanggal peristiwa terpisah.'),
        "coverage_warning": tr('Pencarian kandidat Crossref saja; bukan pencarian lengkap Scopus/WoS/SINTA atau artikel full-text.')
    }


def crossref_url(topic, cutoff=None, rows=20):
    if not 1 <= rows <= 100:
        raise ValueError(tr('rows harus 1-100'))
    params = {"query.bibliographic":topic,"rows":rows,
              "select":"DOI,title,author,published,published-print,published-online,container-title,URL,type,abstract,ISSN"}
    if cutoff:
        params["filter"] = f"from-pub-date:{cutoff}"
    return "https://api.crossref.org/works?"+urlencode(params)


def fetch_crossref(url, mailto=None):
    from .pathfinder_harvest import LimitedClient, HarvestBlocked, UA
    import json
    if mailto and not re.fullmatch(r'[^@\s]+@[^@\s]+',mailto):raise ValueError(tr('Email kontak metadata tidak valid'))
    user_agent=UA+(f' (mailto:{mailto})' if mailto else '')
    try:
        raw,_=LimitedClient(max_requests=2,max_bytes=5_000_000,user_agent=user_agent).get(url,provider='crossref')
        data=json.loads(raw)
    except HarvestBlocked as exc:
        raise RuntimeError(tr('Akses metadata Crossref terhalang; periksa jaringan/izin')) from exc
    items = data.get("message",{}).get("items")
    if not isinstance(items, list):
        raise ValueError(tr('Format Crossref tidak sesuai: message.items harus array'))
    return items


def publication_date(item):
    """Return displayed publication date, precision and used field; never invent day."""
    for field in ("published", "published-online", "published-print"):
        parts = (item.get(field) or {}).get("date-parts",[])
        if not parts or not parts[0]:
            continue
        d = parts[0]
        try:
            year = int(d[0])
            if year < 1500 or year > 2200:
                continue
            if len(d) >= 3:
                value = date(year,int(d[1]),int(d[2]))
                return value.isoformat(),"day",field
            if len(d) == 2 and 1 <= int(d[1]) <= 12:
                return f"{year:04d}-{int(d[1]):02d}","month",field
            return str(year),"year",field
        except (ValueError,TypeError,IndexError):
            continue
    return None,"unknown",None


def publication_year(item):
    value, _, _ = publication_date(item)
    return int(value[:4]) if value else None


def _date_relation(value, precision, cutoff):
    """Returns before/after/uncertain relative to cutoff without guessing dates."""
    if not value or precision == "unknown":
        return "uncertain"
    comparable = cutoff[:len(value)]
    if value < comparable:
        return "before"
    if value > comparable:
        return "after"
    if precision == "day":
        return "after"  # on cutoff counts as within window
    return "uncertain"


def compact_crossref(item, requested_url, topic):
    if not isinstance(item,dict):
        raise ValueError(tr('Item Crossref bukan objek'))
    raw_title = item.get("title") or []
    title = raw_title[0] if isinstance(raw_title,list) and raw_title else str(raw_title or "")
    raw_journal = item.get("container-title") or []
    journal = raw_journal[0] if isinstance(raw_journal,list) and raw_journal else str(raw_journal or "")
    authors = "; ".join((a.get("given", "")+" "+a.get("family", "")).strip() for a in item.get("author",[]) if isinstance(a,dict))
    doi=normalize_doi(item.get("DOI"))
    tokens=set(re.findall(r"\w+",normalize(topic)))
    words=set(re.findall(r"\w+",normalize(title)))
    score=round(len(tokens & words)/len(tokens),3) if tokens else 0
    pub_date,precision,date_field=publication_date(item)
    abstract=item.get("abstract")
    # Abstracts may be publisher XML; presence is metadata, not an AI reading claim.
    has_abstract = bool(isinstance(abstract,str) and abstract.strip())
    return {"doi":doi, "doi_format_status":"format_valid" if DOI_PATTERN.match(doi) else "missing_or_invalid",
            "title":title,"authors":authors,"year":int(pub_date[:4]) if pub_date else None,
            "publication_date":pub_date,"date_precision":precision,"publication_date_field":date_field or "",
            "journal":journal,"issn":"; ".join(item.get("ISSN") or []),
            "url":item.get("URL") or "", "type":item.get("type") or "",
            "relevance_keyword_overlap":score,"relevance_status":tr('heuristik judul; perlu penilaian ilmiah'),
            "available_level":"metadata+abstract_metadata" if has_abstract else "metadata",
            "abstract_available":has_abstract,"fulltext_read":False,
            "source_database":"Crossref", "query_url":requested_url,"observed_at":now_iso(),
            "excluded":False,"exclusion_reason":"","recency_tag":"belum dinilai",
            "needs_manual_date_check":False}


def deduplicate(records):
    seen,out,removed={},[],[]
    for r in records:
        key = "doi:"+r["doi"] if r.get("doi") and r.get("doi_format_status") == "format_valid" else (
            "title:"+normalize(r.get("title",""))+"|"+str(r.get("year")))
        if key in seen:
            removed.append({"key":key,"title":r.get("title", ""),"kept_record":seen[key]})
        else:
            seen[key]=len(out)
            out.append(r)
    return out,removed


def classify_date(record, plan):
    cutoff=plan["priority_cutoff"]
    if not cutoff:
        record["recency_tag"]=tr('tanpa prioritas usia')
        return record
    relation=_date_relation(record["publication_date"],record["date_precision"],cutoff)
    if relation == "before":
        record["recency_tag"]=tr('lebih lama dari lima tahun')
        if plan["scope"] == "fenomena":
            record["excluded"] = True
            record["exclusion_reason"] = tr('Tanggal publikasi mendahului batas fenomena default; tanggal peristiwa tetap harus diperiksa.')
    elif relation == "after":
        record["recency_tag"]=tr('dalam jendela lima tahun menurut metadata publikasi')
    else:
        record["recency_tag"]=tr('tanggal batas tidak pasti')
        record["needs_manual_date_check"] = True
        # Uncertainty is not an exclusion: conservatively hold instead of discarding.
        record["exclusion_reason"]=tr('Perlu pemeriksaan presisi tanggal sebelum inklusi final.')
    return record


def _to_ris(records):
    lines=[]
    for r in records:
        if r.get("excluded"):
            continue
        lines.extend(["TY  - JOUR" if r.get("type")=="journal-article" else "TY  - GEN","TI  - "+r["title"]])
        for author in filter(None,r["authors"].split("; ")):
            lines.append("AU  - "+author)
        for field,value in (("PY",r.get("year")),("JO",r.get("journal")),("DO",r.get("doi")),("UR",r.get("url"))):
            if value:
                lines.append(field+"  - "+str(value))
        lines.extend(["ER  - ",""])
    return "\n".join(lines)


@localized
def search(topic, out_dir, scope="fenomena", rows=20, mailto=None, fixture=None, as_of=None, timezone_name=None):
    plan=query_plan(topic,scope,as_of=as_of or today(timezone_name))
    plan["timezone"]=timezone_name or tr('zona waktu lokal mesin')
    url=crossref_url(topic,plan["default_cutoff"],rows=rows)
    out=Path(out_dir)
    out.mkdir(parents=True,exist_ok=True)
    plan["request_url"]=url
    plan["execution"]="not_started"
    try:
        if fixture:
            raw=load_json(fixture)
            raw=raw.get("message",{}).get("items",raw) if isinstance(raw,dict) else raw
            plan["execution"]="offline_fixture"
        else:
            raw=fetch_crossref(url,mailto=mailto)
            plan["execution"]="live_crossref"
        if not isinstance(raw,list):
            raise ValueError(tr('Daftar kandidat bukan array'))
        records=[classify_date(compact_crossref(item,url,topic),plan) for item in raw]
    except (OSError,ValueError,TypeError,RuntimeError,requests.RequestException) as exc:
        plan["execution"]="blocked"
        plan["error_type"]=type(exc).__name__
        plan["error_message"]=str(exc)[:350]
        save_json(out/"search_plan.json",plan)
        save_json(out/"search_error.json",{"status":"BLOCKED","reason":plan["error_message"],"timestamp":now_iso()})
        raise RuntimeError(tr('Pencarian Liora tidak berhasil; lihat search_error.json. Hasil sebelumnya tidak dapat dianggap hasil run ini.')) from exc
    unique,removed=deduplicate(records)
    for record in unique:record['article_id']=stable_article_id(record)
    require_unique_ids(unique,'article_id')
    plan["candidate_count"] = len(unique)
    plan["dedup_count"] = len(removed)
    plan["executed_provider"]="Crossref"
    save_json(out/"search_plan.json",plan)
    save_json(out/"candidates.json",{"plan":plan,"records":unique,"deduplicated":removed})
    save_csv(out/"candidates.csv",unique,list(unique[0]) if unique else ["doi","title","year","url"])
    (out/"candidates.ris").write_text(_to_ris(unique),encoding="utf-8")
    return unique
