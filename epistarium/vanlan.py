"""Vanlan 0.1.1: deterministic PDF location and conservative evidence audit.

This module never infers semantic support solely from a text match. Semantic
judgments can be imported only as explicitly attributed human adjudications.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from collections import defaultdict
from pathlib import Path
import re
import unicodedata
from . import pdf_backend as fitz
from .common import normalize, sha256, now_iso, save_csv, save_json

from ._version import __version__ as VERSION
REVIEW_STATUSES = {
    "terverifikasi", "didukung sebagian", "bertentangan", "tidak ditemukan",
    "belum dapat diverifikasi", "inferensi peneliti/AI", "hipotesis atau rekomendasi",
}
DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s<>\"\[\]]+", flags=re.I)


def normalized_text(value: str):
    """Normalize whitespace and common PDF hyphenation without fuzzy guessing."""
    value = unicodedata.normalize("NFKC", value or "")
    value = value.replace("\u00ad", "")
    value = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", value)
    return normalize(value)


def normalize_doi(value):
    v = str(value or "").strip()
    v = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", v, flags=re.I)
    return v.lower().strip(".,;) ")


def primary_dois(doc):
    """First-page DOI metadata is safer than harvesting reference-list DOIs."""
    if len(doc) == 0:
        return set()
    text = doc[0].get_text("text")
    # A DOI may be split across a line in publisher's metadata.
    text = re.sub(r"(?<=/)\s*\n\s*", "", text)
    results = {normalize_doi(m.group(0)) for m in DOI_RE.finditer(text)}
    return {v for v in results if v}


def _page_number_candidates(page, total):
    explicit, isolated = [], []
    H = page.rect.height
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, txt = b[:5]
        if y0 > 0.19 * H and y1 < 0.82 * H:
            continue
        for line in txt.splitlines():
            line = line.strip()
            m = re.fullmatch(r"(?:(?:Page|Halaman|hlm\.?)\s*)?(\d{1,4})\s+(?:of|dari)\s+(\d{1,4})", line, re.I)
            if m and int(m.group(2)) == total and 1 <= int(m.group(1)) <= 9999:
                explicit.append(int(m.group(1)))
                continue
            m = re.fullmatch(r"(?:Page|Halaman|hlm\.?)\s*(\d{1,4})", line, re.I)
            if m:
                # A literal "Page N" is explicit pagination, except improbable values.
                if int(m.group(1)) <= 5000:
                    explicit.append(int(m.group(1)))
                continue
            m = re.fullmatch(r"(\d{1,4})", line)
            if m and 1 <= int(m.group(1)) <= 5000:
                isolated.append(int(m.group(1)))
    return explicit, isolated


def detect_printed_pages(doc):
    """Consensus over a document; do not treat a lone year/footer as pagination.

    Returns page-number values with the evidence method. Page labels are only
    used when plausible and corroborated by visible pagination.
    """
    n = len(doc)
    if not n:
        return []
    parsed = [_page_number_candidates(doc[i], n) for i in range(n)]
    values = [None] * n
    methods = [tr('belum dapat ditentukan')] * n
    for i, (explicit, _) in enumerate(parsed):
        if len(set(explicit)) == 1 and explicit:
            values[i] = explicit[0]
            methods[i] = tr('nomor eksplisit pada halaman')
    # Require corroboration by at least two distinct pages with same page offset.
    offset_support = defaultdict(set)
    for i, (explicit, isolated) in enumerate(parsed):
        for v in set(explicit + isolated):
            offset_support[v - i].add(i)
    plausible_offsets = {offset for offset, pages in offset_support.items() if len(pages) >= 2}
    if plausible_offsets:
        ranked = sorted(plausible_offsets, key=lambda off: (-len(offset_support[off]),off))
        # Reject conflicting equally supported sequences rather than guessing.
        if len(ranked) == 1 or len(offset_support[ranked[0]]) > len(offset_support[ranked[1]]):
            offset = ranked[0]
            for i, (explicit, isolated) in enumerate(parsed):
                candidate = i + offset
                if candidate < 1 or candidate > 5000:
                    continue
                if values[i] is None and candidate in isolated:
                    values[i] = candidate
                    methods[i] = tr('angka marginal konsisten antarahalaman')
                elif values[i] is None and not isolated and not explicit:
                    # Infer only if at least two nearby pages corroborate, and
                    # the page is within the span of evidence or immediately next.
                    nearby = [j for j in offset_support[offset] if abs(j - i) <= 2]
                    if len(nearby) >= 2:
                        values[i] = candidate
                        methods[i] = tr('inferensi urutan dari halaman tetangga')
    # PDF page label is an additional source, but only for a plausible numeric sequence.
    labels = [doc[i].get_label() for i in range(n)]
    numeric = [int(x) if re.fullmatch(r"\d{1,4}",x or "") else None for x in labels]
    if n >= 2 and all(v is not None and 1 <= v <= 5000 for v in numeric):
        if all(numeric[i+1] == numeric[i] + 1 for i in range(n-1)):
            # Corroborate with at least one visibly printed page.
            corroborated = any(values[i] == numeric[i] and values[i] is not None for i in range(n))
            if corroborated:
                for i, v in enumerate(numeric):
                    if values[i] is None:
                        values[i] = v
                        methods[i] = tr('label PDF didukung penomoran terlihat')
    return [{"printed_page":str(v) if v is not None else None,"printed_page_method":methods[i]} for i,v in enumerate(values)]


def printed_page_candidate(page):
    """Deprecated single-page checker: never assert unsupported numeric footer."""
    explicit, _ = _page_number_candidates(page, 1)
    return str(explicit[0]) if len(set(explicit)) == 1 and explicit else None


def _safe_search_quads(page, phrase):
    """Search literal text; support only equivalent Unicode ligature spellings.

    Coordinate output comes from PDFium's character geometry.
    """
    q = page.search_for(phrase, quads=True)
    if q:
        return q
    flat = re.sub(r'\s+', ' ', phrase).strip()
    if flat != phrase and normalized_text(flat) == normalized_text(phrase):
        q = page.search_for(flat, quads=True)
        if q:
            return q
    variants = {phrase}
    for plain, ligature in (("ffi", "\ufb03"), ("ffl", "\ufb04"), ("fi", "\ufb01"), ("fl", "\ufb02")):
        candidates = set(variants)
        for item in variants:
            if plain in item:
                candidates.add(item.replace(plain, ligature))
        variants = set(sorted(candidates)[:32])
    for variant in sorted(variants):
        if variant == phrase or normalized_text(variant) != normalized_text(phrase):
            continue
        quads = page.search_for(variant, quads=True)
        if quads:
            return quads
    return []


def _text_matches(doc, excerpt):
    """One occurrence per page is required before any coordinates are trusted."""
    phrase = (excerpt or "").strip()
    if len(phrase) < 12 or len(phrase.split()) < 3:
        return [], tr('anchor terlalu pendek')
    matches = []
    norm_phrase = normalized_text(phrase)
    for i, page in enumerate(doc):
        page_norm = normalized_text(page.get_text("text"))
        count = page_norm.count(norm_phrase)
        if count > 1:
            return [], tr('anchor berulang pada halaman yang sama')
        if count != 1:
            continue
        quads = _safe_search_quads(page, phrase)
        if not quads:
            return [], tr('teks ditemukan tetapi koordinat tidak ditemukan')
        # Reject a phrase that PDF extraction joins across reversed columns or
        # widely separated regions. A single text sequence is not visual proof.
        if len(quads) > 1 and (getattr(page, 'rotation', 0) != 0 or any(
            next_q.rect.y0 < prev_q.rect.y0 - 3 or
            (abs(next_q.rect.y0 - prev_q.rect.y0) <= 3 and next_q.rect.x0 - prev_q.rect.x1 > 35)
            for prev_q, next_q in zip(quads, quads[1:])
        )):
            return [], tr('koordinat di luar bidang halaman')
        # Search may return more than one quad for wrapped text. Every segment
        # must have sane bounds in the page coordinates.
        bounds_ok = all(q.rect.intersects(page.rect) and q.rect.width > 0 and q.rect.height > 0
                        and page.rect.contains(q.rect) for q in quads)
        if not bounds_ok:
            return [], tr('koordinat di luar bidang halaman')
        matches.append((i, quads))
    if len(matches) > 1:
        return [], tr('anchor muncul pada beberapa halaman')
    if not matches:
        return [], tr('anchor tidak ditemukan pada teks PDF')
    return matches, "unik"


def find_exact_occurrences(doc, excerpt):
    results, status = _text_matches(doc,excerpt)
    return results if status == "unik" else []


@localized
def extract_claims(text):
    """Heuristic sentence boundaries, not an automatic scholarly citation parser."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9\"“])", text.strip())
    return [{"id":f"K{i:03d}","text":s.strip(),"jenis":"parafrasa", "source_pdf":"", "kutipan_asli":""}
            for i,s in enumerate(parts,1) if len(s.strip()) >= 20]


