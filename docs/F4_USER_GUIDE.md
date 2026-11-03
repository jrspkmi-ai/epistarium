# Cara memakai Jorhas tanpa keahlian pemrograman

## 1. Mulai dari satu kalimat
Buka folder EPISTARIUM di agen yang bisa membaca `SKILL.md`, lalu katakan: *"Jorhas, jalankan Path Finding untuk topik komunikasi layanan digital mahasiswa. Tunjukkan data yang benar-benar diperoleh, sumber yang gagal, dan tiga arah penelitian tanpa mengarang angka."*

Jika aplikasi memiliki akses terminal, jalankan perintah di bawah. Jika tidak, agen dapat mengikuti prosedur pemeriksaan sumber dan menyusun ledger manual dengan status `MANUAL`, **bukan** mengaku menjalankan Python.

## 2. Instalasi
Python 3.11 atau lebih baru. Setelah mengekstrak paket ZIP, buka root yang langsung memuat `pyproject.toml` dan `.agents/skills/`:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[test]'
python -m epistarium doctor
python -m pytest -q
```

Gunakan folder --out baru/kosong untuk setiap run. Kode keluar 3 berarti hasil parsial; kode 4 berarti terhalang.

## 3. Path Finding tanpa internet

```bash
python -m epistarium jorhas-pathfind --idea "komunikasi layanan digital mahasiswa" --out private/hasil-awal
```

Output tetap berguna untuk tiga arah penelitian dan daftar sumber yang harus diperiksa, tetapi **tanpa bukti terambil** statusnya `BLOCKED` untuk penyediaan dossier empiris. Ini hasil yang benar, bukan error tersembunyi.

## 4. Menguji dengan data sintetis

```bash
python -m epistarium jorhas-pathfind --idea "komunikasi digital mahasiswa" --fixture examples/f4_synthetic/pathfinder_cases.json --as-of 2026-11-03 --out private/demo-f4
```

Buka `PATH_FINDING_REPORT.md` dan `DATA_LEDGER.csv`. Banner SIMULASI wajib ada. Data seperti 35,5 atau 64 pada fixture **fiktif**, tidak boleh dikutip sebagai statistik akademik.

## 5. Memakai file CSV milik pengguna
Buat JSON `private/config.json`:

```json
{"sources":[{"provider":"local_csv","path":"private/dataset_saya.csv","rights_confirmed":true,"organization":"Lembaga penghasil data","title":"Dataset saya","jenis_data":"dataset","field_mapping":{"indikator":"variabel","nilai":"jumlah","satuan":"unit"}}],"target_geography":"Kota Depok"}
```

Kemudian:

```bash
python -m epistarium jorhas-pathfind --idea "isu sesuai data saya" --config private/config.json --out private/hasil-data
```

Jorhas membaca CSV dan mencatat hash, tetapi tidak otomatis mempercayai angka atau metodologinya. Periksa definisi indikator, unit, populasi dan sampel.

## 6. Percobaan API World Bank
Contoh konfigurasi `examples/f4_synthetic/worldbank_attempt_config.json` memakai World Bank API V2. Aktivasi `--online` diperlukan. Pengujian runtime awal gagal karena jaringan DNS, jadi pada komputer lain hasil dapat berbeda:

```bash
python -m epistarium jorhas-pathfind --idea "penggunaan internet" --config examples/f4_synthetic/worldbank_attempt_config.json --online --out private/hasil-live
```

World Bank mengizinkan akses API tanpa API key. Pilih indikator yang sesuai sebelum menjalankan. Data nasional sebagai konteks tidak membuktikan fenomena pada satu kampus atau satu perusahaan. Penerjemahan unit/definisi indikator belum lengkap pada adapter bawaan.

## 7. Full Research Mode

```bash
python -m epistarium jorhas-full --idea "komunikasi krisis digital" --config examples/f4_synthetic/full_config.json --as-of 2026-11-03 --out private/demo-full
```

`FULL_RESEARCH_SUMMARY.md` berisi status tiap spesialis. Fixture memicu rangkaian nyata fungsi lokal, tetapi **tidak** memanggil model AI, menggantikan peer review, atau memproduksi disertasi final. Jika tidak ada PDF sah atau daftar pustaka, beberapa tahapan akan `NOT_RUN`.

## 8. Memeriksa hasil dan kendala
Buka sesuai urutan: `PATH_FINDING_REPORT.md`, `SOURCE_LEDGER.csv`, `DATA_LEDGER.csv`, `DATA_GAPS.md`, `RUN_MANIFEST.json`. Ketika memakai Full Mode, periksa `FULL_RESEARCH_RUN_LOG.json` dan folder masing-masing persona. Jangan menyamakan `SUCCESS` dengan klaim ilmiah tervalidasi. Gunakan DOCX ORIGO sebagai draf diskusi dengan pembimbing.

## 9. Keterbatasan dan pemulihan
- HTTP 403, CAPTCHA, robots melarang atau login diperlukan: catat BLOCKED; cari sumber resmi lain atau unggah file yang boleh diakses.
- Survei tidak ditemukan: catat "belum ditemukan pada sumber yang diperiksa"; jangan membuat angka.
- Google Trends 0-100: bukan jumlah orang atau volume pencarian absolut.
- RSS/GDELT: artikel yang ditemukan bukan jumlah kejadian; periksa duplikasi sindikasi.
- Risiko panas laptop: jalankan satu adapter per batch, gunakan cache, jangan crawling masif; tidak ada browser headless secara default.
- Lisensi/hak distribusi belum ditentukan; jangan menyebarluaskan seluruh ZIP sebagai open-source final.
