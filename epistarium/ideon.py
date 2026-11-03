"""Ideon F3 alpha: evidence-gated RMC 2.0 planning scaffold.

No automated scholarly discovery or verified literature synthesis is claimed here.
Agent-facing SKILL.md specifies the external discovery and human review process.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from pathlib import Path
from .common import save_json, now_iso

CANVAS = ['Topik','Masalah/Gap','Teori','Tujuan','Kebaruan','Metode','Judul Penelitian']
QUESTIONS = [
'Mengapa Anda memilih topik ini?',
'Apa masalah utama (fenomena) yang ingin Anda selesaikan?',
'Apa Das Sein penelitian Anda?',
'Apa Das Sollen penelitian Anda?',
'Apa urgensi penelitian ini dilakukan sekarang?',
'Apa State of the Art penelitian Anda?',
'Apa kebaruan (novelty) dari penelitian Anda?',
'Apa research gap atau kesenjangan penelitian Anda?',
'Apa kontribusi penelitian Anda?',
'Apa batasan penelitian Anda?',
'Apa kerangka konseptual Anda?',
'Teori apa yang Anda gunakan?',
'Apa bedanya dengan penelitian terdahulu?',
'Mengapa menggunakan metode penelitian tersebut?',
'Bagaimana Anda mengumpulkan data?',
'Bagaimana Anda menganalisis data tersebut?',
'Bagaimana memastikan validitas dan reliabilitas data?',
'Jelaskan posisi ontologis penelitian Anda!',
'Jelaskan posisi epistemologis penelitian Anda!',
'Apa aspek aksiologis dari penelitian ini?',
'Apa paradigma penelitian Anda?'
]
EVIDENCE_STATUSES = {'terverifikasi','didukung sebagian','bertentangan','tidak ditemukan','belum dapat diverifikasi','inferensi peneliti/AI','hipotesis atau rekomendasi'}


@localized
def design(spec):
    """Generate explicit tentative alternatives, not false evidence-based research conclusions."""
    if not isinstance(spec,dict): raise ValueError(tr('Input harus objek JSON'))
    topic=str(spec.get('ide') or spec.get('topik') or '').strip()
    if not topic: raise ValueError(tr('Isi field ide atau topik; satu frasa saja boleh.'))
    discipline=str(spec.get('disiplin') or 'belum ditentukan').strip()
    context=str(spec.get('konteks') or '').strip()
    records=spec.get('bukti',[])
    if not isinstance(records,list): raise ValueError(tr('bukti harus array'))
    normalized=[]
    for i, item in enumerate(records):
        if not isinstance(item,dict): raise ValueError(tr('bukti harus array objek'))
        status=item.get('status','belum dapat diverifikasi')
        if status not in EVIDENCE_STATUSES: raise ValueError(tr('status bukti {v0} tidak dikenal',v0=f'{i + 1}'))
        if status=='terverifikasi' and not (item.get('sumber') and item.get('reviewer') and item.get('alasan_verifikasi')):
            status='belum dapat diverifikasi'
        normalized.append({**item,'status':status})
    substantiated=any(r['status']=='terverifikasi' for r in normalized)
    lit=spec.get('kajian_literatur',{})
    reviewed=bool(isinstance(lit,dict) and lit.get('ditinjau_manusia') and lit.get('protokol_pencarian') and lit.get('artikel_terverifikasi'))
    title_context=tr(' di {v0}',v0=f'{context}') if context else ''
    alternatives=[
        {'fokus':tr('Pola dan bentuk aktivitas'),'judul':tr('Pemetaan Pola {v0}{v1}',v0=f'{topic}', v1=f'{title_context}'),
         'masalah':tr('Pola yang dapat diamati dan bagaimana variasinya menurut waktu/unit'),
         'teori':tr('Pilih konsep terukur setelah telaah sumber primer'),
         'metode':tr('Analisis isi/deskriptif, bila korpus dan unit analisis tersedia'),
         'data_yang_dibutuhkan':tr('Korpus atau dokumen dengan periode dan unit jelas'),
         'risiko':tr('Akses data, bias seleksi korpus, batas inferensi')},
        {'fokus':tr('Pemaknaan atau pengalaman aktor'),'judul':tr('Pemaknaan {v0} oleh Aktor Terkait{v1}',v0=f'{topic}', v1=f'{title_context}'),
         'masalah':tr('Bagaimana aktor menafsirkan pengalaman yang terkait fenomena'),
         'teori':tr('Pilih kerangka interpretatif yang sesuai, jangan diasumsikan'),
         'metode':tr('Wawancara kualitatif dengan informan yang relevan'),
         'data_yang_dibutuhkan':tr('Persetujuan dan akses pada partisipan'),
         'risiko':tr('Akses informan, kerahasiaan dan kedalaman wawancara')},
        {'fokus':tr('Praktik atau respons organisasi'),'judul':tr('Strategi dan Praktik Organisasi dalam Menangani {v0}{v1}',v0=f'{topic}', v1=f'{title_context}'),
         'masalah':tr('Keputusan, langkah dan alasan organisasi dalam menghadapi fenomena'),
         'teori':tr('Pilih konsep organisasi/proses sesuai pertanyaan dan bukti'),
         'metode':tr('Studi kasus berbasis dokumen dan wawancara jika akses memungkinkan'),
         'data_yang_dibutuhkan':tr('Dokumen organisasi dan narasumber yang sah'),
         'risiko':tr('Keterbatasan akses internal dan bias informan')}
    ]
    access=spec.get('akses_data',{})
    if not isinstance(access,dict):access={}
    access_keys=['korpus','informan','organisasi']
    for i,a in enumerate(alternatives,1):
        key=access_keys[i-1]
        state=str(access.get(key,'belum diverifikasi'))
        if state not in ('tersedia','terbatas','tidak tersedia','belum diverifikasi'):
            state='belum diverifikasi'
        a.update({'id':f'K{i}','status':'hipotesis atau rekomendasi',
                  'akses_data':state,
                  'kelayakan':(tr('kandidat praktis untuk ditelaah') if state=='tersedia' else tr('akses terbatas; sesuaikan cakupan') if state=='terbatas' else tr('akses tidak tersedia; alternatif perlu diganti') if state=='tidak tersedia' else tr('perlu studi kelayakan')),
                  'kontribusi':tr('potensi, belum diuji terhadap penelitian terdahulu'),
                  'pemeriksaan_kelayakan':{'masalah':a['masalah'], 'teori':a['teori'],
                    'metode':a['metode'],'ruang_lingkup':tr('perlu unit, lokasi dan periode spesifik'),
                    'akses_data':state,'kontribusi':tr('menunggu perbandingan literature review')}})
    # Legacy RMC route retained for callers of ideon.design(). Avoid selecting an
    # unavailable data path when an actually available one is documented.
    chosen=next((a for a in alternatives if a['akses_data']=='tersedia'),
                next((a for a in alternatives if a['akses_data']!='tidak tersedia'), alternatives[0]))
    canvas={
        'Topik':topic,
        'Masalah/Gap':tr('Masalah empiris perlu diuji: {v0}. Belum boleh disebut research gap yang terbukti.',v0=f"{chosen['masalah']}"),
        'Teori':str(spec.get('teori') or spec.get('teori_pilihan') or tr('Belum ditetapkan. Telusuri karya primer dan kesesuaian konsep dengan RQ.')),
        'Tujuan':tr('Mendeskripsikan atau menjelaskan {v0}.',v0=f"{chosen['masalah'].lower()}"),
        'Kebaruan':tr('Kebaruan sementara; perlu perbandingan dengan kajian pustaka yang tervalidasi.') if not reviewed else tr('Kandidat kebaruan tersedia; verifikasi apakah hasil kajian cukup mendukung klaim.'),
        'Metode':str(spec.get('metode') or spec.get('metode_pilihan') or chosen['metode'])+tr('; tentukan populasi, sampling, periode dan prosedur analisis.'),
        'Judul Penelitian':chosen['judul']}
    hints=[
        tr('Fenomena awal: {v0}. Relevansi disiplin {v1} perlu diterangkan melalui unit/aktor dan bukti.',v0=f'{topic}', v1=f'{discipline}'),
        tr('Masalah ilmiah masih berupa calon pertanyaan, bukan masalah faktual yang sudah terkonfirmasi.'),
        tr('Kondisi empiris tidak boleh diisi angka/peristiwa tanpa sumber primer terverifikasi.'),
        tr('Kondisi ideal memerlukan standar atau sumber primer teori yang ditetapkan.'),
        tr('Urgensi memerlukan data tanggal peristiwa dan perubahan terbaru, bukan hanya tanggal publikasi artikel.'),
        tr('Susun perkembangan literatur dari artikel full-text yang telah dibaca dan diaudit.'),
        tr('Novelty masih hipotesis sampai dibandingkan dengan studi yang relevan.'),
        tr('Gap terbatas pada cakupan penelusuran yang terdokumentasi; ketiadaan temuan tidak berarti ketiadaan studi.'),
        tr('Pisahkan sumbangan konseptual dari manfaat untuk aktor secara realistis.'),
        tr('Tetapkan konteks, unit analisis, periode, populasi/informan dan hal yang dikecualikan.'),
        tr('Bangun bagan hubungan antar konsep setelah variabel atau kategori terdefinisi.'),
        tr('Tentukan teori dari sumber primer beserta alasan dan mekanisme penerapannya.'),
        tr('Bandingkan dua atau tiga studi terdekat yang benar-benar telah dibaca.'),
        tr('Pilihan awal {v0}; periksa apakah menjawab jenis RQ.',v0=f"{chosen['metode']}"),
        tr('Rencana pengumpulan: {v0}; periksa akses legal dan etika.',v0=f"{chosen['data_yang_dibutuhkan']}"),
        tr('Susun langkah analisis terinci setelah jenis data dan kode/konstruk ditentukan.'),
        tr('Pilih uji kualitas sesuai desain: reliabilitas pengukuran atau kredibilitas dan audit trail.'),
        tr('Tulis posisi realitas sosial yang selaras dengan objek dan pertanyaan.'),
        tr('Jelaskan cara memperoleh pengetahuan, posisi peneliti, dan pemeriksaan bukti.'),
        tr('Uraikan risiko privasi, persetujuan partisipan, manfaat dan etika.'),
        tr('Pilih dan beri alasan paradigma setelah ontologi, epistemologi serta desain konsisten.')
    ]
    evidence_note=(tr('Ada {v0} catatan bukti dengan adjudikasi tercatat; cakupan dan relevansinya untuk pertanyaan ini tetap harus diperiksa.',v0=f"{sum((x['status'] == 'terverifikasi' for x in normalized))}")
                   if substantiated else tr('Belum ada bukti empiris yang memenuhi syarat verifikasi pada input ini.'))
    responses=[]
    for i,(q,h) in enumerate(zip(QUESTIONS,hints),1):
        q=tr(q)
        response=(tr('Rancangan awal untuk {v0}: {v1} {v2} Sebelum proposal diajukan, lengkapi alasan pilihan dengan data, rujukan primer, dan batas inferensi; jika akses atau informasi belum tersedia, nyatakan keterbatasannya dan tinjau kembali rancangan.',v0=f'{topic}', v1=f'{h}', v2=f'{evidence_note}'))
        responses.append({'nomor':i,'pertanyaan':q,'jawaban_awal':response,
            'status':'hipotesis atau rekomendasi','verifikasi_dibutuhkan':True})
    warnings=[]
    if not substantiated: warnings.append(tr('Belum ada bukti empiris yang diaudit; fenomena dan urgensi tidak dapat diklaim terverifikasi.'))
    if not reviewed: warnings.append(tr('State of the art, research gap dan novelty bersifat sementara sampai literature review terdokumentasi.'))
    if not spec.get('teori'): warnings.append(tr('Teori belum ditentukan; jangan mengarang nama/rujukan teori.'))
    if not spec.get('akses_data'): warnings.append(tr('Akses data belum terkonfirmasi; ketiga alternatif masih bersyarat.'))
    return {'schema_version':'f3.ideon.0.1','generated_at':now_iso(),'topik_awal':topic,'disiplin':discipline,
            'kandidat_judul':alternatives,'pilihan_sementara':chosen['id'],'rmc_2_0':canvas,
            'jawaban_21':responses,'bukti':normalized,'gap_status':'sementara' if not reviewed else tr('memerlukan adjudikasi klaim'),
            'peringatan':warnings,'kesimpulan_status':'DRAFT_PERLU_REVIEW_MANUSIA',
            'template_source':tr('RMC 2.0: 6 bidang, 1 judul, 21 pertanyaan; template asli tidak didistribusikan')}


@localized
def export(spec,out_dir):
    r=design(spec);p=Path(out_dir);p.mkdir(parents=True,exist_ok=True)
    save_json(p/'ideon_rmc.json',r)
    lines=[tr('# Ideon: rancangan RMC 2.0 (DRAFT)'), '',
           tr('Status: belum tervalidasi secara empiris atau metodologis. **Bukan proposal final**.'),'',
           tr('## Tiga kandidat judul'),'']
    for a in r['kandidat_judul']:
        lines += [f"### {a['id']}. {a['judul']}",tr('Fokus: {v0}. Metode kandidat: {v1}.',v0=f"{a['fokus']}", v1=f"{a['metode']}"),
                  tr('Akses data: {v0}. Kebutuhan: {v1}. Risiko: {v2}.',v0=f"{a['akses_data']}", v1=f"{a['data_yang_dibutuhkan']}", v2=f"{a['risiko']}"),'']
    lines+=[tr('## RMC 2.0 (konsep sementara)'),'']
    for k,v in r['rmc_2_0'].items():lines += [f'**{k}:** {v}','']
    lines+=[tr('## 21 pertanyaan: kerangka elaborasi yang harus ditinjau'),'']
    for row in r['jawaban_21']:lines += [f"### {row['nomor']:02d}. {row['pertanyaan']}",row['jawaban_awal'],f"*Status: {row['status']}.*",'']
    lines+=[tr('## Keterbatasan'),'']+[f'- {x}' for x in r['peringatan']]
    (p/'rancangan_rmc.md').write_text('\n'.join(lines),encoding='utf8')
    return r
