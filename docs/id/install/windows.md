[English](../../en/install/windows.md) | Bahasa Indonesia

<!-- section: identity -->
# Instalasi pada Windows 10/11

EPISTARIUM v0.9.0 RELEASE_CANDIDATE. Persyaratan minimum paket: Python 3.11.
Hanya Linux x86_64 dengan Python 3.12.14 yang dijalankan secara lokal. Panduan OS ini tidak membuktikan pengujian native.

Baca [lisensi](../LICENSING.md) sebelum memasang runtime PDF.
MIT mencakup karya orisinal. Runtime memakai pypdfium2 dan pypdf. Baca gerbang rilis v0.9.0.

<!-- section: python -->
## 1. Pasang Python dan buka PowerShell

Dapatkan Python install manager dari [Python.org](https://www.python.org/downloads/).
Gunakan runtime CPython standar. Jangan memilih paket embeddable atau build free-threaded untuk panduan ini.
Buka Start, cari PowerShell, lalu jalankan sebagai pengguna biasa.
Jika memakai install manager, jalankan:

```powershell
py install 3.14
py -3.14 --version
```

Perintah install manager berbeda dari launcher py lama. Jika `py install` tidak tersedia, ikuti panduan pemasangan Windows resmi.
Python 3.11 hingga 3.14 yang sudah terpasang dapat dipilih dengan nomor versinya.
Matriks CI disiapkan untuk 3.11, 3.12, dan 3.14. Eksekusi native Windows masih NOT_RUN.
Baca [panduan Windows resmi](https://docs.python.org/3/using/windows.html) untuk kegagalan pemasangan dan dukungan OS.
CPython 64-bit menjadi jalur utama panduan ini. Windows ARM dan 32-bit berstatus NOT_RUN. Kebijakan ASR atau organisasi dapat membatasi instalasi.

<!-- section: download -->
## 2. Ekstrak dan temukan root proyek

Di halaman repositori GitHub, pilih **Code > Download ZIP** atau unduh aset ZIP versi 0.7.1 melalui Releases jika sudah tersedia.
Gunakan tindakan Extract All atau Ekstrak pada pengelola berkas. Pertahankan seluruh direktori, termasuk .agents/skills/.
Buka folder hasil ekstraksi (misalnya `epistarium-main` atau `EPISTARIUM_v0.9.0`). Root berisi pyproject.toml, epistarium/, AGENTS.md, dan .agents/skills/.
Pada terminal, pindah ke folder tersebut. Ganti jalur contoh ini dengan jalur Anda sendiri:

```powershell
Set-Location -LiteralPath "C:\Users\YourName\Downloads\EPISTARIUM_v0.9.0"
Get-ChildItem -Force
```

Lingkungan virtual adalah folder instalasi Python privat untuk proyek ini. Folder ini mencegah paket proyek bercampur dengan paket sistem.

<!-- section: install -->
## 3. Pasang dan jalankan doctor

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m epistarium --version
.\.venv\Scripts\python.exe -m epistarium doctor --lang en
```

Skrip aktivasi tidak diperlukan. Akun pengguna biasa cukup untuk perintah ini.
Pip memerlukan jaringan untuk mengunduh dependensi. Contoh penelitian di bawah berjalan luring.
Runtime memerlukan pypdfium2>=5.14,<6 dan pypdf>=6.21,<7. Wheel PDFium menyertakan pemberitahuan lisensi komponen.
Batas versi tidak menyelesaikan kewajiban AGPL. Jangan memakai ulang lingkungan campuran 2.x. Buat lingkungan baru untuk kandidat ini.

Doctor memeriksa impor dependensi, data zona waktu, dan hak tulis. Doctor tidak menguji aktivasi AI native atau kebenaran sumber.
Pada root yang benar, hasil yang diharapkan adalah version 0.7.1, execution_status SUCCESS, dan skill_count_at_project_root 10.
Ringkasan ini menggambarkan field yang diharapkan. Keluaran Linux aktual ada dalam [bukti doctor terdahulu](../../../reports/v0.7.0/doctor-en.json).

<!-- section: example -->
## 4. Jalankan contoh pertama dan baca berkasnya

```powershell
.\.venv\Scripts\python.exe -m epistarium ideon-origo --input examples/bilingual/origo.en.json --lang en --out private/first-map-en
.\.venv\Scripts\python.exe -m epistarium ideon-origo --input examples/bilingual/origo.id.json --lang id --out private/first-map-id
```

Gunakan nama folder baru jika mengulangi perintah. Buka private/first-map-en melalui pengelola berkas.
Baca ideon_origo.json. Nama keluaran di dalamnya menunjukkan DOCX yang dihasilkan. Buka DOCX dengan pembaca dokumen.
Pastikan docx_status CREATED_AND_REOPENED. Tinjau enam simpul dan 21 pertanyaan. Masukannya sintetis dan isinya tetap draf.
Pilih --lang auto untuk fallback locale. Bahasa eksplisit mengungguli variabel lingkungan dan konfigurasi masukan.
Jorhas mempertahankan Asia/Jakarta kecuali --timezone memilih zona lain. Pemilihan bahasa tidak mengubah zona waktu itu.
Lanjutkan ke [Penelitian Pertama](../FIRST_RESEARCH.md) dan [tutorial persona](../PERSONA_TUTORIALS.md).

<!-- section: update -->
## 5. Pembaruan dan uninstall

Cadangkan penelitian privat di luar proyek hasil ekstraksi. Unduh paket baru yang disetujui pemilik ke folder terpisah.
Baca panduan migrasinya. Buat lingkungan virtual baru, pasang kembali, lalu ulangi doctor dan contoh.
Jangan menimpa satu-satunya salinan data privat. Jika membuat adaptor Claude, hapus adaptor sebelum menghapus proyek lama.

Untuk uninstall, tutup agen yang memakai proyek. Hapus hanya folder .venv proyek ini melalui pengelola berkas.
Kemudian hapus proyek hasil ekstraksi jika tidak ada berkas yang diperlukan. Menghapus venv menghilangkan paketnya tanpa mengubah Python sistem.
Jika EPISTARIUM dipasang pada lingkungan lain, gunakan Python lingkungan tersebut dengan `-m pip uninstall epistarium`.
Jangan menghapus dependensi yang dipakai proyek lain.

<!-- section: troubleshooting -->
## 6. Pemecahan masalah dan batas validasi

| Gejala | Tindakan |
|---|---|
| pyproject.toml tidak ada | Buka root proyek hasil ekstraksi yang lengkap. |
| No module named epistarium | Pasang dengan interpreter venv yang juga dipakai menjalankan perintah. |
| Impor pypdfium2 atau pypdf gagal | Buat venv bersih dan pasang kembali dependensi berbatas versi. |
| No matching distribution | Periksa versi CPython, arsitektur CPU, OS, dan dukungan wheel pypdfium2. Catat BLOCKED jika tidak tersedia. |
| Folder sudah ada | Pilih folder keluaran baru. Jangan menimpa eksekusi sebelumnya. |
| Doctor menghitung nol skill | Wheel saja tidak memuat skill. Buka root proyek ZIP lengkap. |
| Kesalahan jaringan atau sertifikat | Periksa konfigurasi proxy/sertifikat yang diizinkan. Jangan menonaktifkan verifikasi TLS. |
| Exit code 2 | Perbaiki masukan atau field kontrak yang tidak valid. |
| Exit code 3 | Baca hasil parsial dan status setiap tahap. |
| Exit code 4 | Baca tahap terhalang beserta artefak atau dependensi yang belum tersedia. |

Exit code nol hanya menjelaskan eksekusi. Status itu tidak memverifikasi klaim ilmiah.
Contoh ini tidak memerlukan provider langsung atau layanan AI berbayar.
Baca [hasil tes terdahulu](../../../reports/v0.7.0/TEST_RESULTS.md) untuk perintah aktual dan denominasi.

Jika PowerShell memblokir Activate.ps1, tetap gunakan perintah python.exe eksplisit di atas. Perubahan execution policy tidak diperlukan.

Referensi resmi diperiksa pada 2026-11-03: [venv](https://docs.python.org/3/library/venv.html) dan referensi Python/OS di atas. Instalasi native Windows 10/11 berstatus NOT_RUN.
