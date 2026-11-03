[English](../en/FIRST_RESEARCH.md) | Bahasa Indonesia

<!-- section: purpose -->
# Penelitian Pertama dalam EPISTARIUM

Tutorial ini memakai contoh sintetis yang boleh didistribusikan dari proyek. Tidak diperlukan login, API eksternal, atau PDF jurnal berlisensi.
Topiknya komunikasi kampus dan penggunaan AI oleh mahasiswa. Perlakukan setiap rekaman dan rancangan sebagai bahan latihan.

Pasang melalui panduan [Windows](install/windows.md), [macOS](install/macos.md), atau [Linux](install/linux.md).
Baca [gerbang lisensi](LICENSING.md). Buka root proyek dan jalankan doctor terlebih dahulu.

<!-- section: ask -->
## Minta bantuan agen

ID: "Gunakan Jorhas untuk memetakan bukti penggunaan AI oleh mahasiswa. Jalankan contoh sintetis lokal, lalu jelaskan batasnya."

EN: "Use Jorhas to map evidence about student AI use. Run the local synthetic example and explain its limits."

Minta agen membaca .agents/skills/jorhas-master-diving/SKILL.md dan panduan bahasa yang sesuai.
Jika discovery native tidak tersedia, ini penggunaan instruksi manual. Langkah ini tidak memasang skill atau memberi akses terminal.
Pilih [panduan platform](INDEX.md) untuk pengaturan native. Semua perintah juga dapat dijalankan langsung.

<!-- section: run -->
## Jalankan alur sintetis

Gunakan perintah dalam urutan berikut. Semua jalur relatif terhadap root proyek lengkap.
Pada Windows, ganti .venv/bin/python dengan .\.venv\Scripts\python.exe. Argumennya tetap sama.

```bash
.venv/bin/python -m epistarium jorhas-pathfind --idea 'Student AI use' --fixture examples/bilingual/pathfinder.en.json --lang en --as-of 2026-11-03 --out private/first-research/path
.venv/bin/python -m epistarium ideon-origo --input examples/bilingual/origo.en.json --lang en --out private/first-research/map
.venv/bin/python -m epistarium liora-search --topic 'University communication' --fixture examples/f4_synthetic/full_crossref.json --as-of 2026-11-03 --lang en --out private/first-research/liora
.venv/bin/python -m epistarium retho-retrieve --candidates private/first-research/liora/candidates.json --library examples/f2_synthetic/library.json --lang en --out private/first-research/retho
.venv/bin/python -m epistarium domares-read --articles private/first-research/retho/articles.json --lang en --out private/first-research/domares
.venv/bin/python -m epistarium synthia-review --readings private/first-research/domares/critical_readings.json --lang en --out private/first-research/synthia
.venv/bin/python -m epistarium agresa-audit --journals examples/journals.json --evidence examples/index_evidence.json --lang en --out private/first-research/agresa
.venv/bin/python -m epistarium vanlan-audit --claims examples/claims.json --pdf-dir examples/pdfs --lang en --out private/first-research/vanlan
.venv/bin/python -m epistarium quilo-audit --text examples/f3_synthetic/draf.txt --lang en --out private/first-research/quilo
.venv/bin/python -m epistarium huxley-audit --docx examples/f3_synthetic/naskah_sintetis.docx --annotate-copy --lang en --out private/first-research/huxley
.venv/bin/python -m epistarium jorhas-full --idea 'University communication' --config examples/bilingual/full.en.json --lang en --as-of 2026-11-03 --out private/first-research/full
```

Perintah pertama mengembalikan 3/PARTIAL. Baca hasil itu, lalu lanjutkan ke perintah berikutnya.
Perintah terakhir juga mengembalikan 3/PARTIAL. Jangan menggabungkan perintah memakai && karena status parsial memang diharapkan.
Perintah antara mengembalikan 0 ketika berkas keluaran dibuat. Baca pula status artefaknya.
Untuk laporan Indonesia, ganti --lang en menjadi --lang id. Gunakan folder privat berbeda saat mengulang tutorial.
Bahasa naskah tetap seperti sumbernya. Pilih --preset academic-en hanya untuk naskah Inggris.

<!-- section: read -->
## Baca hasilnya

Buka private/first-research melalui pengelola berkas. Setiap persona mempunyai folder sendiri.
Baca laporan dan JSON kanonis sebelum membuka DOCX/XLSX yang dihasilkan.
Jorhas mencatat hash keluaran dalam RUN_MANIFEST.json. Full Research mencatat pemanggilan spesialis aktual dan status tahap.

Periksa DOCX ORIGO, workbook Synthia, salinan beranotasi Vanlan, dan DOCX beranotasi Huxley.
Berkas yang dapat dibuka merupakan pemeriksaan artefak. Hal itu belum memvalidasi penelitian.
Contoh Vanlan memuat angka yang salah dan PDF yang hilang. Highlight menunjukkan lokasi teks, tetapi tidak dapat menyetujui klaim tersebut.
Kandidat Liora memuat metadata sintetis. Bukti indeks Agresa juga simulasi.
Retho membedakan sumber hilang, pindaian, dan identitas berbeda. Domares serta Synthia mempertahankan bukti yang belum tersedia.

[Log demo terkini](../../reports/v0.7.0/tutorial-smoke.json) mencatat exit code aktual dan pemeriksaan berkas.
Eksekusi agen native terpisah dari eksekusi CLI deterministik ini.

<!-- section: next -->
## Beralih ke penelitian nyata

Salin hanya sumber berizin ke ruang kerja privat baru. Ganti metadata sintetis dengan bukti yang telah diperiksa dan diberi atribusi.
Catat tanggal, identitas sumber, hak akses, definisi, satuan, dan denominator. Baca sumber sebelum membuat klaim interpretatif.
Gunakan direktori keluaran baru. Jangan memakai rekaman sintetis sebagai temuan.
Telaah manusia diperlukan untuk relevansi sumber, semantik, kebaruan, metode, dan kesimpulan.
Jika sumber memerlukan login, pembayaran, atau izin yang belum ada, catat BLOCKED dan hentikan percobaan akses itu.
Baca [tutorial persona](PERSONA_TUTORIALS.md) dan [handoff alur kerja](../WORKFLOW.md).
