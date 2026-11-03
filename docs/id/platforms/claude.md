[English](../../en/platforms/claude.md) | Bahasa Indonesia

<!-- section: scope -->
# Claude Code and Claude web

EPISTARIUM v0.7.1 RELEASE_CANDIDATE. Dokumentasi diperiksa pada 2026-11-03.
[Dokumentasi skill resmi](https://code.claude.com/docs/en/skills) dan [situs produk](https://claude.com).
Verifikasi sumber: PASS. Aktivasi EPISTARIUM native: NOT_RUN. Versi aplikasi yang diuji: belum ada.
Versi minimum aplikasi untuk paket lengkap belum ditetapkan. Gunakan versi yang didukung vendor dan verifikasi fitur yang diperlukan.

Claude Code mendokumentasikan discovery native .claude/skills. Buat salinan terkelola dari .agents/skills. Ini adaptor proyek, bukan plugin marketplace.

Panduan tidak memberi perintah pemasangan marketplace/plugin. Kandidat belum memiliki manifest plugin native yang diuji.

<!-- section: setup -->
## 1. Siapkan proyek

Ikuti panduan [Windows](../install/windows.md), [macOS](../install/macos.md), atau [Linux](../install/linux.md) terlebih dahulu.
Baca [lisensi](../LICENSING.md). Simpan sumber privat di luar berkas publik.

Pasang Claude Code dari petunjuk resmi. Buka root proyek lengkap. Jalankan perintah adaptor di bawah dengan venv proyek.

| Cakupan | Lokasi atau batas yang terdokumentasi |
|---|---|
| Proyek | `.claude/skills/ via a generated project adapter` |
| Pengguna/global | `~/.claude/skills/ is documented, but this package does not install there` |
| Jalur EPISTARIUM | Proyek lengkap, .agents/skills kanonis, venv lokal |

Lokasi global hanya informasi rujukan. Kandidat tidak menyalin skill ke direktori pengguna.
Panduan memerlukan proyek lengkap. Menyalin SKILL.md saja menghilangkan runtime Python dan dokumen bukti bersama.

```bash
.venv/bin/python scripts/sync_host_skills.py --host claude --apply
.venv/bin/python scripts/sync_host_skills.py --host claude --check
```

Adaptor menyalin sepuluh skill dan panduannya secara identik. Manifest hash mencatat asal kanonis serta versinya.
Ulangi --apply setelah pembaruan. Skrip menolak berkas tidak terkelola, berkas adaptor yang diubah, dan symlink.
Jika berkas hasil telah disunting, simpan perubahan itu sebelum menghapus atau memperbarui adaptor.
Generator diuji secara lokal. Aktivasi Claude native masih NOT_RUN.

<!-- section: activate -->
## 2. Pilih persona

Pada Claude Code lokal, masukkan /jorhas-master-diving. Gunakan /huxley-citation-auditor untuk audit sitasi atau nama persona persis lainnya.

ID: "Gunakan Jorhas untuk memetakan penggunaan AI oleh mahasiswa. Jalankan contoh sintetis lokal dan tampilkan berkas yang benar-benar dibuat."

EN: "Use Jorhas to map student AI use. Run the local synthetic example and show the files actually created."

Untuk pemeriksaan berkas pertama, minta Ideon memakai examples/bilingual/origo.en.json.
Jorhas mengoordinasikan sembilan spesialis hanya ketika masukan wajib tersedia. Tahap yang belum tersedia tetap NOT_RUN atau BLOCKED.
Baca [sepuluh tutorial](../PERSONA_TUTORIALS.md) untuk memilih tugas.

<!-- section: runtime -->
## 3. Hubungkan runtime Python lokal

Minta agen memakai interpreter venv proyek dari root proyek. Perintah shell ini bukan perintah instalasi khusus host.

```bash
.venv/bin/python -m epistarium doctor --lang en
.venv/bin/python -m epistarium ideon-origo --input examples/bilingual/origo.en.json --lang en --out private/host-map-en-001
```

Pada Windows, ganti .venv/bin/python dengan .\.venv\Scripts\python.exe. Skrip aktivasi tidak diperlukan.
Untuk laporan Indonesia, gunakan --lang id dan masukan Indonesia jika sesuai. Pilih folder keluaran baru.
Doctor memeriksa dependensi dan melaporkan skill_count_at_project_root 10. Hasil itu tidak membuktikan aktivasi host.
Jika host tidak memiliki terminal, jalankan perintah sendiri dan unggah hanya keluaran berizin. Catat eksekusi agen NOT_RUN.

<!-- section: permissions -->
## 4. Tinjau izin

Izinkan agen membaca proyek dan berkas penelitian yang dipilih secara eksplisit. Batasi penulisan pada folder keluaran privat yang ditentukan.
Izinkan eksekusi terminal hanya untuk perintah yang dapat diperiksa. Pemasangan dependensi memerlukan jaringan ke sumber paket yang disetujui.
Contoh penelitian sintetis tidak memerlukan internet. Provider langsung memerlukan otorisasi pengguna terpisah dan opsi jaringan perintah jika didukung.
Skill tidak dapat memberi hak filesystem, terminal, login, atau jaringan. Jangan melewati kebijakan workspace, CAPTCHA, paywall, atau pembatas akses.
Host cloud atau remote memerlukan proyek, dependensi, dan folder keluaran yang dapat ditulis pada lingkungannya sendiri. Venv komputer tidak otomatis berpindah.

<!-- section: verify -->
## 5. Verifikasi eksekusi aktual

Periksa daftar perintah slash dan jejak skill yang dimuat. Jalankan --check pada adaptor. Pastikan doctor serta artefak yang diminta ada pada transkrip tool.

Cocokkan nama keluaran yang disebutkan dengan berkas aktual. Buka status JSON dan salinan DOCX/XLSX/PDF yang ada.
Bedakan discovery, pemuatan skill, eksekusi CLI, validitas artefak, dan penilaian penelitian. PASS pada satu tingkat tidak membuktikan tingkat lain.
Jika tool ditolak, catat BLOCKED beserta tahapnya. Jika tahap belum dicoba, catat NOT_RUN.
Panduan memuat contoh permintaan nyata, tetapi tidak mengklaim keberhasilan host native.

<!-- section: limits -->
## 6. Batas, pembaruan, dan penghapusan

Skill akun Claude web dan Cowork memiliki siklus berbeda dari folder lokal. Sinkronisasi akun tidak memasang Python EPISTARIUM. Thread proyek cloud memiliki batas tambahan.

Perbarui proyek lengkap pada folder terpisah. Buat ulang venv dan jalankan doctor kembali.
Untuk jalur native kanonis, buka ulang atau refresh skill host setelah mengganti proyek. Hindari salinan bernama sama pada lokasi pengguna/global.
Untuk adaptor Claude, ulangi --apply dan --check. Hapus hanya salinan terkelolanya dengan:

```bash
.venv/bin/python scripts/sync_host_skills.py --host claude --remove
```

Gunakan perintah penghapusan itu hanya jika adaptor Claude telah dibuat. Host lain tidak memerlukan penghapusan adaptor hasil generasi.
Tutup workspace lama dan hapus folder hasil ekstraksinya setelah mencadangkan penelitian. Langkah ini tidak menghapus aplikasi AI.
Untuk mode manual, hapus lampiran instruksi/konteks dari chat. Tidak ada instalasi skill global yang perlu dihapus.

Baca [bukti kompatibilitas](../../../reports/v0.7.0/COMPATIBILITY_MATRIX.id.md) dan [penelitian sumber](../../../reports/v0.7.0/SOURCE_RESEARCH.id.md).
Instalasi npx skills yang terverifikasi belum disertakan. Panduan tidak mengasumsikan URL repositori publik.
