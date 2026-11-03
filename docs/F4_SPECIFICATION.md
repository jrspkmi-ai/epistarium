# EPISTARIUM F4 | Spesifikasi Jorhas Master Diving v0.5.0

## Identitas dan sasaran
Jorhas, The Path Finder, adalah persona ke-10 sekaligus pengarah sembilan spesialis: Vanlan, Liora, Agresa, Retho, Domares, Synthia, Ideon, Quilo, dan Huxley. Identitas publik: EPISTARIUM, Research Intelligences. Skill adalah prosedur yang dapat dijalankan, bukan persona yang mengarang aksi.

## Dua mode
- **Path Finding Mode** (utama): ide -> source plan -> harvesting izin -> data/source ledgers -> pemeriksaan kecocokan -> 3 peluang fokus -> dossier, gaps dan run log. Tidak memerlukan statistik jika bukti kualitatif lebih sesuai.
- **Full Research Mode**: Path Finding -> Liora -> Agresa -> Retho -> Domares -> Synthia -> Vanlan -> Ideon ORIGO -> Quilo -> Huxley, berdasarkan dependensi. Langkah bisa `NOT_RUN`, `BLOCKED`, `FAILED`. Implementasi sekarang **tidak** memiliki otonomi model untuk menyimpulkan novelty atau menghasilkan proposal final tanpa manusia.

## Modul dan batas
1. `pathfinder_harvest.py`: pencarian sumber dan adapter jaringan terbatas. World Bank Indicators API V2 (permintaan JSON), RSS dan CSV pengguna. Sumber BPS, Satu Data, WHO, GDELT, Google Trends adalah kandidat sumber dengan status NOT_RUN sampai adapter/izin diuji. Crossref dipakai lewat Liora ketika dipanggil dalam Full Mode. Tidak ada browser headless. Limit dan retry konservatif.
2. `pathfinder_ledger.py`: menyimpan provenance setiap nilai, catatan periode/unit/populasi, metode sampling, hak akses dan status. Penilaian heuristik otomatis hanya memberi flag dan tidak mengubah klaim menjadi `terverifikasi`.
3. `jorhas.py`: mengelola dua mode, keluaran, manifest, log, 3 fokus yang berbeda unit pertanyaan, dan panggilan lintas skill bila input tersedia. Semua keluaran draf/heuristik.

## Kontrak masuk
Path Finding minimal `idea` 3 sampai 1000 karakter. Opsional `as_of` ISO date, `timezone` IANA, `config` JSON, `fixture` sintetis, `--online` sebagai izin pengambilan jaringan. `config.sources` menampung daftar provider (worldbank, rss, local_csv) dan batas sumber. Full Research menggunakan flag yang sama, ditambah paths ke fixture Liora, bukti indeks Agresa, library PDF Retho, claims PDF Vanlan, dokumen Huxley, opsi ORIGO.

## Kontrak keluar
Rincian pada `docs/F4_CONTRACTS.md`. Sumber/rekaman data dapat berstatus unknown; `NULL` asli berarti tidak ditemukan dalam dokumen, bukan nol. Kesimpulan ilmiah tidak diciptakan dari ledger. Penautan DOI dalam crosswalk tidak menggantikan pemeriksaan substansi.

## Ketepatan metodologis
- Sumber data resmi atau survei probabilitas hanya dapat digeneralisasi sesuai populasi, definisi, desain sampel, ketidakpastian yang disediakan.
- Survei nonprobabilitas tidak boleh otomatis diklaim mewakili populasi nasional. Google Trends dan GDELT adalah indikator proksi, bukan ukuran kejadian absolut.
- Tahun saja tidak otomatis menjadi tanggal lengkap. Data nasional tidak otomatis mengukur satu lokasi/organisasi.
- Jika dua sumber berbeda populasi, definisi, satuan, geografi, atau sampling, beri flag `TIDAK_SEBANDING`; jangan menghitung perubahan/laju gabungan otomatis.
- Jangan menyatakan `research gap` final tanpa penelusuran sistematis serta pembacaan dan evaluasi pustaka secara benar.

## Risiko dan gerbang
Rilis publik HOLD sampai integrasi live, pengujian lintas platform, validasi ilmiah manusia, privasi, serta lisensi (termasuk PyMuPDF) selesai. F4 dapat menjadi baseline alpha internal. Satu output referensi tidak menjadi klaim `verified` hanya dari persamaan DOI atau pencocokan string.
