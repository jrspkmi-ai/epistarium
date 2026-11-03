"""Simple command-line interface for a local agent or a researcher."""
from .i18n import tr, display_status, localized, get_language
import argparse
from datetime import date
from pathlib import Path
from .common import load_json, save_json
import json
import sys
from .i18n import resolve_language, language_context
from . import __version__


def run(argv=None):
    p = argparse.ArgumentParser(prog="epistarium", description=tr('EPISTARIUM: sepuluh persona penelitian dengan provenance bukti'))
    p.add_argument("--version",action="version",version=__version__)
    p.add_argument("--lang",choices=("id","en","auto"),help=tr("Bahasa keluaran: id, en, atau auto"))
    s = p.add_subparsers(dest="command", required=True)
    doctor=s.add_parser("doctor",help=tr('Periksa dependensi, zona waktu, akses tulis dan lokasi skill tanpa jaringan'))
    doctor.add_argument("--out",help=tr('Opsional path JSON laporan lingkungan'))
    extract = s.add_parser("vanlan-extract", help=tr('Ekstraksi kandidat klaim dari file teks'))
    extract.add_argument("--text", required=True)
    extract.add_argument("--out","--output", dest="output",required=True)
    v = s.add_parser("vanlan-audit", help=tr('Audit PDF terarah dari JSON'))
    v.add_argument("--claims", required=True)
    v.add_argument("--pdf-dir", required=True)
    v.add_argument("--out", required=True)
    v.add_argument("--reviews")
    l = s.add_parser("liora-search", help=tr('Pencarian metadata literatur (Crossref)'))
    l.add_argument("--topic", required=True)
    l.add_argument("--scope", default="fenomena",choices=["fenomena","empiris","teori","metode","konsep","phenomenon","empirical","theory","method","concept"])
    l.add_argument("--rows", type=int, default=20)
    l.add_argument("--mailto")
    l.add_argument("--fixture", help=tr('JSON Crossref offline untuk uji'))
    l.add_argument("--timezone", help=tr('Zona IANA, misalnya Asia/Jakarta; default zona mesin'))
    l.add_argument("--as-of", help=tr('Tanggal YYYY-MM-DD untuk replikasi, default hari eksekusi'))
    l.add_argument("--out", required=True)
    a = s.add_parser("agresa-audit", help=tr('Pencocokan bukti indeks resmi yang diarsipkan'))
    a.add_argument("--journals", required=True)
    a.add_argument("--evidence", required=True)
    a.add_argument("--out", required=True)
    r = s.add_parser("retho-retrieve", help=tr('Pemeriksaan akses PDF dan versi naskah (Retho)'))
    r.add_argument("--candidates",required=True)
    r.add_argument("--library",help=tr('JSON peta DOI ke PDF lokal dan hak akses'))
    r.add_argument("--oa-records",help=tr('JSON metadata lokasi OA (bukan bukti hak)'))
    r.add_argument("--download",action="store_true",help=tr('Parameter kompatibilitas lama; unduh otomatis DISABLED di 0.2.2'))
    r.add_argument("--publisher-observations",help=tr('JSON catatan akses dari pemeriksaan manual; tidak membuktikan hak unduh'))
    r.add_argument("--out",required=True)
    d = s.add_parser("domares-read", help=tr('Ekstrak kandidat passage dari PDF full-text Retho'))
    d.add_argument("--articles",required=True)
    d.add_argument("--out",required=True)
    sy = s.add_parser("synthia-review", help=tr('Matriks 20 kolom dan sintesis sementara'))
    sy.add_argument("--readings",required=True)
    sy.add_argument("--template-xlsx",help=tr('Workbook milik pengguna untuk ditambahkan baris tanpa menghapus data'))
    sy.add_argument("--no-xlsx",action="store_true",help=tr('Hanya CSV/JSON, tidak membuat XLSX'))
    sy.add_argument("--out",required=True)
    gd = s.add_parser('f2-gold-evaluate',help=tr('QA privat: bandingkan halaman kandidat Domares dengan workbook review manusia (bukan penilaian semantik)'))
    gd.add_argument('--readings',required=True)
    gd.add_argument('--template-xlsx',required=True)
    gd.add_argument('--out',required=True)
    ide = s.add_parser("ideon-design", help=tr('ORIGO Research Mapping, default QUICK_MAP, ekspor DOCX'))
    ide.add_argument("--input",required=True,help=tr('JSON berisi field ide/topik dan bukti opsional'))
    ide.add_argument("--out",required=True)
    ide.add_argument("--previous-map",help=tr('JSON hasil ORIGO sebelumnya untuk mode REVISION'))
    ide.add_argument("--legacy-rmc",action="store_true",help=tr('Jalur kompatibilitas lama, keluaran RMC tanpa ORIGO'))
    org = s.add_parser("ideon-origo", help=tr('Alias eksplisit IDEON ORIGO, satu DOCX dua bagian'))
    org.add_argument("--input",required=True)
    org.add_argument("--out",required=True)
    org.add_argument("--previous-map")
    qu = s.add_parser("quilo-audit", help=tr('Audit gaya dan pemeriksaan perubahan yang melindungi token bukti'))
    qu.add_argument("--text",required=True)
    qu.add_argument("--revised",help=tr('Opsional teks revisi eksternal untuk dibandingkan'))
    qu.add_argument("--style",help=tr('Opsional JSON preset privat, tidak dikirim ke repositori'))
    qu.add_argument("--preset",choices=("academic-id","academic-en"),help=tr("Preset untuk bahasa naskah. Pilihan ini terpisah dari --lang."))
    qu.add_argument("--out",required=True)
    hu = s.add_parser("huxley-audit", help=tr('Audit sitasi dua arah DOCX dan salinan highlight konservatif'))
    hu.add_argument("--docx",required=True)
    hu.add_argument("--out",required=True)
    hu.add_argument("--annotate-copy",action="store_true")
    hu.add_argument("--online",action="store_true",help=tr('Cari kandidat metadata Crossref, opsional'))
    hu.add_argument("--candidate-fixture",help=tr('Fixture JSON kandidat metadata untuk tes offline'))
    pf = s.add_parser("jorhas-pathfind", help=tr('Path Finding: sumber, data, dan tiga peluang penelitian'))
    pf.add_argument("--idea",required=True)
    pf.add_argument("--out",required=True)
    pf.add_argument("--config",help=tr('JSON sumber dan batas akses opsional'))
    pf.add_argument("--fixture",help=tr('Rekaman sintetis offline untuk pengujian, bukan data empiris'))
    pf.add_argument("--as-of",help=tr('YYYY-MM-DD untuk pengujian/reproduksi'))
    pf.add_argument("--timezone",default="Asia/Jakarta")
    pf.add_argument("--online",action="store_true",help=tr('Izin mencoba adapter eksternal; tidak menerobos pembatas akses'))
    full = s.add_parser("jorhas-full",help=tr('Full Research parsial dengan log pemanggilan sembilan spesialis'))
    full.add_argument("--idea",required=True)
    full.add_argument("--out",required=True)
    full.add_argument("--config",help=tr('JSON ketergantungan, sumber, dan input tiap skill'))
    full.add_argument("--as-of")
    full.add_argument("--timezone",default="Asia/Jakarta")
    full.add_argument("--online",action="store_true")
    for subparser in s.choices.values():
        subparser.add_argument('--lang',choices=('id','en','auto'),default=argparse.SUPPRESS,
                               help=tr('Bahasa keluaran: id, en, atau auto'))
    args = p.parse_args(argv)
    if args.command=='doctor':
        from .doctor import diagnose
        result=diagnose()
        if args.out:save_json(args.out,result)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['execution_status']=='SUCCESS' else 4
    # Import persona dependencies only after handling doctor and --version.
    from . import vanlan, liora, agresa, retho, domares, synthia, ideon, origo, quilo, huxley, jorhas
    from .gold_validation import compare_gold
    from .common import prepare_run_directory, validate_schema
    if getattr(args,'out',None):prepare_run_directory(args.out)
    result_code=0
    if args.command=="jorhas-pathfind":
        r=jorhas.pathfind(args.idea,args.out,fixture=args.fixture,
                         config=load_json(args.config) if args.config else None,
                         as_of=args.as_of,timezone=args.timezone,allow_live=args.online)
        result_code=4 if r['manifest']['status']=='BLOCKED' else 3 if r['manifest']['status']=='PARTIAL' else 0
        print(tr('Jorhas Path Finding: {v0}, {v1} data records, {v2} opsi; lihat {v3}/RUN_MANIFEST.json',v0=f"{display_status(r['manifest']['status'])}", v1=f"{len(r['records'])}", v2=f"{len(r['opportunities'])}", v3=f'{args.out}'))
    elif args.command=="jorhas-full":
        r=jorhas.full_research(args.idea,args.out,
                             config=load_json(args.config) if args.config else None,
                             as_of=args.as_of,timezone=args.timezone,allow_live=args.online)
        result_code=4 if r['deliverable_status']=='INCOMPLETE' else 3
        print(tr('Jorhas Full Research: {v0}; detail {v1}/FULL_RESEARCH_MANIFEST.json',v0=f"{display_status(r['status'])}", v1=f'{args.out}'))
    elif args.command in ("ideon-design","ideon-origo"):
        if args.command=="ideon-design" and args.legacy_rmc:
            r=ideon.export(load_json(args.input),args.out)
            print(tr('Ideon LEGACY RMC: {v0} alternatif; hanya untuk migrasi.',v0=f"{len(r['kandidat_judul'])}"))
        else:
            previous=load_json(args.previous_map) if args.previous_map else None
            r=origo.export(load_json(args.input),args.out,previous=previous)
            result_code=0 if r['docx_status']=='CREATED_AND_REOPENED' else 4
            print(tr('Ideon ORIGO: {v0} alternatif, 21 pertanyaan; DOCX {v1}; lihat {v2}',v0=f"{len(r['titles'])}", v1=f"{r['docx_status']}", v2=f'{args.out}'))
    elif args.command == "quilo-audit":
        r=quilo.audit(quilo.read_manuscript(args.text),args.out,
                     revised=quilo.read_manuscript(args.revised) if args.revised else None,
                     style=load_json(args.style) if args.style else quilo.ENGLISH_STYLE if args.preset=="academic-en" else None)
        print(tr('Quilo: {v0} catatan editorial; lihat {v1}/laporan_quilo.md',v0=f"{len(r['issues'])}", v1=f'{args.out}'))
    elif args.command == "huxley-audit":
        r=huxley.audit(args.docx,args.out,annotate=args.annotate_copy,online=args.online,candidate_fixture=args.candidate_fixture)
        print(tr('Huxley: {v0} sitasi, {v1} referensi; lihat {v2}/laporan_huxley.md',v0=f"{len(r['citations'])}", v1=f"{len(r['references'])}", v2=f'{args.out}'))
    elif args.command == "vanlan-extract":
        text = Path(args.text).read_text(encoding="utf-8")
        result = vanlan.extract_claims(text)
        save_json(args.output,result)
        print(tr('{v0} kandidat klaim. Periksa manual sebelum audit.',v0=f'{len(result)}'))
    elif args.command == "vanlan-audit":
        claims=validate_schema(load_json(args.claims),"vanlan_claims")
        rows = vanlan.audit(claims,args.pdf_dir,args.out,load_json(args.reviews) if args.reviews else None)
        print(tr('Vanlan: {v0} klaim; lihat {v1}/laporan.md',v0=f'{len(rows)}', v1=f'{args.out}'))
    elif args.command == "liora-search":
        rows = liora.search(args.topic,args.out,scope=args.scope,rows=args.rows,mailto=args.mailto,fixture=args.fixture,
                            as_of=date.fromisoformat(args.as_of) if args.as_of else None, timezone_name=args.timezone)
        print(tr('Liora: {v0} kandidat unik; lihat {v1}/candidates.csv',v0=f'{len(rows)}', v1=f'{args.out}'))
    elif args.command == "agresa-audit":
        rows = agresa.audit(load_json(args.journals),load_json(args.evidence),args.out)
        print(tr('Agresa: {v0} hasil basis data; lihat {v1}/laporan.md',v0=f'{len(rows)}', v1=f'{args.out}'))
    elif args.command == "retho-retrieve":
        candidates=load_json(args.candidates)
        library=load_json(args.library) if args.library else None
        records=load_json(args.oa_records) if args.oa_records else None
        publisher_obs=load_json(args.publisher_observations) if args.publisher_observations else None
        rows=retho.build(candidates,args.out,library=library,oa_records=records,download=args.download,publisher_observations=publisher_obs)
        print(tr('Retho: {v0} kandidat; lihat {v1}/retrieval_report.md',v0=f'{len(rows)}', v1=f'{args.out}'))
    elif args.command == "domares-read":
        rows=domares.analyze(load_json(args.articles),args.out)
        print(tr('Domares: {v0} artikel; lihat {v1}/reading_report.md',v0=f'{len(rows)}', v1=f'{args.out}'))
    elif args.command == "f2-gold-evaluate":
        r=compare_gold(load_json(args.readings),args.template_xlsx,args.out)
        print(tr('Evaluasi kandidat halaman: {v0} bidang; akurasi semantik NOT MEASURED',v0=f"{r['fields_evaluated']}"))
    elif args.command == "synthia-review":
        r=synthia.export(load_json(args.readings),args.out,template_xlsx=args.template_xlsx,xlsx=not args.no_xlsx)
        result_code=0 if r["xlsx_status"] in ("created","not_requested") else 4
        print(tr('Synthia: {v0} baris; Excel: {v1}; lihat {v2}/sintesis_sementara.md',v0=f"{len(r['rows'])}", v1=f"{r['xlsx_status']}", v2=f'{args.out}'))

    return result_code


