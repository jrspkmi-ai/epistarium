# Handoff EPISTARIUM F2 V0.2.1 ke F3

## Status
F2 V0.2.1-alpha: GO bersyarat untuk implementasi F3. Tes lokal 76/76 lulus. Pengujian semantik 13 bidang dan template Excel asli belum dilakukan; rilis publik HOLD. Semua PDF akademik pengguna tetap privat.

## Kontrak yang tidak boleh dilonggarkan
- **Retho**: `source_identity_status` wajib jelas, hash SHA-256 wajib untuk PDF, `status=identity_review_required` harus memblokir penggunaan otomatis. Tautan OA tidak sama dengan PDF atau lisensi. Unduh otomatis DISABLED.
- **Domares**: `reading_level=machine_fulltext_extracted` hanya berarti teks mesin terekstrak; `integrity_status=hash_matched_before_after` bukan verifikasi makna. `reported_by_author` adalah kandidat passage; `ai_audit_observations` berisi catatan audit, bukan hasil sumber.
- **Synthia**: 20 header matriks tetap, metadata dan sel XLSX disimpan sebagai literal, status kandidat tidak dinaikkan menjadi temuan. `sintesis_sementara.md` bukan literature review substantif final. Format template pengguna harus diperiksa khusus.
- **Vanlan**: kecocokan literal tidak menjamin dukungan substantif; `semantic_support_status` memerlukan review.
- **Agresa**: index status dari input bersifat belum diverifikasi independen; tidak mengesahkan artikel terindeks.
- **Liora**: artikel empiris lama tidak dibuang otomatis; pembedaan fenomena lima tahun vs teori klasik tetap berlaku.

## Fase III (sesuai Playbook V1.1)
1. **Ideon**, The Research Architect: Topic Brainstormer, RMC 2.0 (enam komponen + judul, elaborasi 21 pertanyaan, minimal tiga kandidat judul).
2. **Quilo**, The Academic Scribe: Academic Writer. Style modular dengan Stop Slop sebagai pemeriksaan sekunder; jangan ubah angka/kutipan.
3. **Huxley**, The Citation Cartographer: Citation-Reference Auditor, APA 7 sebagai default. Cocokkan sitasi di naskah dengan daftar pustaka dua arah, temukan yang hilang/berlebih, rekomendasikan kandidat referensi yang memiliki bukti, bukan sisipan tanpa pemeriksaan.

## Larangan inferensi tidak sah
- Jangan mendasarkan state of the art, gap, novelty atau kesimpulan akademik final hanya pada keberadaan/ketidakberadaan kandidat passage.
- Bila dokumen hanya abstrak atau PDF konflik, jangan klaim full-text dibaca.
- F3 harus mempertahankan review manusia dan catatan provenance, tidak menciptakan status PASS baru tanpa tes.

## Tata kelola
GitHub belum disentuh. Jangan push/merge/rilis publik tanpa permintaan dan persetujuan terpisah. Pemeriksaan format dan lisensi harus dilakukan sebelum publikasi.
