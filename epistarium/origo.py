"""ORIGO IRFS v1: evidence-conservative research map and DOCX renderer.

No LLM inference, API search, RMC template replication or full-text claim.
No fabricated facts; explicit user constraints are immutable except in REVISION.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language, normalize_aliases, ORIGO_ALIASES, NODE_ALIASES
import json
import re
from pathlib import Path
from .common import save_json, now_iso, xml_safe_copy

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

BASE = Path(__file__).resolve().parent
QUESTIONS = json.loads((BASE/'data/origo_questions.json').read_text(encoding='utf-8'))['questions']
MODES={'QUICK_MAP','ELABORATE_21','BLUEPRINT','REVISION'}
NODE_KEYS=['realitas_fenomena','fokus_penelitian','landasan_teori','arah_metodologi','potensi_kebaruan','alternatif_judul']
NODE_NAMES=['01. Realitas Fenomena','02. Fokus Penelitian','03. Landasan Teori','04. Arah Metodologi','05. Potensi Kebaruan','06. Alternatif Judul']
MAP_TO_SPEC={'realitas_fenomena':'fenomena','fokus_penelitian':'fokus','landasan_teori':'teori_pilihan','arah_metodologi':'metode_pilihan','potensi_kebaruan':'potensi_kebaruan'}


def _value(spec,*keys):
    for key in keys:
        v=spec.get(key)
        if isinstance(v,str) and v.strip():return v.strip()
    return ''


def _access(spec):
    raw=spec.get('akses_data') or {}
    if not isinstance(raw,dict):raise ValueError(tr('akses_data harus objek status akses'))
    def state(keys):
        s=' '.join(str(v).casefold() for k,v in raw.items() if any(x in k.casefold() for x in keys))
        if any(x in s for x in ['tidak tersedia','tidak ada','mustahil','ditolak','belum bisa','belum tersedia','unavailable','not available','not yet available','no access','denied','impossible']):return 'tidak tersedia'
        if any(x in s for x in ['tersedia','dapat diakses','diizinkan','available','accessible','authorized']):return 'tersedia'
        if any(x in s for x in ['terbatas','izin','persetujuan','restricted','limited','permission','consent']):return 'terbatas'
        return 'belum diverifikasi'
    return raw, {'korpus':state(['korpus','arsip','dokumen','observasi','story','corpus','archive','document','observation']),
                 'informan':state(['informan','mahasiswa','wawancara','partisipan','participant','interview','student']),
                 'organisasi':state(['organisasi','internal','perusahaan','organization','company'])}


@localized
def build(spec, previous=None):
    if not isinstance(spec,dict):raise ValueError(tr('Input ORIGO harus objek JSON'))
    spec=normalize_aliases(spec,ORIGO_ALIASES)
    if isinstance(spec.get('perubahan'),dict):spec['perubahan']=normalize_aliases(spec['perubahan'],NODE_ALIASES)
    idea=_value(spec,'ide_awal','ide','topik')
    if len(idea)<3:raise ValueError(tr('Satu ide minimal tiga karakter diperlukan'))
    mode=str(spec.get('mode','QUICK_MAP')).upper()
    if mode not in MODES:raise ValueError(tr('Mode tidak dikenal: {v0}',v0=f'{mode}'))
    if mode=='REVISION' and isinstance(previous,dict):
        inherited={'teori_pilihan':'teori_pengguna','paradigma':'paradigma_pengguna','metode_pilihan':'metode_pengguna',
                   'pertanyaan_penelitian':'rq_pengguna','akses_data':'akses_data'}
        spec={**{k:previous.get(v) for k,v in inherited.items() if k not in spec and previous.get(v)},**spec}
    count=spec.get('judul_count',3)
    if not isinstance(count,int) or not 1<=count<=7:raise ValueError(tr('judul_count harus integer 1-7'))
    raw_access, a = _access(spec)
    theory=_value(spec,'teori_pilihan','teori')
    paradigm=_value(spec,'paradigma')
    method=_value(spec,'metode_pilihan','metode')
    focus=_value(spec,'fokus')
    phenomenon=_value(spec,'fenomena')
    rq=_value(spec,'pertanyaan_penelitian','rq','research_question')
    unit=_value(spec,'unit_analisis')
    constraints=_value(spec,'catatan_pengguna')
    checked=[]
    user_answers=spec.get('jawaban_21') or {}
    if not isinstance(user_answers,(dict,list)):raise ValueError(tr('jawaban_21 harus objek ID ke jawaban atau array objek'))
    if isinstance(user_answers,list):user_answers={str(x.get('id')):x.get('jawaban',x.get('answer','')) for x in user_answers if isinstance(x,dict)}
    if not phenomenon:checked.append({'check':'fenomena-fokus','status':'BUTUH_BUKTI','note':tr('Fenomena berdasarkan ide pengguna, belum diverifikasi secara empiris.')})
    else:checked.append({'check':'fenomena-fokus','status':'TINJAU_MANUSIA','note':tr('Fenomena diberikan pengguna; kebenaran dan hubungan ke fokus belum diuji otomatis.')})
    checked.append({'check':'teori-fokus','status':'TINJAU_MANUSIA' if theory else 'TEORI_BELUM_DITETAPKAN',
                    'note':tr('Teori pengguna dipertahankan; penerapannya harus dicek melalui sumber primer.') if theory else tr('Belum ada teori yang dapat dinilai.')})
    corpus_unavailable=a['korpus']=='tidak tersedia'; interview_available=a['informan']=='tersedia'
    is_corpus_method=bool(re.search(r'\b(korpus|corpus|content analysis|analisis isi|analisis wacana|discourse|network analysis|digital trace|crawling|scrap)',method,re.I))
    conflict=bool(is_corpus_method and corpus_unavailable)
    checked.append({'check':'metode-akses','status':'KONFLIK' if conflict else 'TINJAU_MANUSIA',
        'note':tr('Metode berbasis korpus ditetapkan tetapi korpus tidak tersedia; jangan menggantinya diam-diam.') if conflict else tr('Akses harus dikonfirmasi pada unit data yang dipakai.')})
    checked.append({'check':'kebaruan-literatur','status':'BELUM_TERVERIFIKASI',
        'note':tr('Tidak ada pemeriksaan literatur otomatis. Potensi kebaruan bukan research gap yang sudah teruji.')})
    if conflict:method_text=tr('{v0}. KONFLIK: korpus dinyatakan tidak tersedia. Perlu revisi akses atau metode berdasarkan keputusan pengguna.',v0=f'{method}')
    elif method:method_text=tr('{v0}. Akses data: {v1}. Rincian sampling dan analisis menunggu pengujian desain.',v0=f'{method}', v1=f'{json.dumps(raw_access, ensure_ascii=False)}')
    elif corpus_unavailable and interview_available:method_text=tr('Opsi awal: wawancara kualitatif karena akses informan tercatat tersedia; desain, persetujuan dan pemilihan partisipan perlu diperiksa.')
    elif a['korpus']=='tersedia':method_text=tr('Opsi awal: analisis dokumen/korpus dengan unit, periode dan etika pengumpulan yang ditetapkan setelah verifikasi akses.')
    else:method_text=tr('Metode belum ditetapkan; periksa jenis pertanyaan, jenis data, akses, unit analisis, serta izin penelitian.')
    nodes={
      'realitas_fenomena':(phenomenon + tr(' [Pernyataan pengguna; belum diverifikasi independen.]')) if phenomenon else tr('Ide awal pengguna: {v0}. Peristiwa, populasi, waktu, dan bukti aktual belum diperiksa.',v0=f'{idea}'),
      'fokus_penelitian':(focus or tr('Merumuskan fokus penelitian seputar {v0} berdasarkan unit dan konteks yang perlu ditentukan.',v0=f'{idea}')) + (tr(' Unit analisis: {v0}.',v0=f'{unit}') if unit else tr(' Unit analisis perlu dipastikan.')) + (tr(' Pertanyaan penelitian pengguna: {v0}.',v0=f'{rq}') if rq else ''),
      'landasan_teori':(tr('Teori yang dipilih pengguna: {v0}.',v0=f'{theory}') if theory else tr('Teori belum dipilih; evaluasi kecocokan dengan fokus dan sumber primer diperlukan.')) + (tr(' Paradigma pilihan pengguna: {v0}.',v0=f'{paradigm}') if paradigm else '') + tr(' Status: kesesuaian konsep memerlukan audit literatur.'),
      'arah_metodologi':method_text,
      'potensi_kebaruan':tr('Dugaan kontribusi pada konteks/fokus penelitian yang ditentukan. Kebaruan dan research gap belum dapat ditetapkan tanpa telaah pustaka yang terlacak.'),
    }
    topic=focus or idea
    # Alternatives differ in unit/question rather than only surface wording.
    options=[
      {'fokus':'pola/praktik','judul':tr('Pemetaan Praktik {v0}',v0=f'{topic}'), 'metode':tr('analisis dokumen atau pengamatan yang berizin'),'akses':a['korpus']},
      {'fokus':tr('pemaknaan aktor'),'judul':tr('Pemaknaan {v0} oleh Partisipan Terkait',v0=f'{topic}'),'metode':tr('wawancara kualitatif'),'akses':a['informan']},
      {'fokus':tr('keputusan organisasi'),'judul':tr('Pengambilan Keputusan Organisasi dalam {v0}',v0=f'{topic}'),'metode':tr('studi kasus organisasi'),'akses':a['organisasi']},
      {'fokus':tr('perbandingan proses'),'judul':tr('Perbandingan Proses {v0} pada Dua Konteks',v0=f'{topic}'),'metode':tr('studi kasus komparatif'),'akses':tr('perlu konfirmasi lintas kasus')},
      {'fokus':tr('dinamika waktu'),'judul':tr('Perkembangan Temporal {v0}',v0=f'{topic}'),'metode':tr('analisis longitudinal'),'akses':a['korpus']},
      {'fokus':tr('hubungan antarkonsep'),'judul':tr('Hubungan Konsep dalam {v0}',v0=f'{topic}'),'metode':tr('survei bila variabel dapat dioperasionalkan'),'akses':tr('perlu sampel yang memadai')},
      {'fokus':tr('praktik interpretasi'),'judul':tr('Pengalaman dan Interpretasi {v0}',v0=f'{topic}'),'metode':tr('wawancara mendalam'),'akses':a['informan']},
    ]
    # Preserve user-supplied method as a requirement, not stealth replace;
    # recommend orientation only if the original input did not fix a method.
    for item in options:
        item['status']='DRAF_PERLU_REVIEW'
        item['konsekuensi']=tr('Alternatif: {v0}; status akses: {v1}.',v0=f"{item['metode']}", v1=f"{display_status(item['akses'])}")
        if item['akses']=='tidak tersedia':item['konsekuensi']+=tr(' Tidak layak dipilih tanpa perubahan akses.')
        if method:item['konsekuensi']+=tr(' Metode pengguna tetap: {v0}; perubahan memerlukan persetujuan.',v0=f'{method}')
    feasible=[x for x in options if x['akses']=='tersedia']
    preferred=(feasible[0] if feasible else next((x for x in options if x['akses']!='tidak tersedia'),options[0]))
    for i,item in enumerate(options):item['id']=f'K{i+1}'
    if method and conflict:preferred=None
    if mode=='REVISION':
        if not isinstance(previous,dict):raise ValueError(tr('REVISION memerlukan previous_map JSON yang telah disetujui'))
        previous_nodes=previous.get('nodes') or {}
        if not isinstance(previous_nodes,dict):raise ValueError(tr('previous_map tidak memiliki nodes yang sah'))
        updates=spec.get('perubahan') or {}
        if not isinstance(updates,dict):raise ValueError(tr('perubahan harus objek node -> teks'))
        # Only explicitly changed nodes; preserve other prior map values.
        for node in NODE_KEYS[:-1]:
            if node not in updates and node in previous_nodes:nodes[node]=previous_nodes[node]
        for node,value in updates.items():
            if node in NODE_KEYS[:-1] and isinstance(value,str) and value.strip():nodes[node]=value.strip()
        if 'alternatif_judul' not in updates and isinstance(previous.get('titles'),list):options=previous['titles']
    output={'language':get_language(),'schema_version':'epistarium.origo.ideon.rfs.v1','generated_at':now_iso(),'mode':mode,'ide_awal':idea,
        'bidang_ilmu':_value(spec,'bidang_ilmu','disiplin'),'jenjang':_value(spec,'jenjang'),
        'nodes':nodes,'titles':options[:count],'preferred_title':preferred['id'] if preferred else None,
        'checks':checked,'source_assessment':'INPUT_PENGGUNA_DAN_INFERENSI_TENTATIF','literature_status':'USER_INPUT_NOT_INDEPENDENTLY_AUDITED' if spec.get('literatur_terverifikasi') else 'NOT_RUN',
        'paradigma_pengguna':paradigm,'teori_pengguna':theory,'metode_pengguna':method,'rq_pengguna':rq,
        'akses_data':raw_access,'revision_id':str(spec.get('revision_id') or ''),
        'revision_notes':_value(spec,'perubahan_pembimbing'),
        'changed_nodes':list((spec.get('perubahan') or {}).keys()) if mode=='REVISION' else [],
        'status':'DRAFT_PERLU_REVIEW_MANUSIA', 'questions':[]}
    for q in QUESTIONS:
        q={**q,'title':tr(q['title'])}
        user_answer=user_answers.get(q['id'])
        if mode=='QUICK_MAP':answer=tr('Belum dielaborasi.')
        elif isinstance(user_answer,str) and user_answer.strip():
            answer=user_answer.strip()
        else:
            k=q['map_node']; v=nodes.get(k,'')
            if q['id'] in ('Q06','Q07','Q08','Q13'):
                answer=tr('Belum dapat disimpulkan dari data ini. Perlu tinjauan literatur terlacak dan pembandingan studi.')
            elif q['id'] in ('Q03','Q05') and not phenomenon:
                answer=tr('Bukti empiris dan periode fenomena belum tersedia. Tidak ada data atau angka yang diasumsikan.')
            elif q['id'] in ('Q18','Q19','Q21') and not paradigm:
                answer=tr('Paradigma belum ditetapkan oleh pengguna; pilihan memerlukan konsistensi ontologi, epistemologi dan metode.')
            else:answer=tr('Rancangan sementara berdasarkan input: {v0} Kesimpulan memerlukan bukti dan keputusan peneliti.',v0=f'{v}')
        output['questions'].append({'id':q['id'],'question':q['title'],'answer':answer,
                  'status':'BELUM_DIELABORASI' if mode=='QUICK_MAP' else ('INPUT_PENGGUNA_BELUM_AUDIT' if isinstance(user_answer,str) and user_answer.strip() else 'DRAF_PERLU_REVIEW'), 'node':q['map_node']})
    if mode=='BLUEPRINT':output['blueprint']={'status':'DRAF_TANPA_EKSEKUSI','steps':[tr('Periksa ketersediaan data dan etika'),tr('Telusuri literatur menggunakan Liora jika ada akses'),tr('Periksa artikel dan metode melalui Retho/Domares/Synthia'),tr('Revisi map berdasarkan temuan terverifikasi')],'tools_called':[]}
    return output


def _doc(result):
    doc=Document();s=doc.sections[0]
    s.page_width=Inches(8.27);s.page_height=Inches(11.69)
    s.top_margin=Inches(.8);s.bottom_margin=Inches(.9);s.left_margin=Inches(.83);s.right_margin=Inches(.83)
    # Reserve enough body space above the footer across Word-compatible renderers.
    s.header_distance=Inches(.3);s.footer_distance=Inches(.3)
    normal=doc.styles['Normal'];normal.font.name='Aptos';normal.font.size=Pt(9);normal.font.color.rgb=RGBColor(0,0,0)
    normal.paragraph_format.space_after=Pt(4)
    for nm,size in [('Title',17),('Heading 1',12),('Heading 2',10)]:
        x=doc.styles[nm];x.font.name='Aptos';x.font.size=Pt(size);x.font.bold=True;x.font.color.rgb=RGBColor(0,0,0)
        x.paragraph_format.space_before=Pt(7);x.paragraph_format.space_after=Pt(4);x.paragraph_format.keep_with_next=True
    # Remove inherited title borders from the installed default document template.
    from docx.oxml.ns import qn
    for border in list(doc.styles['Title']._element.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
    header=s.header.paragraphs[0];header.text='EPISTARIUM ORIGO  |  IDEON RESEARCH FORMATION SYSTEM';header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    footer=s.footer.paragraphs[0];footer.text=tr('ORIGO v1.0.0  |  Draf untuk pemeriksaan, belum proposal final');footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    title_paragraph=doc.add_paragraph('EPISTARIUM ORIGO',style='Title')
    for border in list(title_paragraph._p.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
    doc.add_paragraph(tr('Pemetaan Penelitian (Research Mapping)'))
    doc.add_paragraph(tr('Mode: {v0}  |  Status: DRAF  |  Tanggal: {v1}',v0=f"{result['mode']}", v1=f"{result['generated_at'][:10]}"))
    doc.add_paragraph(tr('Ide awal: {v0}',v0=f"{result['ide_awal']}"))
    doc.add_heading(tr('Bagian I. ORIGO Pemetaan Penelitian'),level=1)
    for key,title in zip(NODE_KEYS,NODE_NAMES):
        doc.add_heading(tr(title),level=2)
        if key=='alternatif_judul':
            for i,item in enumerate(result['titles'],1):
                p=doc.add_paragraph(); r=p.add_run(f"{i}. {item['judul']}");r.bold=True
                doc.add_paragraph(tr('Implikasi: ')+item['konsekuensi'])
        else:doc.add_paragraph(result['nodes'][key])
    doc.add_paragraph(tr('Catatan Ideon: ')+('; '.join(c['note'] for c in result['checks'] if c['status'] in ('KONFLIK','BELUM_TERVERIFIKASI','TEORI_BELUM_DITETAPKAN')))[:400])
    doc.add_page_break();doc.add_heading(tr('Bagian II. ORIGO 21 Langkah Elaborasi'),level=1)
    doc.add_paragraph(tr('Jawaban masih draf; sumber dan keputusan metodologis harus diperiksa sebelum penggunaan formal.'))
    for q in result['questions']:
        p=doc.add_paragraph(style='Normal')
        p.paragraph_format.space_after=Pt(3 if result['mode']=='QUICK_MAP' else 2)
        run=p.add_run(f"{q['id']}  {q['question']}");run.bold=True
        if result['mode']=='QUICK_MAP':
            x=p.add_run(tr('  |  Belum dielaborasi'));x.italic=True
        else:
            p.paragraph_format.keep_with_next=True
            a=doc.add_paragraph(q['answer']);a.paragraph_format.space_after=Pt(5)
    doc.core_properties.title=tr('ORIGO Pemetaan Penelitian dan 21 Langkah Elaborasi')
    doc.core_properties.author='EPISTARIUM'
    return doc


@localized
def export(spec,out_dir,*,previous=None):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    result=build(spec,previous=previous)
    if spec.get('provenance_context'):result['provenance_context']=spec['provenance_context']
    safe=re.sub(r'[^a-zA-Z0-9]+','_',result['ide_awal']).strip('_')[:42] or 'Research'
    docpath=out/f'EPISTARIUM_ORIGO_Research_Mapping_{safe}_v01.docx'
    save_json(out/'ideon_origo.json',result)
    try:
        sanitation=[]
        export_copy=xml_safe_copy(result,sanitation)
        save_json(out/'sanitization_audit_docx.json',{'scope':'DOCX export copy only',
                  'items':sanitation,'total_replacements':sum(x['replacements'] for x in sanitation)})
        doc=_doc(export_copy);doc.save(docpath)
        # Reopen to verify DOCX logical content; visual QA remains separate.
        reopened=Document(docpath)
        headings=[p.text for p in reopened.paragraphs if p.style.name=='Heading 2']
        qids=[p.text[:3] for p in reopened.paragraphs if p.text.startswith('Q') and len(p.text)>3]
        if headings[:6]!=[tr(n) for n in NODE_NAMES] or qids!=[f'Q{i:02}' for i in range(1,22)]:
            raise RuntimeError(tr('Struktur DOCX tidak sesuai spesifikasi enam simpul dan 21 pertanyaan'))
        result['docx_status']='CREATED_AND_REOPENED';result['docx_path']=str(docpath)
    except Exception as exc:
        result['docx_status']='DOCX_NOT_AVAILABLE/BLOCKED';result['docx_error']=type(exc).__name__+': '+str(exc)
    save_json(out/'ideon_origo.json',result)
    (out/'ringkasan_origo.md').write_text('# EPISTARIUM ORIGO\n\n'+
        f"Mode: {result['mode']}. Status: {result['status']}. DOCX: {result['docx_status']}.\n\n"+
        '\n'.join(f'- {n}: {result["nodes"].get(k,"[lihat daftar judul]")}' for k,n in zip(NODE_KEYS,[tr(n) for n in NODE_NAMES])),encoding='utf-8')
    return result
