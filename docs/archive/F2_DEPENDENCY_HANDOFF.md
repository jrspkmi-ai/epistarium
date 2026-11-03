# Handoff F1 v0.1.2-alpha untuk F2

## Baseline yang dapat digunakan
Arsip `EPISTARIUM_FASE_I_STABILIZED_v0.1.2-alpha.zip` mencakup Vanlan, Liora, Agresa dengan 50 tes lokal lulus. `reports/F1_FINAL_GATE_v0.1.2.md` adalah keputusan pemeriksaan internal. GitHub dan rilis publik belum disetujui.

## Langkah F2 yang disarankan
1. Retho: terima `candidates.json` Liora yang hanya berisi metadata; cari versi legal PDF dengan provenance, hak akses, dan jenis versi (published/accepted/preprint). Jangan menyebut teks lengkap ditemukan tanpa pemeriksaan file.
2. Domares: terima dokumen full-text teridentifikasi dari Retho, lakukan ekstraksi berhalaman dan audit kritis; jika hanya abstrak/metadata, keluarkan status terbatas. Jangan mengambil label indeks dari Agresa sebagai fakta indeks final.
3. Synthia: masukkan hasil Domares ke matriks literature review 20 kolom, sertakan dukungan halaman dan keterbatasan corpus. Periksa kompatibilitas template fisik jika file workbook tersedia.

## Penanda yang tidak boleh dihapus saat mengintegrasikan
- Liora: `scope`, `time_policy`, `recency_tag`, `publication_date`, `date_precision`, `available_level`, `fulltext_read=false`, `source_database`, `query_url`.
- Agresa: `identity_match`, `status_jurnal`, `status_artikel`, `evidence_checked_at`, `independent_verification=false`, `verification_level`.
- Vanlan: `literal_match_status`, `semantic_support_status`, `evidence_locations`, `pdf_sha256`, `printed_page`, `reviewer`.

## Gerbang epistemik
Keterbatasan API Crossref live, verifikasi indeks resmi, semantic review, dan hak akses full-text tetap nyata. Jika konektor tidak berjalan, laporkan `BLOCKED`/`NOT RUN`. Jangan mengganti keterbatasan dengan DOI, halaman, sitasi, atau hasil yang direka.

## Cara melanjutkan
Mulai F2 dengan Prompt F2 dari Playbook V1.1 dan lampirkan ZIP F1 v0.1.2-alpha serta laporan gerbang. Tidak perlu mengulang pembuatan F1 dari nol. Fase III berisi Ideon, Quilo, dan Huxley sesuai Playbook V1.1 (10 persona).
