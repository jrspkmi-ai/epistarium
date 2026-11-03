## 0.4.0-alpha (2026-11-03)
- Tambah Jorhas Master Diving, Path Finding/Full Research CLI, Harvest adapters (World Bank JSON V2, RSS berizin, CSV lokal), Data/Source Ledger, manifest/hash, crosswalk DOI dan logging lintas spesialis.
- Pertahankan baseline F1-F3 v0.3.1-alpha tanpa mengganti kontrak ORIGO maupun mereklasifikasi metadata sebagai bukti.
- Batas rilis: hanya alpha internal; akses live dan validasi native antarplatform belum terbukti.

# F3 v0.3.0-alpha (3 November 2026, lokal tanpa GitHub)

- Menambahkan Ideon (`ideon-design`): 3 judul berbeda fokus, RMC 2.0, 21 jawaban kerangka, pemeriksaan kelayakan awal dan status bukti konservatif. Belum ada pencarian ilmiah otomatis dalam CLI.
- Menambahkan Quilo (`quilo-audit`): preset publik netral, lint, diff, pemeriksaan preservasi angka, DOI, sitasi, kutipan. Bukan validasi kesamaan makna.
- Menambahkan Huxley (`huxley-audit`): parser author-date APA7 sebagian, pencocokan dua arah, ambigu, metadata Crossref opt-in, highlight DOCX presisi terbatas, penjagaan field dinamis. Native comments NOT IMPLEMENTED.
- Menambahkan tes dan fixture sintetis serta laporan gerbang F3. Status kesiapan alpha internal, bukan rilis. F1/F2 kontrak lama tetap berlaku.

## 0.2.1-alpha | 3 November 2026 | F2 Stabilization

- Retho: blokir unduh daring tanpa pengecualian, cegah DOI dalam daftar pustaka diterima sebagai identitas artikel, periksa kesesuaian kata judul; status `identity_review_required` pada bukti belum meyakinkan.
- Domares: pemeriksaan hash sebelum/sesudah membaca, blokir perubahan PDF, penomoran cetak memakai detektor konservatif Vanlan, kurangi kandidat hasil palsu akibat penyangkalan eksplisit dan DOI.
- Synthia: cegah injeksi formula pada ekspor XLSX (bukan hanya CSV), perjelas ekspor template serta status kandidat bukti yang belum dinilai.
- Sinkronisasi dokumentasi sesuai Playbook V1.1: **10 persona**, Huxley The Citation Cartographer pada Fase III, kompatibilitas lintas platform berbasis kemampuan yang teruji.
- Tes regresi sintetis ditambahkan; pengujian PDF akademik nyata tetap privat dan dilaporkan hanya sebagai keterbacaan/identitas/bukti hash.
- Tidak ada push GitHub, lisensi/rilis publik belum diputuskan.

# Changelog EPISTARIUM (pengembangan lokal)

## 0.1.2-alpha | 3 November 2026 | F1 Stabilization Complete for Internal F2 Handoff

- Liora: memisahkan *batas publikasi default fenomena* dari *prioritas lima tahun literatur empiris*, menangani presisi tanggal di batas, mempertahankan studi klasik, mencatat DOI/abstrak/full-text secara konservatif, log kegagalan API BLOCKED, dan memperbaiki ekspor RIS.
- Agresa: konflik ISSN dan judul tidak lolos sebagai indeks, pasangan ISSN/e-ISSN ditangani, WoS memerlukan koleksi, SINTA memerlukan riwayat periode akreditasi, dan status jurnal dipisahkan dari artikel.
- Kontrak keluaran Agresa menjadi `cocok dengan catatan indeks yang diinput`, `independent_verification=false` dan penanda pemeriksaan manusia. Tidak ada verifikasi portal independen yang diklaim.
- 22 tes tambahan/skenario kebijakan dan negatif; total 50 tes PASS. Enam PDF nyata Vanlan divalidasi ulang privat.
- API Crossref live BLOCKED DNS; kompatibilitas aplikasi AI/macOS/Windows NOT RUN.
- Tidak ada tindakan GitHub atau rilis.

# Changelog

