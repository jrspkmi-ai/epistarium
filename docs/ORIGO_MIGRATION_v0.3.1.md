# Migrasi Ideon ke ORIGO pada F3 V0.3.1

- Persona tetap Ideon, The Research Architect. ORIGO adalah mesin hasil karyanya, bukan persona ke-11. Total EPISTARIUM tetap 10 persona.
- Default `python -m epistarium ideon-design --input file.json --out folder` sekarang **ORIGO QUICK_MAP DOCX**; tidak lagi menghasilkan RMC 2.0. Input alias `ide` atau `topik` masih diterima.
- CLI khusus `ideon-origo` merupakan alias yang teruji.
- Pemanggilan kode Python lama `ideon.design()` dan `ideon.export()` tetap tersedia agar proyek lama tidak rusak, serta opsi CLI `--legacy-rmc`. Pemanggilan lama mempertahankan teori pilihan dan kelayakan akses yang benar.
- ORIGO memakai empat mode dan enam simpul vertikal; 21 pertanyaan ada dalam satu DOCX, QUICK_MAP tidak otomatis membentuk 21 esai.
- `ELABORATE_21` pada CLI hanya menyusun scaffold draf berbasis input yang tersedia dan label ketidakpastian. Saat evidence tidak ada, keluaran **bukan jawaban akademik final**. Agen dengan akses sumber dan pemeriksaan dapat mengembangkan argumentasi, kemudian peneliti harus melakukan audit.
- RMC asli milik pihak ketiga tidak disertakan; berkas ORIGO mengacu pada desain mandiri dari addendum. Sumber desain mempunyai hak kepemilikan yang belum diputuskan untuk publikasi.
- `REVISION` memerlukan `--previous-map` dan perubahan simpul eksplisit, sedangkan field lain tetap. Bila revisi pembimbing hanya dinyatakan sebagai teks umum tanpa simpul yang jelas, catat untuk peninjauan manual.
- Output JSON `schema_version=epistarium.origo.ideon.rfs.v1`; sistem downstream harus menggunakan `nodes`, `titles`, `questions`, `checks` dan status, bukan mengasumsikan `rmc_2_0` hadir pada default.

## Tiga tes lama yang disesuaikan karena kemampuan meningkat
- `test_huxley_missing_references_header`: dari UNMATCHED_CITATION menjadi MANUAL_REVIEW karena daftar referensi tidak tersedia.
- `test_huxley_annotates_exact_text_and_preserves_original`: kini harus mempunyai komentar Word native yang benar-benar tertambat.
- `test_huxley_multi_run_not_highlighted`: kini harus menemukan highlight literal lintas-run bila struktur teks aman.

Penyesuaian ekspektasi tercatat sebagai migrasi kontrak. Seluruh tes tetap dijalankan dan diberi status hasil aktual, bukan dihapus.
