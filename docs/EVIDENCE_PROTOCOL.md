# Kontrak bukti dan provenance V0.1

## Status substantif baku
`terverifikasi`, `didukung sebagian`, `bertentangan`, `tidak ditemukan`, `belum dapat diverifikasi`, `inferensi peneliti/AI`, `hipotesis atau rekomendasi`.

Status substansi harus disertai penjelasan ruang lingkup verifikasi, bukan tanda centang tanpa catatan. Mulai Vanlan V0.1.1, kecocokan literal/anchor dicatat terpisah sebagai `anchor_text_match_status`, sedangkan status substansi otomatis tetap `belum dapat diverifikasi` sampai ada adjudikasi manusia beridentitas dan beralasan. Dukungan substantif, konteks, negasi, angka, keterbatasan dan hubungan sebab-akibat tidak diputuskan oleh mesin pencocokan teks. Reviewer tercatat eksplisit dan tidak diklaim hasil AI otomatis.

## Objek provenance
`claim_id`, `claim`, `jenis`, `source_pdf`, `source_doi`, `source_identity_verified`, `source_match_status`, `pdf_sha256`, `pdf_page` (1-based), `printed_page` (hasil footer eksplisit atau null), `pdf_page_label` (label internal), `text_anchor`, `status`, `cakupan_keputusan`, `note`, `reviewer`, `tanggal_audit`, `highlight`.

Untuk metadata ilmiah, `query_url`, `source_database`, `observed_at`, `available_level`, `fulltext_read`, `doi`, `journal`, `year` dan alasan eksklusi.

Untuk indeks jurnal, `database`, `status_jurnal`, `status_artikel`, `coverage_start`, `coverage_end`, `source_url`, `checked_at`, `note`.

## Keputusan konservatif
- Hilang dari pencarian teks bukan berarti klaim salah.
- Ada dalam teks bukan berarti mendukung makna parafrasa.
- Ada jurnal di Scopus/WoS/SINTA bukan berarti artikel terindeks di sana.
- Halaman PDF berbeda dari halaman cetak; laporkan null jika footer/angka cetak tidak jelas.
- Bukti dari pengguna yang tampak berasal dari domain resmi belum menggantikan verifikasi isi sumber resmi pada waktu yang tepat.
- Periksa tanggal terbit vs tanggal peristiwa; jendela lima tahun fenomena tidak membatasi teori klasik.

## Kebijakan tambahan V0.1.2

- `fenomena`: query Crossref bisa diberi batas tanggal **publikasi** lima tahun; jangan menganggap ini sudah memverifikasi tanggal **peristiwa**.
- `empiris`: lima tahun adalah **prioritas**, karya lama tetap kandidat dan ditandai sebagai lebih lama; teori/konsep/metode tidak diberi batas otomatis.
- `available_level=metadata+abstract_metadata` bukan full-text. Field `fulltext_read` tetap false pada Liora.
- `Agresa.status_jurnal = cocok dengan catatan indeks yang diinput` hanya konsistensi arsip lokal; field `independent_verification=false` menghalangi klaim verifikasi langsung.
- Kecocokan ISSN dan judul harus diuji terhadap konflik. Untuk SINTA perlu periode akreditasi; untuk WoS perlu koleksi indeks. Artikel tidak otomatis terindeks ketika jurnalnya memiliki jejak indeks.
