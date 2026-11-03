[English](TEST_RESULTS.md) | Bahasa Indonesia

<!-- section: environment -->
# Hasil pengujian

EPISTARIUM 0.7.0 RELEASE_CANDIDATE, 2026-11-03. Lingkungan: Linux x86_64, glibc 2.39, Python 3.12.14.
Hasil pytest final: 374/374 PASS, 0 FAIL, 0 dilewati. Proses tes langsung keluar dengan kode 0.
Baseline v0.6.0 tanpa perubahan lulus 341/341 kasus secara terpisah. Jangan menjumlahkan baseline dan final sebagai satu denominator.
Versi dependensi ada dalam [DEPENDENCIES.json](DEPENDENCIES.json). Build memakai setuptools 84.2.1.
Log mesin mentah mempertahankan perintah, return code, nama berkas, dan hash persis.

<!-- section: counts -->
## Hasil menurut unit

| Unit pemeriksaan | PASS | FAIL | BLOCKED | NOT_RUN | Bukti |
|---|---:|---:|---:|---:|---|
| Kasus regresi final | 374 | 0 | 0 | 0 | pytest.xml / pytest.log |
| Definisi persona kanonis | 10 | 0 | 0 | 0 | skill-checks.json |
| Mirror schema | 9 | 0 | 0 | 0 | contract-checks.json |
| Perintah tutorial, EN + ID | 22 | 0 | 0 | 0 | tutorial-smoke*.json |
| Pemeriksaan buka ulang/parse artefak tutorial | 198 | 0 | 0 | 0 | 108 EN + 90 ID, synthetic |
| Perintah CLI wheel terisolasi | 5 | 0 | 0 | 0 | wheel-smoke.json |
| Perintah CLI ZIP terisolasi | 5 | 0 | 0 | 0 | zip-install-smoke.json |
| Halaman ORIGO hasil render | 7 | 0 | 0 | 0 | layout-checks.json, two samples |
| Tautan Markdown lokal | 538 | 0 | 0 | 0 | doc-checks.json |
| Pasangan edisi dokumen | 30 | 0 | 0 | 0 | Section parity, not translation certification |
| Berkas prosa Inggris statis | 52 | 0 | 0 | 0 | english-checks.json, mechanical scope |
| Telaah sumber resmi host | 9 | 0 | 1 | 0 | Windsurf redirect content inaccessible |
| Aktivasi host native | 0 | 0 | 0 | 10 | No app instance exercised |
| Job matriks CI remote | 0 | 0 | 0 | 9 | Three OS labels × three Python versions |
| Rencana lisensi PDF gabungan | 0 | 0 | 1 | 0 | Public release blocker |

Baris memakai unit serta cakupan berbeda. Jangan menjumlahkan denominator atau menyamakan PASS eksekusi dengan verifikasi ilmiah.
Jumlah dokumentasi final juga tercatat dalam doc-checks.json dan english-checks.json.

<!-- section: execution -->
## Perintah dan bukti instalasi

Venv proyek menjalankan doctor EN/ID, verify_skills.py, check_docs.py, check_english.py, pytest, audit_dependencies.py, dan package_release.py.
Perintah regresi persis: `python -m pytest -q --junitxml=reports/v0.7.0/pytest.xml`.
Perintah wheel final: `python -m build --wheel --no-isolation`. Build lengkap sebelumnya juga membuat sdist.
Hanya wheel terkini yang dipilih untuk ZIP. Wheel lama dan direktori build hasil generasi dikecualikan.

Runner tutorial sintetis menjalankan sebelas perintah berurutan per bahasa. Code 3 Path Finding dan Full Research dihitung sebagai ekspektasi yang terpenuhi.
Runner membuka ulang atau mem-parse setiap artefak yang dihasilkan. Pemeriksaan ini maupun manifest valid tidak menilai makna ilmiah.

Pemeriksaan wheel memakai venv terpisah dan instalasi non-editable. Pemeriksaan ZIP mengekstrak kandidat terkemas lalu membuat venv baru yang lain.
Keduanya memakai mode impor Python terisolasi agar direktori sumber tidak menutupi paket terpasang.
Lima perintah CLI lulus untuk setiap instalasi. Stdout doctor dapat di-parse sebagai JSON pada kedua bahasa dan menemukan sepuluh skill pada root.
[Pemeriksaan arsip](archive-install-checks.json) mencakup kandidat uji instalasi. Pengemasan final memeriksa ulang setiap hash payload.
ZIP final dapat berbeda dalam laporan dan dokumentasi, tetapi signature sumber runtime harus cocok dengan zip-install-smoke.json.

<!-- section: findings -->
## Temuan yang diperbaiki saat validasi

Uji pemula menemukan nama kunci dictionary dipakai sebagai nilai halaman cetak Domares. Perbaikan membaca nilainya secara eksplisit dan mempertahankan halaman tak diketahui sebagai null.
Empat kasus regresi EN/ID kini memeriksa halaman cetak yang tersedia dan tidak tersedia melalui Domares, JSON Synthia, serta workbook.
Contoh ORIGO panjang juga mencapai footer. Revisi margin dan jarak footer lulus pemeriksaan tujuh halaman hasil render dari dua sampel bahasa.
Artefak awal dipertahankan. Cacat lama pada artefak itu tidak disajikan sebagai hasil terkini.

Pemeriksaan proses ZIP bersih kemudian menemukan peringatan impor fitz sebelum JSON doctor.
Impor runtime kini memakai pymupdf. Dua tes bahasa pada proses baru mencegah regresi. ZIP serta wheel yang dibangun ulang lulus pemeriksaannya.
Dua temuan pemindaian rahasia pertama merupakan URL tes penolakan sintetis. Pengecualian persis yang ditelaah mempertahankan tes tanpa mengabaikan temuan tambahan.

Bukti pemakaian ada dalam forward-use/. Ini alur lokal manual, bukan sertifikasi aktivasi aplikasi native.
Provider langsung, temuan empiris, skor penalaran model, atau akurasi dukungan semantik tidak ditetapkan.
Matriks 20 kolom maupun kecocokan teks tetap merupakan bantuan penelitian yang memerlukan telaah manusia.
