<!-- section: start -->
# EPISTARIUM v0.9.0 | Research Observatory (ID)

Observatory merupakan **pemantau lokal opsional** bagi eksekusi Python Jorhas yang benar-benar berlangsung. Halaman ini menampilkan status sepuluh persona resmi, langkah, jumlah rekaman sumber/data, artefak, peristiwa, dan gerbang persetujuan peneliti. Observatory membantu pengawasan kerja, **bukan layanan verifikasi empiris otomatis**.

Gunakan Python 3.11 atau lebih baru. Pasang EPISTARIUM dari direktori repositori dalam lingkungan virtual sesuai panduan: [Windows](../install/windows.md), [macOS](../install/macos.md), dan [Linux](../install/linux.md). Fitur ini tidak memerlukan Node.js, akun cloud, React, FastAPI, atau penyedia API berbayar.

Setelah lingkungan virtual aktif:

```bash
python -m epistarium observatory --open
```

Alamat bawaan `http://127.0.0.1:4782/`. Opsi `--open` meminta sistem operasi membuka browser. Jika sistem memblokirnya, buka alamat yang tercetak secara manual. Gunakan `--no-browser` untuk lingkungan tanpa antarmuka grafis. Folder penyimpanan privat bawaan `~/.epistarium-observatory/`, di luar repositori GitHub. Hentikan server dengan Ctrl+C.

Untuk menjalankan **Jorhas Path Finding nyata** dengan data tes sintetis (jangan menganggap temuannya empiris):

```bash
python -m epistarium observatory --idea "Komunikasi krisis digital" --mode pathfind --fixture examples/f4_synthetic/pathfinder_cases.json --lang id --open
```

Untuk run berdasarkan ide tanpa fixture sintetis:

```bash
python -m epistarium observatory --idea "Keluhan konsumen F&B" --mode pathfind --lang id --open
```

Tanpa input atau adapter sumber yang tersedia, keluaran dapat berstatus `PARTIAL` atau `BLOCKED`. Observatory tidak mengarang sumber maupun status verifikasi. Antarmuka browser hanya dapat membuat run **offline**. Untuk menggunakan berkas lokal, konfigurasi berizin, atau akses jaringan, jalankan CLI dengan `--config`, `--fixture`, dan `--online` sesuai kebutuhan.

[Pratinjau antarmuka, mode gelap pada fixture sintetis](../../en/observatory/media/dark_en_synthetic.png) serta [mode terang](media/light_id_synthetic.png). Gambar membuktikan hasil render UI, sedangkan transport langsung diuji terpisah melalui tes HTTP/SSE lokal.

<!-- section: monitoring -->
## Pemantauan langsung

Dashboard menggunakan **empat kolom: Belum dijalankan/antre, Berjalan, Perlu pemeriksaan, Langkah selesai**. Setiap persona mempunyai simbol fungsional, tanpa potret manusia acak. Header menyediakan EN/ID (bawaan **EN**) serta gelap/terang (bawaan **gelap**). Pilihan disimpan di browser. Tata letak responsif dan kedua bahasa membaca peristiwa kanonis yang sama.

Server menerima checkpoint dari **fungsi Jorhas yang benar-benar dipanggil** melalui callback opsional. Peristiwa masuk ke `runs/<run-id>/events.jsonl`, kemudian browser menerima pemberitahuan SSE untuk memperbarui keadaan. `run.json` menyimpan status eksekusi, sedangkan `outputs/<run-id>/` menyimpan ledger dan laporan Jorhas yang sudah ada.

Sembilan spesialis tetap `NOT_RUN` jika belum dipanggil. Path Finding pada umumnya menjalankan **Jorhas**, bukan kesepuluh persona. Full Research hanya menjalankan spesialis ketika konfigurasi dan bahan tersedia. `SUCCESS` menunjukkan fungsi selesai, bukan klaim telah terbukti. Status `PARTIAL`, `BLOCKED`, `NOT_RUN`, dan status pembuktian dipisahkan.

Angka rekaman dihitung dari `SOURCE_LEDGER.json` dan `DATA_LEDGER.json`. Nilai yang tidak tersedia ditampilkan sebagai `—`. Pratinjau hanya mendukung teks, JSON, CSV, atau Markdown berukuran kecil. Dashboard tidak menciptakan skor ketepatan, ETA, atau aktivitas simulatif untuk penelitian nyata.

<!-- section: approval -->
## Gerbang persetujuan

- Opsi `--online` membuat run berhenti **sebelum akses sumber luar**. Peneliti harus menyetujuinya dari dashboard lokal menggunakan kata sandi peninjauan. Adapter tetap wajib mematuhi izin, hak akses, dan batas layanan.
- Setelah eksekusi, Jorhas menunggu **otorisasi pelepasan paket artefak**. Peneliti dapat menyetujui, menolak, atau meminta revisi. Penolakan dan permintaan revisi harus disertai alasan. Rekaman `approvals.json` menyimpan pilihan, waktu, label peninjau lokal yang identitasnya belum diautentikasi, hash manifest, dan daftar hash artefak. `release_authorization.json` hanya dibuat setelah persetujuan final eksplisit.
- Persetujuan berarti izin melanjutkan atau melepas paket, **bukan** keputusan bahwa seluruh sumber terverifikasi, serta bukan izin untuk menerbitkan kode ke GitHub.
- Permintaan revisi mengakhiri run dengan `NEEDS_CHANGES`. Pengguna dapat menjalankan run baru; melanjutkan otomatis sebagian tahapan persona belum tersedia.

<!-- section: security -->
## Keamanan dan batas data

Server hanya membuka `127.0.0.1` dan menolak Host/Origin asing. Endpoint yang mengubah status memerlukan token sesi melalui header khusus. Tidak ada izin lintas-origin. Pratinjau dibatasi pada folder run privat, menolak symlink serta *path traversal*, dan mengirim **teks saja** yang dirender dengan `textContent`, bukan sebagai HTML yang dieksekusi. Nama artefak relatif dapat tercatat dalam event privat; masukan mentah tidak diterima melalui bridge. Jangan menyimpan folder run di repositori yang akan dipublikasikan.

**Batas ancaman:** proses berbahaya dengan akses pengguna sistem operasi yang sama mungkin tetap bisa memeriksa lalu lintas localhost atau berkas. Dashboard ini **belum dirancang untuk server publik, penerusan port, atau banyak pengguna yang tidak saling dipercaya**. Jangan membukanya melalui reverse proxy atau tunnel publik.

<!-- section: limits -->
## Keterbatasan dan pemeriksaan

Baca [panduan bridge](BRIDGE.md) untuk kata sandi dan laporan host eksternal. Kata sandi peninjauan terpisah dari token agen.

Tes regresi Python dan HTTP/SSE lokal tersedia pada `tests/test_observatory_v080.py`. Pemeriksaan visual Chromium merupakan tes opsional melalui `scripts/observatory_browser_smoke.py` dan memerlukan Playwright/Chromium terpisah. Jalankan `python -m pytest -q` dan matriks GitHub Actions sebelum memublikasikan rilis.

Akses browser lokal dari ChatGPT web/Work, Gemini web, atau Claude web **tidak otomatis tersedia**. Diperlukan dukungan filesystem, browser, atau MCP pada masing-masing host. Plugin yang hanya memuat `SKILL.md` tidak dapat menjalankan proses Python lokal dengan sendirinya. Observatory saat ini merupakan kemampuan Python lokal, bukan dashboard cloud. Kode orisinal Observatory menggunakan MIT sesuai LICENSE, sedangkan pemberitahuan lisensi pihak ketiga lama tetap berlaku.
