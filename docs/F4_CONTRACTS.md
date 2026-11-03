# Kontrak F4: schema dan pertukaran antarskill

## Status berbeda domain
**Eksekusi:** `SUCCESS`, `PARTIAL`, `BLOCKED`, `FAILED`, `NOT_RUN`. `SUCCESS` berarti fungsi menghasilkan artefak wajib yang diperiksa, **tidak** mengesahkan interpretasi. `PARTIAL` berarti hanya sebagian pekerjaan tersedia.

**Bukti:** `terverifikasi`, `didukung sebagian`, `bertentangan`, `tidak ditemukan`, `belum dapat diverifikasi`, `inferensi peneliti/AI`, `hipotesis atau rekomendasi`. Untuk sumber tidak ditelaah manusia status default `belum dapat diverifikasi`; model tidak boleh mengubahnya sendiri.

## Schema versions
- Data Ledger: `epistarium.pathfinder.data.v1`, 48 field, lihat `epistarium/pathfinder_ledger.py::FIELDS` dan schema JSON.
- Source Ledger: `epistarium.pathfinder.sources.v1`, field `SOURCE_FIELDS`.
- Source Plan: `epistarium.pathfinder.source_plan.v1`.
- Research Opportunities: `epistarium.pathfinder.opportunities.v1`.
- Run Manifest: `epistarium.pathfinder.run.v1`.
- Full Manifest: `epistarium.jorhas.full.v1`.
- EVIDENCE_CROSSWALK: `epistarium.jorhas.crosswalk.v1`; ID LW-XXXX untuk kandidat dari Liora, article_id stabil menghubungkan Retho dan Domares; DOI menjadi atribut tambahan serta status pembacaan. Perbedaan tingkat verifikasi tidak dihapus.

## Data Ledger dan NULL
Minimal berisi record_id; jenis_data; kelompok_bukti; indikator; definisi_operasional; nilai/satuan; pembilang/penyebut; penerbit dan produsen; judul/URL/DOI/file_sha256/versi; tanggal peristiwa, observasi, periode referensi, publikasi, dan pengambilan; geografi/populasi/unit/cakupan/sampel/sampling; pengumpulan/perhitungan/representativitas/estimasi/bias; akses/lisensi/mutu/status; cuplikan/lokasi bukti/kaitan klaim/batas generalisasi. Kolom kosong adalah NULL atau belum diketahui; lihat flags.

## Integrasi dengan F1-F3
- Liora menghasilkan `candidates.json` dan metadata/abstrak, bukan bukti full-text.
- Agresa hanya dijalankan dengan jurnal dan bukti indeks yang dipasangkan; tanpa sumber tidak ada klaim indexed.
- Retho memakai kandidat Liora, kemudian PDF lokal berizin yang dinyatakan pengguna; tidak menerobos paywall.
- Domares hanya melakukan *candidate passage extraction* dan validasi hash PDF; `machine_fulltext_extracted` bukan semantic read verified.
- Synthia hanya dijalankan jika Domares memiliki full-text yang berhasil diekstraksi; database tetap kandidat review, bukan sintesis ilmiah final.
- Vanlan hanya jika klaim dan direktori PDF disediakan. Highlight literal dan substansi berstatus terpisah.
- Ideon default ORIGO QUICK_MAP/ELABORATE_21/BLUEPRINT/REVISION; **RMC tidak digunakan** sebagai kontrak standar.
- Quilo memisahkan penjagaan token dari kesetaraan semantik (`NOT_ASSESSED`).
- Huxley dapat diaudit bila DOCX pengguna ada; `MATCHED` tidak membuktikan dukungan klaim. Jangan mengisi daftar pustaka final dari kandidat daring.

## Semantik data dan logs
`RUN_LOG.json`: setiap langkah mencatat nama, command yang benar-benar dijalankan atau `not_invoked`, input/output dan hash SHA-256, status, waktu, biaya dan kuota bila diketahui, alasan error, serta model_called. Penanda `NOT_RUN` harus tetap terlihat. Manifest menyimpan tanggal/zona, versi, sistem operasi, sumber/adapter yang dicoba, durasi, hasil dan hash output. `fixture=true` selalu mengharuskan banner simulasi.

## Keamanan
CSV memakai escape literal untuk spreadsheet formula injection. Server HTTPS publik membatasi alamat dan tidak mengikuti redirect otomatis. RSS membutuhkan pemeriksaan izin dan robots.txt; transport bawaan memeriksa DNS dan memakai koneksi IP publik yang diperiksa; syarat situs tetap ditinjau per sumber. Tidak ada kredensial di repositori atau log. Jangan menyimpan PDF berlisensi pada distribusi.

## Perluasan v0.5.0

Data Ledger memiliki 48 kolom; status klaim sumber disimpan terpisah. Source Ledger memiliki 21 kolom termasuk alias dan riwayat akses. Validator runtime dan pemeriksaan hubungan ID dijalankan sebelum ekspor ledger. `stage_results` memisahkan execution_status, deliverable_status, evidence_status, artifacts, warnings dan errors. Folder run harus baru/kosong. Baca [migrasi](MIGRATION_0.5.0.md).
