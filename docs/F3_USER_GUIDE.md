# Panduan pengguna Fase III (V0.3.1-alpha, internal)

EPISTARIUM ditujukan untuk platform AI yang dapat memakai skills atau mengadaptasi SKILL.md. Fokus awal OpenCode, Antigravity, Codex, ChatGPT, Claude dan Gemini. Python CLI dapat dijalankan langsung bila agen tidak mendapat akses filesystem.

## Instalasi sederhana
```bash
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -e '.[test]'
python -m pytest -q
```

## Ideon (default ORIGO)
1. Salin `examples/f3_synthetic/origo_research_example.json` lalu ubah `ide_awal`. Input satu kalimat cukup. Tidak perlu formulir RMC.
2. Jalankan `python -m epistarium ideon-design --input examples/f3_synthetic/origo_research_example.json --out private/origo`.
3. Buka DOCX di `private/origo`. Bagian I berisi enam simpul penelitian; Bagian II memuat 21 pertanyaan yang belum dielaborasi.
4. Ubah `mode` menjadi `ELABORATE_21` untuk draf 21 jawaban, `BLUEPRINT` untuk rencana prosedur, atau `REVISION` bersama `--previous-map private/origo/ideon_origo.json` dan objek `perubahan` yang eksplisit. Tidak ada pencarian internet yang dijalankan secara diam-diam.
5. Bila perintah lama memerlukan RMC, opsi `--legacy-rmc` tersedia sementara untuk migrasi. Kode lama bukan standar dokumen utama lagi.

## Quilo
`python -m epistarium quilo-audit --text private/draf.txt --revised private/revisi.txt --out private/quilo`.
Perhatikan `protected_tokens_unchanged` dan `semantic_validity`. Perubahan negasi, aktor, modalitas, angka, DOI dan sitasi diberi peringatan. `semantic_validity=NOT_ASSESSED` tetap berlaku bahkan untuk usulan penyuntingan sederhana.

## Huxley
`python -m epistarium huxley-audit --docx private/naskah.docx --annotate-copy --out private/huxley`.
Salinan Word dapat memiliki highlight dan komentar asli di posisi sitasi dan referensi bermasalah, termasuk teks yang terdiri dari beberapa run. Jika terdapat field sitasi dinamis di tubuh dokumen, Huxley mengeluarkan salinan byte-identik dan mengalihkan masalah ke laporan. Periksa `coverage` untuk bagian yang tidak diproses. `MATCHED` berarti cocok secara bibliografis, bukan dukungan klaim ilmiah.

## Keamanan dan cakupan
Korpus privat, transkrip, daftar pustaka berlisensi, dan PDF penerbit jangan diunggah ke GitHub. Huxley baru mendukung subset APA 7 author-date, bukan semua variasi. Kualitas 21 elaborasi dan revisi makna belum dapat disahkan oleh pemeriksaan sintetik. Uji native pada tiap aplikasi AI dan OS masih diperlukan sebelum klaim kompatibilitas resmi.
