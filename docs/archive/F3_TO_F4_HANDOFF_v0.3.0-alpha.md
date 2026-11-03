# Handoff EPISTARIUM F3 alpha ke stabilisasi/F4

**Sumber kerja:** ZIP F2 Stabilized 0.2.2-alpha yang diunggah pengguna; regresi 83 tes PASS. Versi hasil F3: 0.3.0-alpha, 3 modul baru, 38 tes F3 PASS, total 121 PASS. Tidak ada repositori/push/commit.

## Kebenaran tentang modul
Ideon CLI = scaffold RMC dan 21 kerangka jawaban, bukan mesin literatur atau proposal yang sudah terverifikasi. Quilo = lint dan pemeriksaan token, bukan audit kesamaan semantik. Huxley = rekonsiliasi parsial APA7 DOCX, bukan pemeriksa apakah sumber mendukung suatu klaim. Vanlan tetap menangani audit substantif dengan review manusia. Paket memuat fixture fiktif dan demonstrasi beranotasi.

## Hal yang sebaiknya dikerjakan berikutnya
1. Stabilkan Huxley dengan minimal beberapa manuskrip DOCX berizin dan gold human labels, termasuk aturan organisasi, suffix, footnote, teks tabel, field Zotero, Mendeley dan EndNote; ukur precision/recall eksternal serta deteksi duplikat.
2. Validasi jawaban Ideon berdasarkan PDF RMC asli dan kajian literatur tervalidasi; minta narasumber pengguna menilai ketepatan pertanyaan, bukan hanya jumlah 21.
3. Validasi Quilo dengan pasangan tulisan sebelum-sesudah dan penilaian apakah makna dan metodologi dipertahankan.
4. Periksa lisensi dependensi dan hak distribusi template; uji instalasi skill native dan CLI lintas OS.
5. Jangan mengembangkan Jorhas F4 sebagai orkestrator terpercaya sampai ada kontrak dan evaluasi output kritis pada modul yang akan dipanggil; jika prototipe dibuat, tiap langkah harus tercatat PASS/FAIL/BLOCKED.

## Prompt lanjutan siap tempel
"Mulai EPISTARIUM F3 STABILIZATION dari ZIP `EPISTARIUM_FASE_III_ALPHA_v0.3.0.zip` dan laporan `reports/F3_GATE_v0.3.0-alpha.md`. Ulangi 121 tes sebagai baseline, lalu audit keterbatasan Ideon, Quilo, Huxley menggunakan dokumen berizin dan gold standard manusia. Jangan klaim semantik tervalidasi tanpa bukti, dan jangan push atau rilis publik sebelum persetujuan terpisah."
