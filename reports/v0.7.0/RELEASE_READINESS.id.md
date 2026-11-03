[English](RELEASE_READINESS.md) | Bahasa Indonesia

<!-- section: decision -->
# Kesiapan rilis

Keputusan: HOLD untuk rilis publik. Kandidat pemeriksaan pemilik disiapkan sebagai EPISTARIUM v0.7.0 RELEASE_CANDIDATE.
Pemeriksaan teknis lokal lulus. Rencana lisensi PyMuPDF gabungan masih menjadi penghalang rilis yang belum terselesaikan.
Paket belum stable v1.0. Tidak ada tindakan publikasi yang diizinkan atau dilakukan.

<!-- section: evidence -->
## Bukti terkini

Suite regresi final lulus 374/374 kasus. Sepuluh persona kanonis dan sembilan mirror schema tetap tersedia.
Inggris dan Indonesia memakai satu implementasi. Panduan baru memiliki pemeriksaan bagian berpasangan serta tautan.
Tiga panduan OS, sepuluh panduan platform, sepuluh tutorial persona, catatan migrasi, dan catatan rilis disertakan.
MIT mencakup karya orisinal. Pemberitahuan terpisah menjelaskan ketentuan dependensi serta SimpleEnglish.
Wheel dan ZIP hasil ekstraksi lulus pemeriksaan instalasi terisolasi. Tutorial sintetis lulus pada kedua bahasa.
Baca [TEST_RESULTS](TEST_RESULTS.id.md), [COMPATIBILITY_MATRIX](COMPATIBILITY_MATRIX.id.md), dan [SECURITY_AUDIT](SECURITY_AUDIT.id.md).

<!-- section: open -->
## Hal terbuka sebelum publikasi

| Hal | Status | Langkah berikutnya |
|---|---|---|
| Lisensi distribusi PDF gabungan | BLOCKED | Pilih dan telaah kepatuhan AGPL, ketentuan komersial, atau pengganti permisif teruji. |
| Aktivasi AI native | NOT_RUN 10/10 | Jalankan discovery terdokumentasi dan tugas aktual pada setiap host yang diklaim. |
| Runtime Windows/macOS dan CI remote | NOT_RUN | Jalankan matriks yang disiapkan dan periksa artefak khusus OS. |
| Sumber pemasangan native Windsurf | BLOCKED | Periksa ulang dokumentasi resmi terkini sebelum menetapkan jalur native. |
| Provider langsung | NOT_RUN | Gunakan akses berizin dan evaluasi perilaku provider aktual secara terpisah. |
| Render dokumen umum dan isolasi parser | Sampel lokal terbatas | Periksa masukan baru dan gunakan pemrosesan terbatas untuk dokumen tak dikenal. |

Penghalang lisensi mencegah rekomendasi GO atau GO_BERSYARAT untuk distribusi publik saat ini.
Ketiadaan tes native juga mencegah klaim kompatibilitas universal. Dukungan terdokumentasi bukan hasil eksekusi.

<!-- section: approval -->
## Persetujuan publikasi pemilik

Setelah penghalang diselesaikan, dapatkan persetujuan terpisah untuk repositori aktual, visibilitas publik, cakupan sumber/artefak, dan teks rilis.
Persetujuan kemudian dapat mencakup tindakan publikasi tertentu yang telah ditelaah. Kandidat tidak membuat repositori, push, PR, atau GitHub Release.
Kandidat tidak mengubah visibilitas atau mengunggah artefak publik.
Manifest checksum mencakup berkas payload dan mengecualikan dirinya sendiri. Hash ZIP luar diperiksa terpisah untuk menghindari rujukan ke diri sendiri.
Pertahankan ZIP terkini, baseline asli yang diberikan, serta bukti tes ketika meninjau kandidat berikutnya.