def _resolve_source(c, pdf_root, primary_cache, output_dir=None):
    name = str(c.get("source_pdf") or "").strip()
    requested_doi = normalize_doi(c.get("source_doi") or c.get("doi"))
    root = pdf_root.resolve()
    if name:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or path.suffix.lower() != ".pdf":
            return None, tr('sumber disebut tetapi PDF tidak ditemukan dalam direktori yang diizinkan'), []
        if requested_doi:
            found = primary_cache(path)
            if len(found) != 1 or requested_doi not in found:
                return None, tr('DOI PDF tidak unik/tidak cocok dengan DOI yang diminta; perlu pemeriksaan'), [path.name]
        return path, tr('dipetakan dari nama PDF yang diberikan pengguna'), [path.name]
    if not requested_doi:
        return None, tr('tidak ada nama PDF atau DOI; identifikasi sumber perlu dilakukan peneliti'), []
    # DOI-only discovery, no fuzzy guessing by similar filename or topic.
    candidates = []
    for path in sorted(root.rglob("*.pdf")):
        p = path.resolve()
        if p.stem.endswith("_annotated") or (output_dir and p.is_relative_to(Path(output_dir).resolve())):
            continue
        if not p.is_relative_to(root):
            continue
        found_dois = primary_cache(p)
        if len(found_dois) == 1 and requested_doi in found_dois:
            candidates.append(p)
    if len(candidates) == 1:
        return candidates[0], tr('PDF ditemukan secara unik berdasarkan DOI utama'), [candidates[0].name]
    if len(candidates) > 1:
        return None, tr('lebih dari satu PDF memiliki DOI sama; perlu pilih sumber'), [p.name for p in candidates]
    return None, tr('tidak ada PDF dengan DOI yang diminta dalam direktori'), []


