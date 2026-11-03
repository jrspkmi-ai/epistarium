[English](../en/LICENSING.md) | Bahasa Indonesia

<!-- section: scope -->
# Lisensi

MIT mencakup kode, instruksi, dan dokumentasi orisinal EPISTARIUM. Baca [LICENSE](../../LICENSE) pada root.
Hak cipta: 2026 John R.S.P.K.M. Isa. Pemberitahuan mengikuti karya yang diberikan pemilik proyek dan instruksi MIT yang eksplisit.
Tidak ada pemegang hak berbentuk organisasi yang dikarang. Kontribusi luar tetap memerlukan izin sah dari pemegang haknya.

Ekspresi MIT dalam metadata Python menjelaskan karya orisinal EPISTARIUM. Metadata tidak melisensikan ulang dependensi, sumber pengguna, atau materi upstream.
[Pemberitahuan pihak ketiga](../../THIRD_PARTY_NOTICES.md) menetapkan batasnya. Gerbang rilis GO_BERSYARAT untuk bentuk sumber/wheel yang dijelaskan.

<!-- section: pdf -->
## Backend PDF

Runtime memakai pypdfium2 5.14.0 untuk koordinat teks dan pypdf 6.21.4 untuk anotasi serta label halaman. Keduanya tidak memerlukan PyMuPDF. Wheel dan ZIP proyek tidak membundel binari PDFium; pip memasang wheel dependensi secara terpisah. Wheel Linux yang diperiksa memuat PDFium, lisensi, dan pemberitahuan komponen pada direktori `BUILD_LICENSES`. Pertahankan pemberitahuan itu bila wheel tersebut didistribusikan ulang. Backend diuji pada Linux Python 3.12; CI Windows dan macOS masih NOT_RUN.

PyMuPDF tetap ada pada extra tes untuk fixture warisan. Kode produksi tidak mengimpornya, dan instalasi biasa tidak memerlukannya. Pemasangan extra tes membawa ketentuan AGPL/komersial ke lingkungan pengembangan itu; jangan mendistribusikan lingkungan tersebut sebagai bundel binari MIT saja. Baca [perbandingan backend](../../reports/v0.7.1/PDF_BACKEND_COMPARISON.md).

<!-- section: routes -->
## Keputusan distribusi

| Bentuk distribusi | Gerbang | Bukti dan batas |
|---|---|---|
| Kode sumber dan wheel proyek, dependensi runtime dipasang terpisah | GO_BERSYARAT | Tes fungsi lokal lulus; simpan pemberitahuan komponen PDFium bila dependensi dikemas ulang. |
| Wheel/binari pihak ketiga dibundel | HOLD_TERBATAS | Periksa wheel target dan sertakan pemberitahuan komponen; kandidat ini tidak membundelnya. |
| Runtime gabungan PyMuPDF lama | HOLD_TERBATAS | Rencana kepatuhan AGPL/komersial belum tersedia untuk bentuk itu. |
| Klaim lintas OS atau host AI native | NOT_RUN | Jangan nyatakan sudah diverifikasi. |

Lisensi proyek MIT berlaku untuk karya orisinal. Lisensi dependensi tetap terpisah. Baca [laporan lisensi kini](../../reports/v0.7.1/LICENSING_RESOLUTION.md).

<!-- section: thirdparty -->
## Materi lain dan dependensi

SimpleEnglish Plain 2.1.1 memiliki pemberitahuan hak cipta MIT tersendiri. Atribusi dan hash sumber tetap ada dalam third_party/SimpleEnglish/.
Lisensi proyek tidak menggantikan pemberitahuan itu. Tidak ada installer upstream, prosa README, atau ilustrasi mattpocock/skills yang disalin.
Repositori tersebut hanya menjadi acuan tujuan navigasi.

Requests memakai Apache-2.0. python-docx, openpyxl, dan jsonschema menyatakan lisensi MIT. Paket transitif mencakup lisensi lain, seperti MPL-2.0 dan BSD.
Tzdata Windows memiliki Apache-2.0 dan pemberitahuan data zona waktu. Paket itu tidak dijalankan pada Windows di sini.
Perangkat tes/build terpasang diaudit terpisah dalam [laporan lisensi terkini](../../reports/v0.7.1/LICENSING_RESOLUTION.md).
ZIP proyek dan wheel EPISTARIUM tidak membundel wheel dependensi pihak ketiga atau pustaka native.
Pip mengambil dependensi secara terpisah. Kewajiban lisensinya tetap berlaku.

Naskah pengguna, PDF berlisensi, dataset, dan materi wawancara tetap memiliki hak masing-masing. Simpan di luar paket publik.
Fixture sintetis ditandai sebagai bahan latihan/tes. Transkripsi angka BPS lama diberi atribusi terpisah dan tidak memberikan lisensi konten sumber.
Baca [pemberitahuan](../../THIRD_PARTY_NOTICES.md) sebelum memakai ulang materi non-orisinal.
