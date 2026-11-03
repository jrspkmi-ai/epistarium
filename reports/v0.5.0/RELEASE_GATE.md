# Gerbang rilis EPISTARIUM v0.5.0

Tanggal keputusan: 3 November 2026, Asia/Jakarta. **PASS untuk rilis paket lokal v0.5.0 dalam cakupan yang diuji.** Paket ini tidak dipublikasikan ke layanan luar dan tidak menyatakan seluruh host/OS sudah lolos.

| Pemeriksaan | Hasil aktual | Bukti |
|---|---|---|
| Regresi baseline dan tambahan | **252 lulus**, tanpa skip/deselect pada suite akhir; 198 tes lama dan 54 tes baru | TEST_RESULTS.txt dan TEST_RESULTS.xml |
| Jaringan suite regresi | Koneksi socket diblokir oleh fixture pengujian; respons provider memakai mock | tests/conftest.py, tes transport dan provider |
| Dokumen aktif, pemicu dan perintah | 30 dokumen, 10 persona, 15 perintah; SUCCESS | DOCUMENTATION_CHECK.json |
| Schema | Semua schema dapat diparse; kontrak packaged tersedia; salinan schemas dan data identik | Pemeriksa dokumentasi, tes runtime dan wheel |
| Lingkungan sumber | doctor SUCCESS, Linux Python 3.12.14 | ENVIRONMENT.json dan TESTED_DEPENDENCIES.txt |
| Build distribusi | Wheel 0.5.0 dan source distribution berhasil dibangun | BUILD_LOG.txt |
| Instalasi wheel | Pemasangan target terpisah berhasil; impor dari luar source tree | WHEEL_INSTALL_LOG.txt dan WHEEL_SMOKE.json |
| Alur wheel sintetis | Path Finding exit 3; Full Research exit 3; artefak tahap yang dijalankan lengkap, XLSX 20 kolom dibuka ulang dan 1 DOCX ORIGO tersedia | WHEEL_SMOKE.json |
| Kegagalan ekspor | Kegagalan DOCX/XLSX menjadikan tahap BLOCKED; tahap bergantung tidak diklaim berjalan | test_release_integrity.py |
| Percobaan penggunaan instruksi | Satu skenario Jorhas mempertahankan label sintetis dan menolak promosi bukti | FORWARD_USE.md |
| Integritas pengemasan | Daftar hash berkas rilis tersedia; arsip diperiksa ulang setelah dibuat | RELEASE_FILES.sha256 dan catatan QA paket |

Instalasi wheel memakai dependensi runtime yang sama melalui pemasangan --no-deps. Ini memeriksa packaging dan resource, bukan pemasangan daring dari lingkungan Python kosong. Fixture PDF dan DOCX sintetis diambil dari paket sumber; wheel hanya menyediakan pustaka/CLI, sedangkan sepuluh skill dibawa oleh ZIP proyek.

## Perbaikan yang direproduksi

Status substantif sumber tidak lagi menjadi adjudikasi ledger. Source ID tetap tersambung sesudah deduplikasi dengan alias/riwayat akses. Artikel tanpa DOI memakai ID stabil sehingga crosswalk tidak saling menimpa. DOCX/XLSX wajib diperiksa sebelum tahap menyatakan SUCCESS. Data mentah yang gagal menjadi angka tetap terlacak dan tidak menghasilkan JSON NaN/Infinity.

## Pemeriksaan yang belum dijalankan

- Uji native pada Mac dan Windows milik pengguna serta aktivasi Codex, Antigravity dan OpenCode.
- Eksekusi remote matrix CI enam kombinasi OS/Python. Berkas konfigurasi tersedia, belum merupakan bukti lolos.
- Pengambilan data live provider dan benchmark ilmiah menggunakan korpus independen berizin.
- Evaluasi precision/recall substantif, adjudikasi AI, dan pengujian perilaku seluruh sepuluh persona lintas model.
- Lokalisasi penuh keluaran ke Bahasa Inggris dan keputusan lisensi untuk distribusi publik.

Batas ini tidak diisi dengan hasil historis F1-F4. Catatan patch dan keputusan atas empat audit ada di docs/AUDIT_DECISIONS_v0.5.0.md, sedangkan perubahan kontrak ada di docs/MIGRATION_0.5.0.md.
