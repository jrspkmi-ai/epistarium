"""Generate only synthetic, fictional research fixtures; no licensed or personal data."""
from pathlib import Path
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor

p=Path(__file__).resolve().parent
p.mkdir(parents=True,exist_ok=True)
(p/'ideon_input.json').write_text(json.dumps({
  'ide':'penggunaan AI dalam diskusi akademik mahasiswa',
  'disiplin':'Ilmu Komunikasi',
  'konteks':'kelas perguruan tinggi (simulasi)',
  'akses_data':{'korpus':'tersedia','informan':'terbatas','organisasi':'belum diverifikasi'},
  'bukti':[{'klaim':'Bukti ilustratif, belum diverifikasi','status':'belum dapat diverifikasi'}],
},ensure_ascii=False,indent=2),encoding='utf8')
(p/'draf.txt').write_text('Perlu diketahui bahwa kegiatan diskusi dinilai sangat penting. ' 
 'Korpus simulasi memuat 20 komentar (Sari, 2023). ' 
 'Penulis menyatakan “perlu verifikasi lebih lanjut”. ' 
 'DOI contoh 10.9999/synthetic.\n',encoding='utf8')
(p/'draf_revisi_angka_salah.txt').write_text('Kegiatan diskusi dinilai penting. ' 
 'Korpus simulasi memuat 200 komentar (Sari, 2023). ' 
 'Penulis menyatakan “perlu verifikasi lebih lanjut”. ' 
 'DOI contoh 10.9999/synthetic.\n',encoding='utf8')
d=Document(); section=d.sections[0]; section.top_margin=Inches(.85);section.bottom_margin=Inches(.8)
normal=d.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(11)
d.add_heading('Naskah Sintetis untuk Uji Huxley',0)
d.add_paragraph('Semua nama, tahun, judul artikel, dan hasil dalam dokumen ini FIKTIF. Dokumen ini hanya untuk menguji pencocokan sitasi dan anotasi.')
d.add_heading('Pembahasan',level=1)
d.add_paragraph('Sari dan Nanda (2023) membahas perilaku diskusi dalam sebuah studi simulasi.')
d.add_paragraph('Penjelasan tambahan (Sari & Nanda, 2023; Putra et al., 2026a) disertakan untuk menguji sitasi berkelompok.')
d.add_paragraph('Penulis tidak menemukan pasangan bibliografi untuk pernyataan Budi (2024).')
d.add_paragraph('Sitasi Putra (2026) bersifat ambigu karena ada dua referensi dengan sufiks a dan b.')
d.add_paragraph('World Health Organization (2023) dicantumkan sebagai contoh penulis lembaga, bukan sumber yang benar-benar digunakan.')
d.add_heading('Daftar Pustaka',level=1)
for text in [
    'Sari, P., & Nanda, H. (2023). Synthetic discussion article A.',
    'Putra, J., Lestari, B., & Kawan, M. (2026a). Synthetic discussion article B.',
    'Putra, J., Lestari, B., & Kawan, M. (2026b). Synthetic discussion article C.',
    'World Health Organization. (2023). Synthetic organization report.',
    'Darma, N. (2022). Synthetic unreferenced article.'
]: d.add_paragraph(text)
d.save(p/'naskah_sintetis.docx')
# Separate fixture with a citation field, deliberately never edited by annotator.
from docx.oxml import OxmlElement
f=Document();paragraph=f.add_paragraph('Budi (2024) tercantum dalam teks. ');run=paragraph.add_run()
field=OxmlElement('w:fldChar');run._r.append(field)
f.add_paragraph('Daftar Pustaka');f.add_paragraph('Sari, P. (2023). Synthetic article.')
f.save(p/'naskah_dengan_field.docx')
(p/'README.md').write_text('Semua nama dan publikasi di sini adalah fiksi untuk pengujian parser. Tidak boleh dipakai sebagai referensi akademik.\n',encoding='utf8')
print('Synthetic fixtures created in',p)
