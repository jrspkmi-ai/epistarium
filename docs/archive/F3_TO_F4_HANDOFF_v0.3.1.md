# Handoff F3 -> F4 | 0.3.1-alpha

## Baseline
ZIP EPISTARIUM_FASE_III_STABILIZED_v0.3.1-alpha.zip. Tiga persona F3 telah distabilkan; Jorhas belum dibuat. Identitas tetap 10 persona. Baca `reports/F3_STABILIZATION_GATE_v0.3.1.md` dan `docs/F3_CONTRACTS.md`.

## Kontrak F4 wajib
1. Ideon: `origo.export()` atau CLI `ideon-design/ideon-origo`; hanya bukti lokal dan input pengguna yang diproses, tanpa fetch otomatis; `docx_status`, `status=DRAFT_PERLU_REVIEW_MANUSIA`, `literature_status=NOT_RUN` harus diturunkan ke log.
2. Quilo: `safe_to_propose` berarti kandidat editorial terbatas; `semantic_validity=NOT_ASSESSED` wajib dipertahankan. Jangan klaim semantik PASS.
3. Huxley: `MATCHED` berarti korespondensi author-date, bukan substansi. Dokumen field dinamis tetap tidak tersunting; komentar Word hanya ketika anchor berhasil. Status tanpa heading pustaka `MANUAL_REVIEW`.
4. Retho/Domares/Synthia/Vanlan/Agresa/Liora: gunakan kontrak F1/F2 dan matriks status, bedakan full-text, abstrak, metadata, hash, dan keterbatasan indeks.
5. Seluruh pemanggilan eksekusi oleh Jorhas harus punya input, output path, waktu, status PASS/PARTIAL/BLOCKED, hash bila perlu, provenance, biaya/kuota jika tersedia. Tidak boleh mengarang pemanggilan tools.
6. Mode discovery/full research hendaknya berhenti sebelum klaim final tanpa sumber terverifikasi dan review manusia. Hasil dapat menjadi blueprint atau draft yang dapat ditindaklanjuti.

## Risiko
Native app/platform NOT RUN; akses API/bibliografi external belum dijamin; pemahaman semantik F2/F3 masih terbatas. Tes integrasi dari topik mentah harus menggunakan skenario sintetis/berizin, audit kegagalan API dan konflik DOI. Lisensi dan publikasi tetap memerlukan persetujuan eksplisit.

## Status GitHub
Tidak ada commit, push, repo creation, rilis, atau perubahan visibilitas dilakukan pada F3 Stabilization.
