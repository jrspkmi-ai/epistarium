"""Shared, conservative evidence metadata and file output helpers."""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from datetime import date, datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import csv
import hashlib
import json
import re
import math
from importlib.resources import files

EXECUTION_STATUSES = frozenset({"SUCCESS", "PARTIAL", "BLOCKED", "FAILED", "NOT_RUN"})


def xml_safe_copy(value, audit=None, path='$'):
    """Return a sanitized export copy; leave the evidence object untouched."""
    if audit is None:audit=[]
    if isinstance(value,str):
        clean=''.join(c if c in '\t\n\r' or 0x20<=ord(c)<=0xD7FF or 0xE000<=ord(c)<=0xFFFD or 0x10000<=ord(c)<=0x10FFFF else '\ufffd' for c in value)
        count=sum(a!=b for a,b in zip(value,clean))
        if count:
            audit.append({'field':path,'replacements':count,
                'original_sha256':hashlib.sha256(value.encode('utf-8',errors='surrogatepass')).hexdigest()})
        return clean
    if isinstance(value,dict):return {k:xml_safe_copy(v,audit,f'{path}.{k}') for k,v in value.items()}
    if isinstance(value,list):return [xml_safe_copy(v,audit,f'{path}[{i}]') for i,v in enumerate(value)]
    return value


def validate_schema(payload, schema_name):
    """Validate a packaged contract with an actionable JSON-path error."""
    from jsonschema import Draft202012Validator
    if not re.fullmatch(r"[a-z0-9_]+", schema_name):
        raise ValueError(tr('Nama schema tidak valid'))
    schema = json.loads(files("epistarium").joinpath("data", schema_name + ".schema.json").read_text(encoding="utf8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda e: str(list(e.path)))
    if errors:
        error = errors[0]
        where = "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in error.path)
        # Do not echo source text, paths or secrets contained in the payload.
        raise ValueError(tr('Kontrak {v0} gagal di {v1}: aturan {v2}',v0=f'{schema_name}', v1=f'{where}', v2=f'{error.validator}'))
    return payload


def require_unique_ids(records, key):
    seen = set()
    for record in records:
        value = record.get(key)
        if not isinstance(value, str) or not value.strip() or value in seen:
            raise ValueError(tr('{v0} harus string tidak kosong dan unik',v0=f'{key}'))
        seen.add(value)


def stable_article_id(record):
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", str(record.get("doi") or "").strip(), flags=re.I).casefold()
    if re.fullmatch(r"10\.\d{4,9}/\S+", doi):
        key = "doi:" + doi
    else:
        key = json.dumps([normalize(record.get("title")), str(record.get("year") or ""), normalize(record.get("authors"))], ensure_ascii=False)
    return "article-" + hashlib.sha256(key.encode("utf8")).hexdigest()[:20]


def prepare_run_directory(path):
    """Refuse stale outputs; caller supplies a fresh directory for each run."""
    out = Path(path)
    if out.exists() and any(out.iterdir()):
        raise ValueError(tr('Folder keluaran sudah berisi berkas; gunakan folder baru untuk run ini'))
    out.mkdir(parents=True, exist_ok=True)
    return out

STATUSES = [
    "terverifikasi", "didukung sebagian", "bertentangan", "tidak ditemukan",
    "belum dapat diverifikasi", "inferensi peneliti/AI", "hipotesis atau rekomendasi"
]


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def today(timezone_name=None):
    return datetime.now(ZoneInfo(timezone_name)).date() if timezone_name else datetime.now().astimezone().date()


def five_years_ago(d: date):
    try:
        return d.replace(year=d.year - 5)
    except ValueError:
        return d.replace(year=d.year - 5, day=28)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize(s):
    return re.sub(r"\s+", " ", (s or "").casefold()).strip()


def save_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def save_csv(path, rows, fields):
    rows=list(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for record in rows:
            safe = {}
            for key, value in record.items():
                if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                    # Prevent spreadsheet formula execution on CSV open.
                    safe[key] = "'" + value
                else:
                    safe[key] = value
            w.writerow(safe)
    if get_language()=='en' and not path.stem.endswith('_display'):
        from .i18n import column_labels,display_field_value
        labels=column_labels()
        headings=[labels.get(key,key) for key in fields]
        if len(headings)!=len(set(headings)):
            raise ValueError('Translated CSV headings must be unique.')
        display_rows=[{labels.get(key,key):display_field_value(key,row.get(key)) for key in fields} for row in rows]
        save_csv(path.with_name(path.stem+'_display.csv'),display_rows,headings)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
