[English](LICENSING_AUDIT.md) | Bahasa Indonesia

<!-- section: decision -->
# Audit lisensi

Keputusan: HOLD untuk distribusi publik. Pemberian MIT karya orisinal: PASS dalam ruang lingkup yang dinyatakan.
Kepatuhan runtime gabungan PyMuPDF: BLOCKED. Ini penghalang rilis, bukan klaim bahwa MIT dan AGPL tidak pernah dapat berdampingan.
Perjanjian komersial atau rencana distribusi corresponding source lengkap belum diberikan.
Pemilik perlu memilih jalur yang telah ditelaah sebelum rilis publik.

Pemberitahuan hak cipta mengikuti identitas pemilik yang sudah ditetapkan, John R.S.P.K.M. Isa, serta proyek yang diberikan.
Pemilik meminta MIT secara eksplisit untuk kode orisinal. Tidak ada organisasi, pengalihan hak kontributor, atau kepemilikan pihak ketiga yang dikarang.

<!-- section: evidence -->
## Bukti yang diperiksa

Lingkungan terpasang memiliki 31 distribusi, termasuk EPISTARIUM dan perangkat tes/build.
Closure runtime aktif memiliki 17 distribusi eksternal pada Linux. Tzdata Windows bersifat kondisional dan NOT_RUN.
[DEPENDENCIES.json](DEPENDENCIES.json) mencatat setiap distribusi terpasang serta hash berkas lisensi yang tersedia.
Inventaris khusus untuk lingkungan ini. Inventaris tidak menyetujui semua versi mendatang yang diizinkan pyproject.toml.

Ketentuan runtime langsung: PyMuPDF AGPL/komersial, requests Apache-2.0, python-docx/openpyxl/jsonschema MIT, serta defusedxml keluarga PSF.
Ketentuan transitif mencakup MIT, BSD, MPL-2.0, dan PSF-2.0. Lisensi perangkat tes/build dicatat terpisah dalam inventaris.
Openpyxl dan et_xmlfile tidak memiliki berkas lisensi terpisah dalam rekaman wheel teramati. Metadata MIT serta rujukan sumber tetap diidentifikasi.
Tidak ada biner dependensi yang dibundel. Unduhan terpisah tidak menghilangkan kewajibannya.

[THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.id.md) mempertahankan pemberitahuan MIT independen dan hash sumber SimpleEnglish.

<!-- section: pdf -->
## Mitigasi PyMuPDF

Kode mengimpor PyMuPDF dalam proses yang sama pada Retho, Domares, dan Vanlan. Status dependensi wajib dipertahankan serta diungkapkan.
Batas teruji >=1.28.2,<2 menghindari rantai layout/ONNX 2.x yang teramati saat instalasi baseline.
Batas itu tidak menetapkan lisensi permisif. Pemeriksaan halaman, koordinat, highlight, hash, dan pembukaan ulang Vanlan tetap utuh.

Extra opsional tidak menyelesaikan batas hukum dengan sendirinya. Subproses command-line saja juga memerlukan argumen pemisahan yang dinilai.
Paket tidak mengklaim pemisahan demikian. Backend PDF tidak diganti atau diubah namanya untuk menyembunyikan lisensi.

| Alternatif | Bukti yang diperlukan | Status |
|---|---|---|
| Runtime gabungan yang mematuhi AGPL | Telaah corresponding source, pemberitahuan, hak penerima, serta rencana distribusi jaringan | BLOCKED |
| Ketentuan komersial Artifex | Perjanjian sah yang mencakup penggunaan dan distribusi | NOT_RUN |
| pypdfium2 beserta pypdf | Implementasi perilaku setara serta seluruh pemberitahuan komponen PDFium | NOT_RUN |
| Paket instruksi saja dengan cakupan terpisah | Telaah pemisahan fungsional dan batas distribusi yang nyata | NOT_RUN |

Pengganti memerlukan tes label halaman, rotasi, Unicode, anchor berulang, batas koordinat, penempatan highlight, hash sumber tetap, dan pembukaan ulang.
Lisensinya juga memerlukan audit komponen. Kandidat saat ini tidak dapat disebut sebagai pengganti yang telah dievaluasi.

<!-- section: sources -->
## Sumber resmi yang diperiksa pada 2026-11-03

[Teks MIT](https://opensource.org/license/mit) · [Lisensi PyMuPDF](https://pymupdf.io/licensing) · [Lisensi Artifex](https://artifex.com/licensing)

[COPYING PyMuPDF](https://github.com/pymupdf/PyMuPDF/blob/main/COPYING) · [LICENSE requests](https://github.com/psf/requests/blob/main/LICENSE)

[LICENSE python-docx](https://github.com/python-openxml/python-docx/blob/master/LICENSE) · [COPYING jsonschema](https://github.com/python-jsonschema/jsonschema/blob/main/COPYING)

[Pernyataan lisensi openpyxl](https://openpyxl.readthedocs.io/en/stable/) · [LICENSE tzdata](https://github.com/python/tzdata/blob/master/LICENSE)

[Ketentuan pypdfium2](https://pypdfium2-team.github.io/pypdfium2/readme.html) · [Lisensi pypdf](https://pypdf.readthedocs.io/en/stable/meta/faq.html)

Pustaka alternatif hanya diteliti. Pustaka tidak dipasang, diintegrasikan, atau disetujui sebagai pengganti.
Dokumentasi resmi dan metadata terpasang mendukung audit ini. Kepastian hukum distribusi gabungan publik belum terselesaikan.