## 0.1.1-alpha (Vanlan stabilization, 2026-11-03)
- Konsensus nomor halaman cetak; cegah tahun/nomor artikel dianggap halaman.
- Pemetaan sumber DOI unik, penolakan DOI tidak cocok, dan pemisahan identitas PDF vs nama berkas.
- Pemisahan status literal/anchor dan substansi, dengan review manusia teratribusi.
- Anotasi multi-anchor, deduplikasi highlight, penanganan ligatur dan validasi integritas salinan PDF.
- Tambahan 14 tes regresi lokal di atas 14 tes lama, semua 28 lulus setelah perubahan.
- QA privat pada enam artikel akademik yang diunggah pengguna; tidak disertakan dalam paket kode.
- Agresa dan Liora tetap baseline sebelumnya, tanpa perubahan perilaku.

## 0.1.0-alpha (F1 baseline)
- Vanlan, Liora, Agresa prototipe dengan 14 tes awal.

## 0.2.0-alpha (F2 internal, 2026-11-03)
- Retho: pemeriksaan legalitas akses, versi PDF, konflik DOI, tautan OA vs file yang diunduh.
- Domares: deteksi kandidat passage pada full-text, provenance halaman, pemisahan authors vs audit AI.
- Synthia: matriks 20 header, catatan halaman, sintesis sementara, ekspor CSV/JSON/XLSX bila tersedia.
- Kontrak F1 tidak diubah. GitHub belum disentuh, tidak ada lisensi/rilis publik.

## V0.2.2-alpha | 3 November 2026 | F2 QA dengan bahan pengguna
- Synthia: impor dan ekspor diuji menggunakan `Template Literatur Review V1.xlsx` asli (6 baris review manusia). Tambahkan pemeriksaan DOI serta judul+tahun sebelum mengisi baris; jangan menggandakan atau menimpa hasil review manusia. Konflik identitas ditahan, cuplikan otomatis tetap dicatat pada `Audit F2` dan `template_merge_audit.json`.
- Domares: adaptor evaluasi `f2-gold-evaluate` membandingkan lokasi kandidat dengan rujukan halaman pada workbook yang diperiksa manusia. Hasil overlap halaman **bukan** ukuran akurasi semantik.
- Retho: menerima catatan pembatasan akses dari pemeriksaan halaman penerbit (`--publisher-observations`) sebagai provenance tidak otoritatif; `/full/` dan metadata OA tidak otomatis mengesahkan full-text. Download otomatis tetap DISABLED.
- Pengujian: regresi bertambah dari 76 menjadi 83 tes sintetis; QA privat enam artikel, template asli, dan tiga laman penerbit. Artefak artikel dan review pengguna dikecualikan dari paket kode publik.
- Gerbang: GO bersyarat untuk pembangunan F3 dengan review manusia; HOLD untuk klaim sintesis akademik penuh, unduh daring otomatis, dan publikasi GitHub.

## 0.3.1-alpha (3 November 2026) | F3 Stabilization, ORIGO Fix 1
- Ideon: `origo.py` dengan QUICK_MAP, ELABORATE_21, BLUEPRINT dan REVISION. Satu DOCX dua bagian berisi 6 simpul berurutan, tiga judul dan 21 langkah; alias CLI legacy dijaga. Teori, RQ, paradigma, metode dan constraint akses pengguna dipertahankan. Keluaran bersifat DRAFT dan tidak mengarang gap.
- Ideon legacy: perbaikan pemilihan judul ketika korpus tidak tersedia, mempertahankan teori dan metode yang dipilih; tiga tes ekspektasi kontrak lama disesuaikan sesuai catatan migrasi.
- Huxley: perbaikan penulis kedua `and`/`dan`/`&`, tahun jamak, span sitasi berulang, highlight lintas run, anotasi referensi tak dikutip, status MANUAL_REVIEW bila heading daftar pustaka tidak ada; komentar native Word pada salinan bila aman, serta penjagaan field dinamis.
- Quilo: `protected_tokens_unchanged` terpisah dari `semantic_validity=NOT_ASSESSED`; larang greenlight penyuntingan substantif arbitrer, termasuk penghapusan negasi dan perubahan modalitas.
- Dokumentasi: SKILL.md, panduan F3, kontrak F3, roadmap, migrasi ORIGO, contoh sintetis dan laporan gerbang F4 diperbarui.
- Pengujian: 151/151 suite F3 lulus, 14/14 skenario adversarial lulus, 7/7 tes spesifikasi ORIGO dari addendum lulus, DOCX ORIGO dan Huxley dirender serta diperiksa. Tes native aplikasi AI dan validasi semantik ilmiah masih belum dijalankan.
- Tidak ada perubahan GitHub atau rilis publik.
