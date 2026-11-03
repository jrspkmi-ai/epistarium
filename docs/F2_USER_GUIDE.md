# Panduan F2 untuk peneliti

EPISTARIUM tidak menuntut pengetahuan pemrograman untuk memahami hasil. Pada komputer sendiri, pengguna masih memerlukan Python 3.11+, perintah terminal atau agen yang dapat mengeksekusi skrip.

Jalankan `python -m epistarium doctor` dari root proyek. Pilih folder --out baru pada setiap run.

## 1. Siapkan artikel
Buat folder `private/pdfs` (sudah dikecualikan Git) dan simpan PDF yang boleh Anda baca secara sah. Jangan masukkan file jurnal berbayar atau rekaman narasumber ke repo GitHub.

Contoh `private/library.json`:

```json
{
  "10.1234/contoh-doi": {
    "pdf_path": "private/pdfs/artikel.pdf",
    "version": "publishedVersion",
    "rights_basis": "user_supplied_private"
  }
}
```

Peta DOI disesuaikan dengan metadata Liora. Tautan artikel tidak otomatis sama dengan PDF dan hak menggunakan PDF tidak sama dengan hak menyebarkannya.

## 2. Jalankan Retho

```bash
python -m epistarium retho-retrieve --candidates private/hasil-liora/candidates.json --library private/library.json --out private/retho
```

Baca `private/retho/retrieval_report.md`. Jika tertulis `identity_conflict` **atau** `identity_review_required`, audit PDF terlebih dahulu; jangan memaksa Domares membaca dokumen itu. Jika `abstract_only`, cari full-text legal sebelum lanjut.

## 3. Jalankan Domares

```bash
python -m epistarium domares-read --articles private/retho/articles.json --out private/domares
```

Buka `critical_readings.json`, lihat candidate excerpt beserta halaman PDF. Cocokkan dengan halaman asli. Domares memeriksa ulang hash PDF. Jika berbeda, pembacaan dihentikan dengan `identity_or_integrity_conflict`. Kesalahan konteks/angka tidak diperbaiki otomatis oleh pembaca deterministik.

## 4. Jalankan Synthia

```bash
python -m epistarium synthia-review --readings private/domares/critical_readings.json --out private/synthia
```

Jika ada template Excel asli:

```bash
python -m epistarium synthia-review --readings private/domares/critical_readings.json --template-xlsx private/Template.xlsx --out private/synthia-template
```

Buka `database_literatur.xlsx` jika tersedia. `Audit F2` memuat cuplikan kandidat serta nomor halaman; periksa semuanya sebelum mengutip. Nilai metadata yang menyerupai rumus harus tetap menjadi teks aman dalam XLSX. `database_literatur.csv` dan `sintesis_sementara.md` tetap tersedia tanpa modul Excel.

## 5. Prosedur pemeriksaan ilmiah
- Bandingkan kutipan kandidat dengan PDF dalam konteks paragraf.
- Pisahkan metode, jumlah sampel, dan satuan analisis, jangan menyamakan sampel dengan unit paparan/komentar.
- Isi kolom yang belum dapat diekstraksi secara manual berdasarkan sumber.
- Susun tema dan research gap setelah penilaian hasil studi, kualitas metode, serta jangkauan pencarian.
- Gunakan Vanlan untuk memeriksa klaim yang akan muncul dalam naskah. Status audit yang belum terverifikasi tidak boleh otomatis dinaikkan.

## Batas dukungan platform
Modul adalah Python CLI bersama instruksi `SKILL.md`, dapat dijalankan oleh agen/IDE yang memiliki akses baca/tulis berkas dan eksekusi Python. Kompatibilitas native OpenCode, Antigravity, Codex, ChatGPT, Claude, Gemini dan platform lainnya masih memerlukan tes lingkungan masing-masing.

## Penanganan masalah
- `dependency_not_available`: jalankan doctor dan perbaiki instalasi dependensi, termasuk openpyxl; CSV/JSON tetap tersedia jika telah berhasil dibuat.
- `pdf_needs_ocr`: PDF berupa gambar/scan; pilih OCR secara terpisah setelah memeriksa izin dan sensitivitas datanya.
- `identity_conflict`: PDF/DOI berbeda; hentikan proses dan periksa file yang dipakai.
- `not_read`: hanya metadata/abstrak atau PDF gagal dibuka. Jangan isi temuan dari abstrak.

## Kebijakan unduh daring (V0.2.1)
Parameter `--download` masih dikenali agar panggilan lama tidak langsung rusak, tetapi **tidak akan mengunduh berkas**. Jika perlu artikel daring, buka tautan melalui browser/akses institusi, periksa versi dan izin lalu simpan secara lokal. `oa_candidates` hanya petunjuk lokasi.

## Penjelasan `machine_fulltext_extracted`
Status ini berarti teks PDF dapat diekstraksi dan hash sesuai; **tidak** membuktikan temuan, teori, sampel atau metode sudah dianalisis dengan benar. Lakukan adjudikasi manusia atas passage sebelum menggunakannya dalam proposal atau Bab II.

## Tambahan V0.2.2: workbook review manusia dan akses penerbit
- Ketika template Excel sudah memuat artikel yang sama, Synthia **tidak menambahkan artikel ganda**. Kandidat lokasi ditambahkan ke sheet `Audit F2` sesuai hasil run dan menyimpan keterangan penggabungan di `template_merge_audit.json`. Jangan menganggap kandidat tersebut menggantikan hasil telaah manusia.
- Contoh perintah memeriksa overlap halaman dengan review manusia (file tetap di komputer privat):

```bash
python -m epistarium f2-gold-evaluate --readings private/hasil-domares/critical_readings.json --template-xlsx private/Template\ Literatur\ Review\ V1.xlsx --out private/evaluasi
```

- Untuk pencatatan akses artikel, `retho-retrieve` dapat menerima `--publisher-observations private/penerbit.json`. File berisi DOI sebagai kunci dan `access_state`, `source_url`, `observed_at`, `observation_source`. Catatan ini tidak melakukan login, tidak mengunduh PDF dan tidak mengesahkan lisensi.
- Penggunaan browser atau API berbeda antar platform. Uji native pada OpenCode, Antigravity, Codex, ChatGPT, Claude, Gemini belum menjadi klaim rilis ini.
