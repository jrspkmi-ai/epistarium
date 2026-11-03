# Catatan perubahan EPISTARIUM

## 0.5.0 | 3 November 2026

Rilis stabilisasi sepuluh persona dari baseline 0.4.0a1. Penomoran rilis paket menjadi 0.5.0; hasil ilmiah setiap persona tetap mengikuti status bukti yang tercatat.

- Semua status ledger yang berasal dari sumber ditahan pada `belum dapat diverifikasi`. Status asal disimpan sebagai `source_claimed_status`.
- Deduplikasi mempertahankan alias dan riwayat akses, lalu memperbaiki referensi `source_id`. Setiap rekaman mempunyai sumber kanonis.
- `article_id` stabil diteruskan dari Liora ke Retho, Domares dan crosswalk. DOI kosong tidak dipakai sebagai kunci bersama.
- Orkestrasi memeriksa berkas wajib dan status DOCX/XLSX. Hasil tahap memisahkan eksekusi, kelengkapan artefak, dan bukti.
- Folder hasil yang sudah berisi berkas ditolak. Manifest Full Research mencakup ringkasan run yang sama.
- `openpyxl` menggantikan `artifact_tool` pada ekspor, penggabungan template dan evaluasi halaman gold. Teks sumber ditulis sebagai sel string.
- Kontrak ledger bertipe ketat, validator runtime, pemeriksaan ID unik dan schema yang tersedia di wheel. Perbaikan tambahan: JSON schema Synthia pada baseline memiliki satu kurung penutup berlebih.
- `doctor`, `--version`, alias `vanlan-extract --out`, kode keluar CLI, dan pembacaan TXT/Markdown/DOCX oleh Quilo.
- Domares memprioritaskan seksi relevan dan berhenti di daftar pustaka yang heading-nya terdeteksi. Tetap ekstraksi kandidat heuristik.
- Peluang Jorhas memuat konteks indikator/geografi/periode/isu dengan label scaffold; ORIGO menerima jejak ledger dan ID literatur.
- Transport HTTPS memeriksa seluruh jawaban DNS dan membuka koneksi ke IP publik yang telah diperiksa dengan hostname TLS tetap. Respons robots/cache dibatasi ukurannya; Liora dan Huxley memakai klien yang sama.
- Panduan aktif, deskripsi pemicu sepuluh skill, peta alur, kamus status, pemeriksa dokumentasi, dan konfigurasi CI tiga OS diperbarui.

Perubahan kontrak: Data Ledger bertambah dari 45 menjadi 48 kolom. Baca [panduan migrasi](docs/MIGRATION_0.5.0.md). Riwayat F1-F4 dipertahankan dalam [arsip](docs/archive/CHANGELOG_F1_F4.md).
