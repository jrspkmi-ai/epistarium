"""Retho: lawful local full-text inventory + optional verified OA discovery.

Metadata links are not proof of a readable PDF, full-text, ownership, or reuse rights.
No file is redistributed or uploaded by this module.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
import ipaddress
import json
import re
import socket
from pathlib import Path
from urllib.parse import urlsplit, quote
import requests
from . import pdf_backend as fitz
from .common import save_json, now_iso, sha256
from .liora import normalize_doi

from ._version import __version__ as VERSION
VERSIONS = {"publishedVersion":"published", "acceptedVersion":"accepted_manuscript",
            "submittedVersion":"preprint", "published":"published", "accepted_manuscript":"accepted_manuscript",
            "preprint":"preprint", "unknown":"unknown"}
SAFE_PUBLIC_LICENSE = {"cc-by", "cc-by-4.0", "cc-by-sa", "cc0", "public-domain", "cc-by-nc", "cc-by-nc-4.0"}
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s<>\]}'\",;]+", flags=re.I)


def _version(value):
    return VERSIONS.get(value or "", "unknown")


def _oa_options(record):
    """Adapts Unpaywall-like OA records. Does not assert license/entitlement."""
    options = []
    for loc in (record or {}).get("oa_locations",[]) or []:
        if not isinstance(loc,dict):
            continue
        url = loc.get("url_for_pdf") or loc.get("url_for_landing_page")
        if not url: continue
        options.append({"url":url, "landing_url":loc.get("url_for_landing_page"),
            "format_hint":"pdf" if loc.get("url_for_pdf") else "landing_page",
            "version":_version(loc.get("version")),"license":loc.get("license"),
            "host_type":loc.get("host_type"),"source":"unpaywall_metadata",
            "rights_basis":"metadata_only_unconfirmed"})
    return options


def _validate_remote_url(url):
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise ValueError(tr('Hanya URL HTTPS tanpa kredensial yang diterima'))
    host = parts.hostname.lower()
    if host in ("localhost",) or host.endswith((".local", ".internal", ".localhost")):
        raise ValueError(tr('URL lokal/privat ditolak'))
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global: raise ValueError(tr('Alamat IP nonpublik ditolak'))
    except ValueError as e:
        if "nonpublik" in str(e): raise
    # DNS does not prove a future redirect stays public. Re-check redirects and DNS.
    for info in socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP):
        addr = ipaddress.ip_address(info[4][0])
        if not addr.is_global: raise ValueError(tr('DNS mengarah ke jaringan nonpublik'))
    return url


def _fetch_public_pdf(url, dest, session=None, max_bytes=15_000_000):
    """Intentionally disabled: licensing and network safety need separate audits."""
    raise RuntimeError("automatic_remote_download_disabled_until_rights_and_network_audit")


def _title_coverage(expected, first_page_text):
    """Lexical sanity check only, never an automatic bibliographic certification."""
    stop = {"the", "a", "an", "of", "on", "in", "and", "for", "to", "with", "from", "study", "research", "article"}
    tokens = {w for w in re.findall(r"[\w]+", (expected or "").casefold()) if len(w) > 2 and w not in stop}
    front = set(re.findall(r"[\w]+", (first_page_text or "").casefold()))
    return round(len(tokens & front) / len(tokens), 3) if tokens else None


def _frontmatter_dois(first_page_text):
    """A bibliography/reference DOI is not the article's identifying DOI.

    Only inspect front matter on page 1. Discard everything after an explicit
    references heading, and avoid treating URLs in running body text as proof.
    """
    marker = re.search(r"(?im)^\s*(references|bibliography|daftar pustaka|works cited)\s*:?\s*(?:$|(?=\S))", first_page_text)
    prefix = first_page_text[:marker.start()] if marker else first_page_text
    front = prefix  # including bottom-of-page publisher DOI; references have been excluded
    found = []
    for match in DOI_RE.finditer(front):
        line_start = front.rfind("\n", 0, match.start()) + 1
        line_end = front.find("\n", match.end())
        line = front[line_start:line_end if line_end >= 0 else len(front)].strip()
        # DOI line near article front matter; header label or standalone doi.org URL.
        if re.search(r"(?i)(?:\bdoi\s*[:=]|doi\.org/|^10\.\d{4,9}/)", line):
            value = normalize_doi(match.group(0).rstrip("."))
            if value:
                found.append(value)
    return set(found)


def inspect_pdf(path, doi=None, title=None):
    path=Path(path)
    if not path.is_file(): return {"pdf_valid":False,"reason":"file_missing"}
    with path.open('rb') as file:
        if file.read(5) != b'%PDF-':
            return {"pdf_valid":False,"reason":"not_a_pdf"}
    try:
        with fitz.open(path) as doc:
            n=len(doc)
            if not n:return {"pdf_valid":False,"reason":"empty_pdf"}
            snippets=[doc[i].get_text(sort=True) for i in range(min(n,4))]
            first_page = doc[0].get_text(sort=True)
    except Exception as e:
        return {"pdf_valid":False,"reason":"pdf_parse_failed:"+type(e).__name__}
    txt="\n".join(snippets)
    found_dois={normalize_doi(m.group(0).rstrip(".")) for m in DOI_RE.finditer(txt)}
    primary=_frontmatter_dois(first_page)
    target=normalize_doi(doi)
    title_coverage=_title_coverage(title,first_page) if title else None
    title_consistent=(title_coverage is not None and title_coverage >= .60)
    if target and primary and target not in primary:
        identity='conflict'
    elif target and target in primary:
        identity='doi_matched' if (title is None or title_consistent) else 'doi_title_unconfirmed'
    elif target:
        identity='unconfirmed'  # including if DOI appears only in references
    elif title and title_consistent:
        identity='title_matched'
    else:
        identity='unconfirmed'
    return {"pdf_valid":True,"pdf_sha256":sha256(path),"page_count":n,
            "text_chars_first_4_pages":len(txt),"machine_text_accessible":len(txt.strip())>=100,
            "pdf_identity_status":identity,"dois_seen_first_4_pages":sorted(found_dois)[:12],
            "primary_dois_first_page":sorted(primary),"title_keyword_coverage_first_page":title_coverage,
            "identity_method":"first_page_frontmatter_doi_and_title_keywords; requires human adjudication for disputed records"}


def _publisher_access_observation(record):
    """Conservative, untrusted access log; never grants rights or full-text availability.

    Browser/provider observations describe the observer's session, not universal
    accessibility for other users and not proof of a downloadable PDF.
    """
    if not isinstance(record, dict):return None
    allowed = {'abstract_visible_restricted_fulltext','fulltext_link_not_access_verified',
               'http_403_unverified','metadata_only','access_unknown','abstract_visible_fulltext_unverified'}
    code = record.get('access_state')
    if code not in allowed:return None
    url=str(record.get('source_url') or '')
    if not url.startswith('https://') or len(url)>2500:return None
    return {'access_state':code,'source_url':url,
            'observed_at':record.get('observed_at'),
            'observation_source':record.get('observation_source') or 'user_supplied_observation',
            'rights_proven':False,'fulltext_verified':False,
            'note':tr('Status hanya menggambarkan pemeriksaan akses yang tercatat, bukan lisensi atau hak akses pengguna lain.')}


@localized
def build(candidates, out_dir, library=None, oa_records=None, *, download=False, public_pdf_dir=None, publisher_observations=None):
    """candidates: Liora JSON records/list. library: {doi: {pdf_path, version, rights_basis}}.
    Remote download disabled in 0.2.1 until independently verified rights and
    network security can be demonstrated. Local user PDFs are not redistributed.
    """
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    if isinstance(candidates,dict): candidates=candidates.get("candidates",candidates.get("records",[]))
    library=library or {};oa_records=oa_records or {};publisher_observations=publisher_observations or {}
    from .common import stable_article_id, require_unique_ids, validate_schema
    candidates=[dict(c,article_id=c.get('article_id') or stable_article_id(c)) for c in candidates]
    require_unique_ids(candidates,'article_id')
    rows=[]
    for ix,c in enumerate(candidates,1):
        doi=normalize_doi(c.get("doi"))
        item=library.get(c.get("article_id")) or (library.get(doi) if doi else None) or {}
        options=_oa_options(oa_records.get(doi,{}))
        options.extend(c.get("oa_locations",[]) or [])
        row={"article_id":c.get("article_id") or f"paper-{ix:03d}", "doi":doi,
            "title":c.get("title"),"authors":c.get("authors"),"year":c.get("year"),
            "journal":c.get("journal"),"article_type":c.get("type",c.get("article_type")),
            "source_database":c.get("source_database"),"query_url":c.get("query_url"),
            "publication_date":c.get("publication_date"),"date_precision":c.get("date_precision"),
            "retrieved_at":now_iso(),"metadata_level":c.get("available_level","metadata_only"),
            "abstract":c.get("abstract") if isinstance(c.get("abstract"),str) else None,
            "fulltext_read":False,"fulltext_available":False,"status":"metadata_only",
            "document_version":"unknown", "pdf_path":None,"pdf_sha256":None,
            "access_rights":"unknown","rights_for_redistribution":"not_established",
            "download_status":"not_requested", "source_identity_status":"unconfirmed",
            "oa_candidates":options,"warnings":[],
            "automatic_download_enabled":False,
            "publisher_access_observation":_publisher_access_observation(publisher_observations.get(doi))}
        if c.get("has_abstract") or row["abstract"] or "abstract" in str(c.get("available_level", "")):
            row["status"]="abstract_only"
        local=item.get("pdf_path")
        if local:
            p=Path(local)
            if not p.is_absolute() and public_pdf_dir: p=Path(public_pdf_dir)/p
            details=inspect_pdf(p,doi=doi,title=c.get("title"))
            row["pdf_path"]=str(p)
            row["document_version"]=_version(item.get("version"))
            row["access_rights"]=item.get("rights_basis","user_supplied_private")
            row["rights_for_redistribution"]="not_established"  # even a local PDF is not publication permission
            row["pdf_info"]=details
            if details.get("pdf_valid"):
                row["pdf_sha256"]=details["pdf_sha256"]
                row["source_identity_status"]=details["pdf_identity_status"]
                if details["pdf_identity_status"]=="conflict":
                    row["status"]="identity_conflict"
                    row["warnings"].append(tr('DOI dalam PDF berbeda dari kandidat, jangan gabungkan tanpa audit manual'))
                else:
                    row["fulltext_available"]=True
                    if not details["machine_text_accessible"]:
                        row["status"]="pdf_needs_ocr"
                    elif details["pdf_identity_status"] in ("unconfirmed", "doi_title_unconfirmed"):
                        row["status"]="identity_review_required"
                        row["warnings"].append(tr('Identitas DOI dan/atau judul belum dapat dipastikan; jangan teruskan ke analisis otomatis'))
                    else:
                        row["status"]="fulltext_local"
            else:
                row["status"]="pdf_invalid_or_missing"
                row["warnings"].append(details.get("reason","invalid_pdf"))
        elif download:
            # No network call: even user-supplied "confirmed_public_oa" is not
            # independent licensing evidence and redirect/DNS handling is not validated.
            row["download_status"]="blocked_rights_not_confirmed"
            row["warnings"].append(tr('Unduh otomatis nonaktif; buka tautan sumber secara manual dan periksa hak akses serta versi'))
        elif options:
            row["download_status"]="link_found_not_downloaded"
        rows.append(row)
    validate_schema(rows,"retho_articles")
    save_json(out/"articles.json",rows)
    with (out/"retrieval_report.md").open("w",encoding="utf8") as f:
        f.write(tr('# Retho: laporan akses dan versi artikel\n\n'))
        for r in rows:
            f.write(tr('- **{v0}** {v1}: `{v2}`, versi `{v3}`, hak `{v4}`, unduh `{v5}`, identitas `{v6}`.\n',v0=f"{r['article_id']}", v1=f"{r.get('title') or '(tanpa judul)'}", v2=f"{display_status(r['status'])}", v3=f"{r['document_version']}", v4=f"{r['access_rights']}", v5=f"{r['download_status']}", v6=f"{r['source_identity_status']}"))
        f.write(tr('\nTautan OA tidak membuktikan file telah diunduh. PDF privat tidak disalin ke keluaran.\n'))
    return rows


def unpaywall_lookup(doi,email,session=None):
    """Optional live metadata lookup. API access and rate limits apply; no PDF downloading."""
    if not email or "@" not in email: raise ValueError(tr('Email API valid diperlukan'))
    url=f"https://api.unpaywall.org/v2/{quote(normalize_doi(doi),safe='/')}"
    res=(session or requests).get(url,params={"email":email},timeout=(5,20))
    res.raise_for_status()
    return res.json()
