# Keputusan audit dan patch v0.5.0

Empat masukan berasal dari berkas dalam `Hasil_Audit_4_Model.zip`. Nama model di sini mengikuti label berkas yang diberikan pengguna; identitas layanan/model tidak diverifikasi secara independen. Temuan diterima berdasarkan kecocokannya dengan kode dan reproduksi, bukan banyaknya model yang menyetujuinya.

## Kontribusi terkuat setiap audit

| Audit berlabel | Masukan yang paling bernilai | Keputusan |
|---|---|---|
| OpenAI GPT-6.1 Sol melalui OpenCode | Status bukti dari input, referensi sumber setelah deduplikasi, kelengkapan hasil modul, DOI kosong sebagai kunci | Prioritas pertama. Tiga reproduksi baseline mengonfirmasi kegagalan status ledger, relasi sumber dan status DOCX |
| Claude Opus melalui Antigravity | Portabilitas XLSX, doctor, versi tunggal, dokumentasi yang bertentangan | Diterapkan; artifact_tool dihapus dari runtime dan tes XLSX |
| Gemini Argon melalui Antigravity | Bahan Path Finding belum diteruskan ke ORIGO, seksi Domares, discovery dari root, dukungan DOCX Quilo | Diterapkan dengan batas heuristik dan pemeriksaan root, tanpa menjanjikan integrasi native |
| GLM Flash melalui OpenCode | Pemicu ID/EN, langkah persiapan, peta pipeline, kamus status dan pemeriksa rujukan | Diterapkan pada sepuluh panduan dan dokumen aktif; uji agen dipisahkan dari uji Python |

## Bukti sebelum patch

`reports/v0.5.0/baseline_reproductions.json` mencatat input `didukung sebagian`, `bertentangan` dan `tidak ditemukan` diterima sebagai status ledger; `source_id=B` tersisa ketika sumber B dihapus; kegagalan pembentukan DOCX ORIGO dilaporkan SUCCESS oleh orkestrator. Reproduksi memakai bahan sintetis dan kegagalan ekspor yang disuntikkan, bukan naskah atau data riset nyata.

Pengumpulan suite baseline terhenti karena artifact_tool tidak tersedia. Subset portabel menghasilkan 189 lulus, dua tes XLSX dikecualikan dan tujuh tes pada modul dengan impor artifact_tool belum terkumpul. Laporan terdahulu tentang 198 tes tidak disalin menjadi hasil pengujian baru. Pada v0.5.0, 198 tes lama dimigrasi agar dapat dijalankan kembali; log hasil akhir tercatat di laporan rilis.

## Paket patch yang dipilih

| Kelompok | Perbaikan | Alasan pemilihan |
|---|---|---|
| Integritas keputusan | Simpan source_claimed_status, tahan semua status input ledger, boolean ketat, nilai mentah dan alasan parsing | Mencegah status sumber diperlakukan sebagai adjudikasi |
| Provenance | Alias/riwayat akses sumber, rekonsiliasi source_id, article_id stabil dan unik | Menutup relasi terputus dan salah sambung artikel tanpa DOI |
| Orkestrasi | Periksa berkas wajib, DOCX/XLSX, stage_results, folder baru dan hash ringkasan | Fungsi selesai tidak cukup untuk menyatakan hasil lengkap |
| Portabilitas | openpyxl untuk ekspor/merge/gold, doctor lazy import, versi tunggal | Menjalankan fitur pokok pada lingkungan Python umum |
| Kontrak | Schema bertipe, validasi runtime pada ledger/keluaran F2/manifest dan input klaim CLI, schema tersedia di wheel | Mengubah dokumen kontrak menjadi pemeriksaan yang dijalankan |
| Kualitas kandidat | Konteks ledger pada peluang/ORIGO, prioritas seksi Domares, pembacaan DOCX Quilo dan tingkat revisi | Memperbaiki kegunaan dengan status epistemik tetap terbatas |
| Jaringan | DNS publik dan koneksi IP yang diperiksa, limit robots/cache, transport bersama Liora/Huxley | Menutup jalan akses internal dan respons tak terbatas pada klien bawaan |
| Pemakaian | Root paket langsung, router tugas, pemicu ID/EN, setup, kamus status dan pemeriksa rujukan | Mengurangi asumsi agen tentang lokasi, kesiapan dan arti hasil |
| Pengujian | Regresi kegagalan ekspor, relasi sumber, artikel tanpa DOI, formula sel, transport dan CLI; konfigurasi CI | Menguji kondisi yang benar-benar bisa menghasilkan laporan menyesatkan |

## Usulan yang ditunda atau dibatasi

- Adjudikasi AI terlacak memerlukan kontrak review, pengujian konteks kutipan dan benchmark. Pencocokan kutipan saja belum mengesahkan makna. Belum ditambahkan status AI yang setara keputusan manusia.
- OpenAlex, WHO, GDELT, pagination baru, Zotero/RIS/BibTeX, OCR, MCP dan UI review memerlukan pengembangan tersendiri. Penambahan provider tidak menyelesaikan masalah integritas baseline.
- Ekspor Huxley ke Vanlan dan pemindaian folder PDF otomatis belum dibuat. Peta alur menyebut bagian yang masih manual agar tidak memberi kesan ada jembatan executable.
- Perubahan backend PDF atau penetapan lisensi tidak diputuskan hanya dari nasihat audit model. Rilis ini tidak menetapkan lisensi atau dipublikasikan ke layanan luar.
- Symlink otomatis ke folder induk tidak dipakai. Paket disusun dengan satu root yang jelas; penemuan skill tetap dibuktikan per host.
- Seluruh keluaran ID/EN belum dilokalkan. Bahasa utama tetap Indonesia, dengan pemicu pencarian dua bahasa.
- Perombakan CLI menjadi registry dan pemformatan seluruh kode ditunda karena memperluas diff tanpa menutup kegagalan utama. Alias lama yang sah dipertahankan.

## Batas keputusan rilis

v0.5.0 adalah versi paket yang diserahkan kepada pemilik. Evaluasi ilmiah pada korpus independen, uji live provider dan pemasangan native perangkat pengguna tetap mempunyai status tersendiri. Konfigurasi CI bukan hasil CI yang sudah berjalan. Lihat `reports/v0.5.0/RELEASE_GATE.md` untuk hasil aktual.
