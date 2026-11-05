# EPISTARIUM v0.8.0 | Bukti Pengujian

Lingkungan: kontainer Linux, Python 3.13.5, Node 22, Chromium headless. Baseline kode menggunakan sumber GitHub v0.7.1 yang telah disortir. Perubahan v0.8.0 diterapkan sebagai overlay agar ilustrasi dan CI terbaru tetap dipertahankan di repositori pengguna.

| Pengujian | Hasil | Cakupan |
|---|---|---|
| Regresi Python keseluruhan | **399/399 PASS** | Kode lama dan 19 tes Observatory baru |
| Bantuan perintah Observatory | **PASS** | CLI dan argumen opsional |
| Jorhas dengan fixture sintetis | **PASS** | Path Finding aktual, peristiwa, manifest, artefak dan jeda persetujuan |
| Gerbang persetujuan | **PASS** | Sebelum akses jaringan, pelepasan artefak, penolakan, revisi, catatan keputusan |
| HTTP/SSE loopback | **PASS** | API, token, Host/Origin, stream dan aset UI |
| Pemulihan status setelah restart | **PASS** | Run yang terputus ditandai BLOCKED |
| Skema JSON | **PASS** | Status run, peristiwa dan keputusan |
| Chromium offline | **PASS** | Sepuluh simbol persona, EN/ID, gelap/terang, dialog persetujuan, tanpa galat JS |
| Sintaks JavaScript | **PASS** | Pemeriksaan Node |
| Skill | **PASS** | Sepuluh skill kanonis dan 16 perintah CLI |
| Dokumentasi | **PASS** | 102 dokumen aktif, 31 pasangan EN/ID, 565 tautan lokal |
| Pemeriksaan SimpleEnglish mekanis | **PASS** | Tidak ada masalah pada dokumen Inggris yang diperiksa |
| Tutorial sintetis dwi-bahasa | **PASS** | Bahasa Inggris dan Indonesia, masing-masing 11 perintah |
| Wheel Python | **PASS** | HTML, CSS, JS turut dikemas |
| Browser desktop terhubung langsung ke localhost | **BLOCKED** | Kebijakan administrator kontainer memblokir browser ke alamat lokal. Tes UI offline dan HTTP/SSE dilakukan terpisah. |
| GitHub Actions v0.8.0 lintas OS | **NOT_RUN** | Memerlukan push cabang fitur yang belum dilakukan. |
| Instalasi terisolasi dengan dependensi baru | **NOT_RUN** | Lingkungan ini memiliki pypdf 5.9.0 dan pypdfium2 5.8.0, di bawah persyaratan paket. |

Tangkapan layar dihasilkan dari eksekusi Python Jorhas dengan **fixture sintetis**. Itu bukan temuan penelitian empiris. Tes browser offline memakai data aktual hasil fixture tersebut, dengan transport yang disimulasikan. Transport HTTP/SSE diuji langsung secara terpisah. Keputusan rilis untuk `main` tetap menunggu CI dan uji browser pada desktop nyata.
