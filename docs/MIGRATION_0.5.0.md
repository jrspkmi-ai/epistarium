# Migrasi ke v0.5.0

1. Simpan baseline dan hasil run lama. Ekstrak v0.5.0 pada folder terpisah, lalu buka root dengan `pyproject.toml` dan `.agents`.
2. Buat lingkungan Python baru dan pasang `.[test]`. Jalankan `doctor`; `artifact_tool` tidak dipakai lagi.
3. Gunakan folder keluaran baru. CLI menolak folder terisi; Jorhas juga menegakkan aturan ini pada fungsi Python-nya.
4. Data Ledger bertambah dari 45 menjadi **48 kolom**: `source_claimed_status`, `nilai_raw`, `nilai_parse_error`. `nilai` hanya angka hingga atau null. `synthetic` harus boolean, bukan string.
5. Status sumber selalu dipisahkan dari status keputusan ledger. Impor ulang bahan mentah dengan v0.5.0 jika ingin normalisasi baru; jangan menyatakan laporan lama sudah mempunyai pengaman baru.
6. Source Ledger bertambah dua kolom: `source_aliases`, `access_attempts`. ID data mengacu ke sumber kanonis dan riwayat percobaan tetap tersedia.
7. Gunakan `article_id` untuk menghubungkan Liora, Retho dan Domares. Kunci `library.json` boleh berupa ID artikel atau DOI yang tidak kosong. DOI tetap atribut identitas tambahan.
8. Skrip pemanggil harus menangani exit code `3` (parsial), `4` (terhalang), dan `2` (input invalid). Contoh Jorhas sintetis di README memang menghasilkan `3`.
9. Quilo menerima DOCX untuk ekstraksi teks; keluarannya tetap TXT/diff. Format dan field Word pada sumber tidak ditulis ulang. Tabel dibaca; header/footer/footnote bukan cakupan pembaca Quilo ini.
10. Kontrak schema aktif dipaketkan di `epistarium/data/` dan dicerminkan di `schemas/`; pemeriksa rilis memeriksa kesamaannya. Nama schema v1 dipertahankan untuk kesinambungan, sementara pengetatan tipe dan perluasan kolom dibatasi oleh versi distribusi 0.5.0.
