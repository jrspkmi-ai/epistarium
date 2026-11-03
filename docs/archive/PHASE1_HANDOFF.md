# Handoff Epistarium Fase I

## Referensi pengembangan
Nama identitas publik final EPISTARIUM; 10 persona final menurut `docs/ROADMAP.md`; target seluruh platform AI yang kompatibel dengan skill, fokus praktis OpenCode, Antigravity, Codex, ChatGPT, Claude, Gemini. Implementasi dimulai Vanlan, lalu Liora, kemudian Agresa; Jorhas/orkestrator belum dibangun.

## Keadaan saat handoff
- Prototipe Python CLI untuk Vanlan, Liora, Agresa tersedia.
- 14 unit/integration-local tests lulus pada dataset sintetis. Bukan verifikasi dunia nyata atau kompatibilitas lintas perangkat.
- Demo PDF anotasikan teks dengan koordinat hasil pencarian, metadata dan laporan CSV/JSON/RIS tersedia.
- Panggilan jaringan Python ke Crossref gagal pada lingkungan pengembangan, sehingga tes API live tertunda.
- Agresa belum memiliki koneksi autentikasi resmi Scopus / WoS / SINTA; mode bukti input manusia konservatif.
- Tidak ada pengiriman/ubah GitHub, rilis atau penetapan lisensi.

## Prioritas sprint berikutnya
1. Vanlan: uji korpus PDF akademik nyata yang memiliki izin pemakaian; OCR (opt-in); ketepatan segmentasi kutipan multiline; matching berdasarkan DOI dan bibliografi; UI pemilihan bukti; audit semantik oleh agen dengan checklist penolakan/negasi; validasi highlight kompleks dan nomor cetak.
2. Liora: tes internet Crossref, adapter OpenAlex dan sumber lain, query Boolean yang dibangun per provider, pagination, pengendalian rate, pemilahan jenis artikel, verifikasi DOI resolve, pemisahan precision tanggal dan versi online-first, penyaringan relevansi ilmiah.
3. Agresa: parser resmi Source List Scopus, snapshot Master Journal List, pengambilan bukti SINTA beserta masa akreditasi; cek akses dan aturan perizinan; pemeriksaan langsung rekam artikel melalui provider yang sesuai.
4. Audit lintas platform dan perangkat: OpenCode, Antigravity, Codex, ChatGPT, Claude, Gemini; uji Windows/macOS/Linux; panduan pengguna dengan screenshot.
5. Validasi keamanan, hak cipta dataset, izin template, penentuan lisensi open-source, approval GitHub.

## Gerbang rilis
Sebelum push/rilis, pengguna harus menerima ringkasan perubahan, log pengujian, pemetaan risiko dan rekomendasi lisensi; meminta tindakan GitHub secara eksplisit. Jangan menggunakan data privat atau materi PDF penerbit sebagai fixture publik.

## Pembaruan stabilisasi Vanlan v0.1.1 (3 November 2026)

Tes lokal diperluas menjadi 28 PASS, ditambah uji privat pada 6 PDF akademik dan 12 anchor bukti. Kesimpulan semantik masih membutuhkan penilaian manusia. Baca `docs/VANLAN_STABILIZATION.md` dan `reports/F1_VANLAN_STABILIZATION_SUMMARY.md`. P03 Agresa serta P04 Liora masih harus ditangani dalam stabilisasi F1 sebelum F2 dapat mengandalkan semua hasil secara lebih luas.

## Pembaruan penutupan internal F1 v0.1.2-alpha (3 November 2026)

- P03 konflik ISSN/judul Agresa: **diperbaiki, tes negatif PASS**. P04 eksklusi karya empiris lama pada Liora: **diperbaiki, tes kebijakan waktu PASS**.
- Total 50 tes otomatis PASS di Linux; perintah dan matriks tercatat dalam `reports/F1_FINAL_GATE_v0.1.2.md`.
- Validasi Vanlan enam PDF privat diulang; keenam PDF anotasi preservasi teks dan 12 anchor cocok dengan kunci manusia. PDF privat tetap berada di luar paket kode.
- Crossref live: BLOCKED DNS. Indeks Scopus/WoS/SINTA: belum ada pemeriksaan portal langsung.
- Gerbang F2: **lanjut bersyarat** untuk pengembangan Retho/Domares/Synthia, selama label metadata/abstrak/full-text dan verifikasi indeks tetap konservatif. **Bukan persetujuan GitHub atau rilis publik.**
