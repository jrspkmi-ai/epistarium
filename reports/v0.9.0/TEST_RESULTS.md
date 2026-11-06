# Hasil pengujian EPISTARIUM v0.9.0

Baseline: `jrspkmi-ai/epistarium` main, commit `7e35e4b34c253f3936476da9ee6eaefe40744ceb`. Pengujian menggunakan Linux dan Python 3.12.14 dengan data sintetis. Keluaran penelitian privat tidak dimasukkan ke paket.

| Pemeriksaan | Hasil dan cakupan |
|---|---|
| Regresi Python | 431 tes lulus pada putaran terakhir yang selesai. |
| Doctor dan pip check | Lulus pada lingkungan Linux lokal. |
| Tutorial sintetis | Bahasa Inggris dan Indonesia lulus; artefak wajib tersedia. |
| Keamanan dan integrasi lokal | Tes loopback mencakup token lintas run, Host/Origin, skema, ukuran, status palsu, traversal, hash, replay, gate, dan perubahan artefak. Ini bukan penetration test independen. |
| Konsistensi | Verifikasi 10 skill, versi, tautan dokumentasi, pemeriksaan bahasa Inggris, dan sintaks JavaScript lulus. |
| macOS, Windows, CI baru | NOT_RUN di lingkungan ini. Workflow CI sudah disiapkan, belum dieksekusi pada perubahan ini. |
| Browser aktual | NOT_RUN. Chromium tidak tersedia; pemeriksaan statis dan HTTP/SSE bukan pengganti pengujian visual. |
| Host native | OpenCode dan Antigravity NOT_TESTED. Adapter shell diuji melalui loopback sintetis. |
| Akses langsung dan mutu ilmiah | NOT_RUN / NOT_ASSESSED. Pengujian tidak mengesahkan sumber atau kesimpulan akademik. |

Persetujuan memakai kata sandi yang dibuat pada terminal interaktif. Server tanpa kata sandi menonaktifkan approval. Identitas manusia dan perlindungan dari proses lain dengan akses penuh ke akun OS yang sama tidak dapat dipastikan oleh mekanisme lokal ini.
