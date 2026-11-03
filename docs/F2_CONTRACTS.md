# Kontrak pertukaran F2 (stabilization alpha 0.2.1)

## Dependensi F1
- Liora mengembalikan `candidates.json` berisi `records`, metadata DOI, judul, tanggal, sumber pencarian, serta tingkat akses yang **bukan** status full-text.
- Metadata/abstrak tidak boleh menghasilkan temuan atau metode empiris. Agresa tidak mengesahkan indeks artikel hanya dari status jurnal. Vanlan tetap membutuhkan adjudikasi semantik.
- F1 regresi 50 tes dinyatakan lulus pada runtime pengembangan sebelum pembangunan F2, lihat `reports/F2_TEST_RESULTS.txt`.

## 1. Retho
**Input** `candidates.json`: list kandidat atau objek `records` dari Liora.

**Opsional** `library.json`: peta DOI ke `{pdf_path, version, rights_basis}`. Tidak menyimpan PDF ke repo. Versi sah: `publishedVersion`, `acceptedVersion`, `submittedVersion`, atau padanan snake_case. Hak akses hanya catatan, bukan lisensi distribusi.

**Output** `articles.json`: list entri dengan `article_id`, `doi`, `source_database`, `query_url`, `status`, `metadata_level`, `document_version`, `access_rights`, `download_status`, `source_identity_status`, `fulltext_available`, `fulltext_read=false`, `pdf_path`, `pdf_sha256`, `oa_candidates`, `warnings`.

Status: `metadata_only`, `abstract_only`, `fulltext_local`, `pdf_needs_ocr`, `pdf_invalid_or_missing`, `identity_conflict`, `identity_review_required` (jangan baca otomatis). Versi `published`, `accepted_manuscript`, `preprint`, `unknown`.

Tidak adanya DOI pada halaman awal bisa menghasilkan identitas `unconfirmed`, bukan otomatis salah. DOI yang bertentangan memblokir tahap selanjutnya. Mode download otomatis **dinonaktifkan tanpa pengecualian** pada V0.2.1 walaupun --download diberikan; metadata OA tidak cukup untuk izin unduh.

## 2. Domares
**Input:** `articles.json` keluaran Retho.

**Output:** `critical_readings.json` list dengan `reading_level`, `reported_by_author` berisi kandidat excerpt per 13 kategori, `ai_audit_observations`, `field_presence`, `page_count`, `requires_human_review`, serta provenance dari Retho. `integrity_status` memeriksa SHA-256 sebelum dan sesudah ekstraksi; perubahan PDF membuat `reading_level=identity_or_integrity_conflict` dan bidang substantif kosong.

`reading_level=machine_fulltext_extracted` = teks PDF berhasil diekstraksi, **bukan** telaah metodologi atau bukti klaim yang sudah lolos audit. Semua excerpt diberi `verification_status=kandidat teks; perlu verifikasi makna dan konteks`. Pengecualian: abstrak saja, file hilang, konflik DOI dan PDF scan tidak boleh mengisi kategori studi.

## 3. Synthia
**Input:** `critical_readings.json` dari Domares.

**Output:** `database_literatur.csv` (20 header tetap), `database_literatur.json`, `audit_bukti.csv`, `sintesis_sementara.md`, `export_status.json`, `database_literatur.xlsx` melalui `openpyxl` pada instalasi standar v0.5.0. Input metadata berawalan karakter formula disimpan sebagai **literal aman**, bukan rumus aktif.

Bila pengguna menyertakan `--template-xlsx`, sistem mengimpor workbook, menemukan header 20 kolom resmi pada sheet `Database Literatur`, lalu **menambahkan** baris di bawah data terdahulu. Sheet lain dibiarkan tetap ada, sheet `Audit F2` diisi dengan bukti kandidat. Template sumber tidak ditimpa. Kegagalan menemukan header menghalangi ekspor XLSX, tetapi CSV/JSON tetap dihasilkan.

## Prinsip umum
1. `source_pdf_sha256`, `pdf_page` (1-based), `printed_page` (null bila tak yakin), DOI/URL dan status identitas harus dijaga.
2. Sumber belum tersedia berbeda dari hasil tidak mendukung suatu klaim.
3. Identifikasi kata kunci adalah detektor passage, belum analisis kritis atau sintesis ilmiah lengkap.
4. Workbook berlisensi atau berisi data pribadi disimpan privat. Data demo sintetis dapat disebarluaskan dengan label eksplisit.

## Batas kemampuan V0.2.1
Retho memeriksa identitas DOI dan kecocokan kata pada judul halaman awal secara heuristik. Domares hanya mendeteksi **kandidat cuplikan**, bukan mengadili hasil atau validitas metodologi. Synthia membuat matriks kandidat dan ringkasan sementara, tidak melakukan sintesis teori atau research gap final. Jangan menjadikan output ketiganya sebagai temuan penelitian tanpa peninjauan manusia.

## Addendum V0.2.2-alpha: evaluasi manusia dan preservasi workbook
- Synthia: pengguna dapat mengirim workbook aktif berisi hasil pembacaan manusia. Baris kandidat ditambahkan hanya jika DOI belum ada dan judul+tahun tidak bertentangan; jangan menimpa hasil penelaah. `template_merge_audit.json` mencatat artikel duplikat, konflik, dan jumlah baris baru. Ekspor ke template tidak boleh menambahkan entri sama hanya karena artikel sudah ada.
- Sheet `Audit F2` menyimpan kandidat passage terpisah dari baris yang telah ditelaah manusia. Sheet `Database Literatur` dan `Penjelasan Kolom` dipertahankan. Preservasi data dan pratinjau terbatas telah diuji pada workbook 6 artikel pengguna, bukan semua fitur Excel.
- Domares: `f2-gold-evaluate` membaca halaman yang dirujuk oleh catatan review manusia, lalu menghitung tumpang tindih dengan nomor halaman kandidat cuplikan. Status `PAGE_OVERLAP`, `NO_PAGE_OVERLAP`, `NO_CANDIDATE`, `GOLD_PAGE_UNAVAILABLE`. **Tidak ada status PASS semantik** karena kecocokan lokasi tidak menyatakan kesamaan klaim.
- Retho: `publisher_access_observation` adalah pencatatan akses yang diperiksa pada waktu/sesi tertentu. Status dapat meliputi `abstract_visible_restricted_fulltext`, `http_403_unverified`, `fulltext_link_not_access_verified`. `rights_proven=false`, `fulltext_verified=false` sampai dokumen lokal sah hadir dan benar-benar diperiksa. Gunakan `--publisher-observations <json>` pada CLI. Jangan menyimpulkan paywall hanya dari 403.
