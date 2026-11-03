# Kamus status EPISTARIUM v0.5.0

| Domain | Nilai | Arti operasional |
|---|---|---|
| Eksekusi tahap | `SUCCESS` | Fungsi menghasilkan artefak wajib yang diperiksa |
| Eksekusi tahap | `PARTIAL` | Sebagian lingkup pekerjaan tersedia |
| Eksekusi tahap | `BLOCKED` | Input, izin, lingkungan atau artefak wajib menghalangi penyelesaian |
| Eksekusi tahap | `FAILED` | Kegagalan eksekusi yang tidak diklasifikasikan sebagai hambatan biasa |
| Eksekusi tahap | `NOT_RUN` | Fungsi tidak dipanggil |
| Artefak | `COMPLETE`, `INCOMPLETE`, `NOT_REQUESTED` | Kelengkapan berkas per tahap, terpisah dari bukti |
| Ledger | `belum dapat diverifikasi` | Satu-satunya status hasil normalisasi input pada v0.5.0 |
| Metadata/sumber | `source_claimed_status` | Pernyataan sumber yang disimpan; tidak mengubah keputusan EPISTARIUM |
| Huxley | `MATCHED` | Pasangan sitasi-referensi ditemukan dalam subset parser |
| Vanlan | `anchor_text_match_status=cocok` | Teks literal dan posisi ditemukan; semantik tetap diperiksa tersendiri |
| Domares | `machine_fulltext_extracted` | Teks PDF berhasil diekstraksi; passage masih kandidat |
| Ideon | `DRAFT_PERLU_REVIEW_MANUSIA` | Peta rancangan tersedia untuk ditelaah |
| Quilo | `NOT_ASSESSED` | Kesetaraan makna belum dinilai |

Kosakata substantif proyek tetap: `terverifikasi`, `didukung sebagian`, `bertentangan`, `tidak ditemukan`, `belum dapat diverifikasi`, `inferensi peneliti/AI`, `hipotesis atau rekomendasi`. Vanlan dapat mengimpor keputusan manusia beridentitas dan beralasan sesuai kontraknya. Ledger Pathfinder v0.5.0 belum menyediakan perintah promosi status melalui review; jangan memasukkan review rekaan ke input untuk melewati pembatasan.

`Full Research.status=PARTIAL` menyatakan keluaran riset masih draf. `execution_status`, `deliverable_status`, `stage_statuses` dan `stage_results` memperinci hasil mekanisnya. Modul yang dijalankan dapat berhasil menghasilkan draf sementara tahap lain NOT_RUN. Tidak ada klaim penelitian final yang dihasilkan secara otomatis.
