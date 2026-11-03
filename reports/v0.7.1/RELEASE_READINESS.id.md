# Kesiapan rilis v0.7.1

**Keputusan: GO_BERSYARAT untuk evaluasi rilis kode orisinal MIT dalam bentuk sumber/wheel. Publikasi belum diizinkan.**

| Ruang lingkup | Gerbang | Bukti atau tindak lanjut |
|---|---|---|
| Fungsi PDF produksi pada Linux Python 3.12 | GO_BERSYARAT | Suite lengkap dan instalasi bersih wajib lulus. Adapter diuji memakai PDF sintetis; tata letak kompleks tetap dibatasi. |
| Pembundelan binari PDFium atau wheel dependensi | HOLD_TERBATAS | Paket proyek tidak membundelkannya. Periksa wheel sasaran dan sertakan pemberitahuan komponen bila bentuk distribusi berubah. |
| Lingkungan tes PyMuPDF AGPL | HOLD_TERBATAS | Extra tes opsional memakainya. Jangan beri label bundel binari itu sebagai MIT saja. |
| Kegagalan alur riset inti | HOLD_PENUH bila muncul | Kegagalan tes tidak boleh diabaikan. |
| Integrasi host AI native | NOT_RUN | Jangan klaim sudah aktif. Hal ini tidak menahan paket Python yang diuji. |
| Windows/macOS/Python 3.11/3.14 | NOT_RUN | Matriks sembilan pekerjaan siap, belum dijalankan. |
| OCR/fitur tambahan | Batas dinyatakan | PDF scan tetap menunggu OCR atau penelaahan manusia. |

Persetujuan pemilik secara terpisah diperlukan sebelum tindakan repositori publik. Baca [hasil uji](TEST_RESULTS.md), [perbandingan backend](PDF_BACKEND_COMPARISON.md), dan [lisensi](LICENSING_RESOLUTION.md).