def _selected_language(argv):
    pre=argparse.ArgumentParser(add_help=False)
    pre.add_argument('--lang',choices=('id','en','auto'))
    pre.add_argument('--config')
    pre.add_argument('--input')
    known,_=pre.parse_known_args(argv)
    choice=known.lang
    if choice is None:
        import os
        choice=os.environ.get('EPISTARIUM_LANG')
    if choice is None:
        for path in (known.config,known.input):
            if path and Path(path).is_file():
                try:
                    config=load_json(path)
                    if isinstance(config,dict):choice=config.get('language')
                except (OSError,ValueError):pass
                if choice is not None:break
    return resolve_language(choice or 'auto')


def main(argv=None):
    args=list(sys.argv[1:] if argv is None else argv)
    try:
        language=_selected_language(args)
    except ValueError as exc:
        print(str(exc),file=sys.stderr)
        return 2
    with language_context(language):
        return _main(args)


def _main(argv=None):
    try:
        return run(argv)
    except (ValueError,KeyError,TypeError) as exc:
        print(tr('Input/kontrak tidak valid: ')+str(exc)[:250],file=sys.stderr)
        return 2
    except (ImportError,OSError,RuntimeError) as exc:
        print(tr('Eksekusi terhalang: ')+type(exc).__name__+tr('; jalankan doctor dan periksa input/artefak.'),file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
