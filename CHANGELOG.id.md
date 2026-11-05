# Changelog

## v0.8.0 Research Observatory (Kandidat Rilis, 4 November 2026)

- Menambahkan pemantauan SSE lokal atas checkpoint eksekusi Python Jorhas dan status sepuluh persona.
- Menambahkan dashboard empat kolom sesuai rancangan terpilih dengan ikon persona orisinal.
- Menambahkan EN/ID (bawaan EN), mode gelap/terang, jumlah rekaman bukti, pratinjau, dan linimasa aktivitas.
- Menambahkan persetujuan yang menghentikan akses jaringan hingga diberi izin dan mengatur otorisasi paket artefak lokal.
- Memisahkan status eksekusi dari status verifikasi; persetujuan tidak mengubah bukti ilmiah menjadi terverifikasi.
- Menambahkan HTTP lokal, token sesi, pemeriksaan Host/Origin, pembatasan pratinjau teks, serta perlindungan traversal.
- Menambahkan tes unit, HTTP/SSE, skema JSON, dan rendering Chromium offline.
- Menunggu verifikasi: pembukaan browser pada setiap OS, browser-ke-server langsung di lingkungan desktop tanpa pembatasan, dan GitHub Actions pada commit baru.


## 0.7.0 RELEASE_CANDIDATE

Provenance halaman cetak Domares, tata letak footer ORIGO, JSON doctor, penanganan entitas XML, dan hak sumber bawaan diperbaiki.

Pemberitahuan MIT karya orisinal, gerbang lisensi dependensi, batas versi PDF, tiga panduan OS, sepuluh panduan platform, dan adaptor Claude terkelola.
Tutorial pemula berpasangan, penelitian sumber, pemeriksaan tautan/cakupan, persiapan CI, dan bukti rilis terkini. Rilis publik: HOLD.

[Catatan rilis](docs/id/releases/v0.7.1.md)

# Catatan perubahan

[English](CHANGELOG.md) | Bahasa Indonesia

## 0.6.0 | 3 November 2026

Tambahkan bahasa Inggris ke implementasi yang sama dengan sepuluh persona.

- Tambahkan --lang id, en dan auto sebelum atau sesudah subperintah.
- Dukung EPISTARIUM_LANG, field language serta argumen lang= pada API masuk penelitian.
- Pulihkan konteks bahasa setelah pemanggilan agar tugas lain tidak terpengaruh.
- Terjemahkan pesan program, laporan, pertanyaan ORIGO dan label workbook baru.
- Pertahankan kunci data utama, kode status, nama berkas dan bahan sumber.
- Tambahkan CSV display Inggris tanpa mengganti CSV utama.
- Terima alias Inggris untuk input serta revisi ORIGO dengan deteksi konflik.
- Terima dua set header workbook yang dikenal untuk merge dan pembandingan halaman.
- Tambahkan preset Quilo academic-en tanpa penulisan ulang otomatis.
- Dukung deskripsi sampling, rujukan halaman serta penanda risiko suntingan dalam Bahasa Inggris.
- Sediakan panduan rujukan ID dan EN di setiap entrypoint persona yang sama.
- Terapkan SimpleEnglish Plain 2.1.1 dan simpan atribusi serta pemberitahuan MIT sumbernya.

Riwayat lama tetap pada docs/archive/CHANGELOG_v0.5.0.md. Hasil aktual rilis berada di reports/v0.6.0/RELEASE_GATE.md.
