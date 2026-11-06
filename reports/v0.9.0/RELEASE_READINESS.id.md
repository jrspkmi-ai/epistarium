# Kesiapan EPISTARIUM v0.9.0

Keputusan: **GO_BERSYARAT untuk audit paket lokal; HOLD untuk merge dan rilis publik** sampai CI lintas sistem operasi dan pemeriksaan integrasi yang belum dijalankan selesai. Metadata rilis mencatat `PENDING_CROSS_OS_CI`. Tidak ada izin publikasi atau push dalam paket ini.

Implementasi menyediakan ID run, rencana tahap, pencatatan event agen, token per run, validasi skema dan hash, spool replay, serta pemisahan laporan agen dari pengamatan Python. Persetujuan memakai kata sandi peninjauan terpisah dan menyimpan snapshot hash. Pemeriksaan integritas tidak mengesahkan temuan penelitian atau identitas peninjau.

Adapter mengharuskan host mengirim checkpoint secara eksplisit. Integrasi native dan cakupan pemantauan OpenCode maupun Antigravity belum diuji. Tidak ada jaminan bahwa semua aktivitas host tercatat. Tampilan browser langsung, macOS, dan Windows belum diuji pada pekerjaan ini. Hasil terdahulu tidak dipakai sebagai bukti uji versi ini.

ORIGO dan alur deterministik hanya menjalankan tahap yang inputnya tersedia. Status `NOT_RUN` harus dipertahankan. Uji sintetis bukan uji mutu akademik. Proses dengan kendali penuh atas akun sistem operasi yang sama berada di luar batas keamanan lokal. Gunakan satu server untuk setiap direktori penyimpanan privat.

Periksa `TEST_RESULTS.md`, dokumentasi EN/ID, dan changelog sebelum meninjau kode. Setelah audit pemilik, jalankan matriks CI dan uji host pada branch terpisah sebelum mempertimbangkan merge.