@localized
def audit(claims, pdf_root, out_dir, reviews=None):
    root, out = Path(pdf_root), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if not isinstance(claims,list):
        raise ValueError(tr('Masukan claims harus berupa array JSON.'))
    if reviews is not None and not isinstance(reviews,dict):
        raise ValueError(tr('Masukan reviews harus berupa object JSON berindeks ID klaim.'))
    reviews = reviews or {}
    docs, doi_cache, pages_cache = {}, {}, {}
    outputs, pending_annotations = [], defaultdict(dict)

    def open_doc(path):
        if path not in docs:
            try:
                docs[path] = fitz.open(path)
                if docs[path].needs_pass:
                    docs[path].close()
                    docs[path] = None
            except (fitz.FileDataError, fitz.EmptyFileError, RuntimeError, ValueError):
                docs[path] = None
        return docs[path]

    def source_dois(path):
        if path not in doi_cache:
            d = open_doc(path)
            doi_cache[path] = primary_dois(d) if d else set()
        return doi_cache[path]

    try:
        ids = [str(c.get("id","")) for c in claims if isinstance(c,dict)]
        if any(not v for v in ids) or len(set(ids)) != len(ids) or len(ids) != len(claims):
            raise ValueError(tr('Setiap klaim harus object dengan id unik dan tidak kosong.'))
        for c in claims:
            cid = str(c["id"])
            claim, kind = str(c.get("text") or ""), str(c.get("jenis") or "parafrasa").lower()
            if not claim.strip() or kind not in ("parafrasa","kutipan_langsung"):
                raise ValueError(tr('Klaim {v0} tidak memiliki text/jenis yang valid.',v0=f'{cid}'))
            result = {
                "claim_id":cid,"claim":claim,"jenis":kind,
                "source_pdf":str(c.get("source_pdf") or ""),
                "source_doi":normalize_doi(c.get("source_doi") or c.get("doi")),
                "source_match_status":"belum dipetakan", "source_identity_verified":False,
                "source_match_method":"", "source_candidates":[],
                "status":"belum dapat diverifikasi", "cakupan_keputusan":"belum dinilai",
                "literal_match_status":"belum diperiksa", "anchor_text_match_status":"belum diperiksa",
                "semantic_support_status":"belum dinilai",
                "pdf_sha256":"","pdf_page":None,"printed_page":None,"printed_page_method":tr('belum dapat ditentukan'),
                "pdf_page_label":"", "text_anchor":"", "evidence_locations":[],
                "note":"", "highlight":False,"reviewer":"", "tanggal_audit":now_iso()
            }
            path, source_note, candidates = _resolve_source(c,root,source_dois,output_dir=out)
            result["source_candidates"] = candidates
            result["note"] = source_note
            result["source_match_method"] = source_note
            if not path:
                outputs.append(result)
                continue
            result["source_pdf"] = path.name
            doc = open_doc(path)
            if not doc:
                result["note"] += tr('; PDF gagal dibaca/terenkripsi, periksa secara manual')
                outputs.append(result)
                continue
            result["source_match_status"]="dipetakan"
            result["source_identity_verified"] = bool(result["source_doi"] and
                source_dois(path) == {result["source_doi"]})
            result["pdf_sha256"] = sha256(path)
            if path not in pages_cache:
                pages_cache[path] = detect_printed_pages(doc)
            if not any(p.get_text("text").strip() for p in doc):
                result["note"] += tr('; PDF tidak memiliki teks yang dapat diekstraksi; perlu OCR/manual')
                outputs.append(result)
                continue
            anchors = []
            if kind == "kutipan_langsung":
                q = str(c.get("kutipan_asli") or "")
                if not q.strip() or normalized_text(q) not in normalized_text(claim):
                    result["note"] += tr('; kutipan_asli tidak cocok dengan isi klaim')
                    outputs.append(result)
                    continue
                anchors = [q]
            else:
                raw = c.get("evidence_anchors") or c.get("evidence_anchor") or []
                anchors = [raw] if isinstance(raw,str) else raw if isinstance(raw,list) and all(isinstance(v,str) for v in raw) else []
            if not anchors:
                result["note"] += tr('; belum ada frasa bukti literal untuk lokasi PDF')
                outputs.append(result)
                continue
            anchored = []
            errors = []
            for phrase in anchors:
                matches, reason = _text_matches(doc, str(phrase))
                if not matches:
                    errors.append(reason)
                    continue
                pg, quads = matches[0]
                pnum = pages_cache[path][pg]
                loc = {"pdf_page":pg+1,"printed_page":pnum["printed_page"],
                       "printed_page_method":pnum["printed_page_method"],
                       "pdf_page_label":doc[pg].get_label() or "", "text_anchor":str(phrase),
                       "rects":[[round(q.rect.x0,2),round(q.rect.y0,2),round(q.rect.x1,2),round(q.rect.y1,2)] for q in quads]}
                anchored.append(loc)
                key = (pg, tuple(tuple(round(x,2) for x in rect) for rect in loc["rects"]))
                pending_annotations[path].setdefault(key,{"quads":quads,"claim_ids":set()})["claim_ids"].add(cid)
            if anchored:
                result["highlight"] = True
                result["evidence_locations"] = anchored
                first = anchored[0]
                for field in ("pdf_page","printed_page","printed_page_method","pdf_page_label","text_anchor"):
                    result[field] = first[field]
                result["literal_match_status"] = "cocok" if not errors else "sebagian anchor cocok"
                result["note"] += tr('; lokasi anchor teks valid ditemukan, dukungan makna belum dinilai')
            else:
                result["literal_match_status"] = "tidak ditemukan" if all("tidak ditemukan" in e for e in errors) else "ambigu atau koordinat tidak valid"
                if kind == "kutipan_langsung" and result["literal_match_status"] == "tidak ditemukan":
                    result["status"] = "tidak ditemukan"
                    result["cakupan_keputusan"] = tr('hanya frasa kutipan tidak ditemukan, bukan pembuktian makna salah')
            if errors:
                result["note"] += tr('; anchor lain memerlukan pemeriksaan: ') + "; ".join(sorted(set(errors)))
            rev = reviews.get(cid)
            if rev:
                status = rev.get("status","")
                if status not in REVIEW_STATUSES or not str(rev.get("reviewer") or "").strip() or not str(rev.get("reason") or "").strip():
                    result["note"] += tr('; penilaian manusia tidak lengkap atau status tidak dikenal, diabaikan')
                elif not path:
                    result["note"] += tr('; penilaian sumber tidak tersedia; keputusan perlu ditinjau')
                else:
                    result["semantic_support_status"] = status
                    result["status"] = status
                    result["reviewer"] = str(rev["reviewer"])
                    result["cakupan_keputusan"] = tr('penilaian manusia; bukan hasil mesin pencocokan teks')
                    result["note"] += tr('; penilaian manusia: ') + str(rev["reason"])
            result["anchor_text_match_status"] = result["literal_match_status"]
            outputs.append(result)

        annotated_files = []
        annotation_integrity = []
        for path, coords in pending_annotations.items():
            doc=docs[path]
            if not doc or not coords:
                continue
            for (pnum,_), info in coords.items():
                page=doc[pnum]
                annot=page.add_highlight_annot(info["quads"])
                ids=", ".join(sorted(info["claim_ids"]))
                annot.set_info(content=tr('EPISTARIUM Vanlan: anchor klaim {v0}; tidak menyatakan dukungan substansi',v0=f'{ids}'))
                annot.update()
            dest = out / (path.stem + "_annotated.pdf")
            check = {"source_pdf":path.name,"annotated_file":dest.name,"status":"gagal",
                     "original_pages":len(doc),"output_pages":None,"text_preserved":False,"warning":""}
            try:
                doc.save(dest, garbage=4, deflate=True)
                # Compare two fresh document instances: in-memory pages that
                # have new annotations can report stale extraction caches.
                with fitz.open(path) as original, fitz.open(dest) as saved:
                    check["output_pages"] = len(saved)
                    check["text_preserved"] = len(saved) == len(original) and all(
                        saved[i].get_text("text") == original[i].get_text("text") for i in range(len(original)))
                if check["text_preserved"]:
                    check["status"]=tr('lulus cek teks dan jumlah halaman')
                    annotated_files.append(dest.name)
                else:
                    raise ValueError(tr('PDF keluaran berbeda jumlah halaman atau lapisan teks'))
            except (fitz.FileDataError, fitz.EmptyFileError, RuntimeError, ValueError, OSError) as exc:
                check["warning"] = tr('Pemeriksaan integritas anotasi gagal: {v0}',v0=f'{type(exc).__name__}')
                if dest.exists():
                    dest.unlink()
                for r in outputs:
                    if r["source_pdf"] == path.name:
                        r["highlight"] = False
                        r["note"] += tr('; PDF anotasi tidak lolos pemeriksaan integritas dan dibatalkan')
            annotation_integrity.append(check)
        save_json(out/"audit.json",{"tool":"Vanlan","version":VERSION,"records":outputs,"annotated_files":annotated_files,
                                    "annotation_integrity":annotation_integrity,
                                    "disclaimer":tr('Status literal dan dukungan semantik adalah dua hal berbeda. PDF beranotasi hanya menunjuk teks.')})
        csv_rows=[]
        for item in outputs:
            row={k:v for k,v in item.items() if k not in ("evidence_locations","source_candidates")}
            row["evidence_pages"] = ";".join(str(x["pdf_page"]) for x in item["evidence_locations"])
            row["source_candidates"] = ";".join(item["source_candidates"])
            csv_rows.append(row)
        save_csv(out/"audit.csv",csv_rows,list(csv_rows[0]) if csv_rows else ["claim_id","status"])
        lines=[tr('# Laporan Vanlan V0.1.1'), "", tr('Highlight adalah lokasi bukti, bukan pernyataan bahwa seluruh klaim benar.'), ""]
        for r in outputs:
            lines += [f"## {r['claim_id']}: {display_status(r['status'])}",tr('Klaim: {v0}',v0=f"{r['claim']}"),
                      f"PDF: {r['source_pdf'] or tr('(tidak terpetakan)')}; DOI: {r['source_doi'] or tr('(tidak ada)')}",
                      tr('Cocok literal: {v0}; Dukungan substansi: {v1}',v0=f"{display_status(r['literal_match_status'])}", v1=f"{display_status(r['semantic_support_status'])}"),
                      tr('Halaman PDF: {v0}; nomor cetak: {v1}',v0=f"{[x['pdf_page'] for x in r['evidence_locations']]}", v1=f"{[x['printed_page'] for x in r['evidence_locations']]}"),
                      tr('Cakupan: {v0}; Peninjau: {v1}',v0=f"{display_status(r['cakupan_keputusan'])}", v1=f"{r['reviewer'] or '-'}"),tr('Catatan: {v0}',v0=f"{r['note']}"),""]
        (out/"laporan.md").write_text("\n".join(lines),encoding="utf-8")
        return outputs
    finally:
        for doc in docs.values():
            if doc:
                doc.close()
