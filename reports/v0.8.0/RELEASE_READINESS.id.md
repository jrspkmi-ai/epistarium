# EPISTARIUM v0.8.0 | Kesiapan Rilis

**Versi:** 0.8.0, Release Candidate. **Keputusan:** GO_BERSYARAT untuk cabang GitHub khusus peninjauan. HOLD untuk merge ke `main` atau pembuatan rilis publik sampai CI lintas OS dan uji browser langsung selesai.

Implementasi mencakup dashboard empat kolom yang dibuat mandiri, sepuluh simbol persona 2D, EN sebagai bawaan dan ID sebagai pilihan, mode gelap/terang, SSE lokal, peristiwa aktual dari Jorhas, riwayat, rekaman sumber/data, pratinjau artefak, serta persetujuan yang mengendalikan akses luar dan otorisasi paket lokal.

Pengujian Python 399/399 PASS, dokumentasi dan skill PASS, serta Chromium offline PASS. Browser yang membuka localhost secara langsung BLOCKED oleh lingkungan kontainer. Instalasi bersih menggunakan dependensi yang disyaratkan dan GitHub Actions pada versi baru berstatus NOT_RUN.

Langkah wajib sebelum merge: uji instalasi bersih, CI Windows/macOS/Linux, pengujian browser langsung, peninjauan lisensi, dan pemeriksaan diff agar aset merek serta workflow GitHub terbaru tidak tertimpa.

Persetujuan peneliti untuk melepas artefak tidak berarti sumber terverifikasi, dan keberhasilan tes sintetis tidak membuktikan mutu penelitian empiris.
