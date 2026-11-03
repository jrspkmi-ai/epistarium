[English](SECURITY_AUDIT.md) | Bahasa Indonesia

<!-- section: scope -->
# Audit keamanan

Cakupan: pemilihan berkas rilis, pola rahasia yang dapat dikenali, advisori dependensi terpasang, dan kontrol integritas bukti yang tersedia.
Tanggal: 2026-11-03. Audit lokal ini memiliki batas, bukan penetration test atau jaminan keamanan.
Suite regresi memiliki 374 kasus, termasuk ekspor jalur privat, penimpaan adaptor, entitas XML, identitas sumber, dan kontrol hash.
Model izin host AI native maupun provider langsung tidak dijalankan.

<!-- section: controls -->
## Kontrol dan perbaikan yang diamati

| Area | Bukti | Hasil |
|---|---|---|
| Berkas privat | Folder, nama rahasia, akhiran kunci, dan state host hasil generasi dikecualikan | PASS, pemilihan ekspor diuji |
| Rahasia yang dapat dikenali | Pemindaian byte berkas terpilih dengan temuan disamarkan | PASS, baca release-scan.json |
| URL kredensial sintetis | Dua URL tes penolakan yang ditelaah satu per satu | Dipertahankan sebagai tes sintetis |
| Penulisan adaptor | Tes benturan, suntingan lokal, traversal, symlink, dan jalur sementara | PASS |
| XML | defusedxml ditambahkan untuk RSS serta perlindungan workbook | PASS tes penolakan entitas |
| Berkas bukti | Identitas sumber, jalur berizin, hash sebelum/sesudah, dan pembukaan anotasi | PASS regresi terkait |
| Hak contoh angka nyata | Asumsi izin default BPS dihapus | BLOCKED sampai pengguna memastikan hak yang berlaku |
| Keluaran mesin doctor | Impor pymupdf kanonis menggantikan fitz yang deprecated | PASS JSON EN/ID pada proses bersih |

Pemindaian byte pertama menandai dua URL sintetis. Pemindaian final hanya mengizinkan dua string tes persis pada berkas yang ditentukan.
Pengecualian tidak mencakup seluruh folder tes. Kredensial nyata tambahan tetap ditandai.
Aturan gitignore bukan enkripsi atau batas otorisasi. Pemilih rilis menolak jalur yang dikecualikan secara independen.

<!-- section: advisories -->
## Pemeriksaan advisori dependensi

pip-audit 2.10.1 memeriksa 30 distribusi terpasang yang dipin melalui layanan advisori PyPI. Advisori yang dikenal ditemukan: 0.
Perintah: `python -m pip_audit --disable-pip --no-deps -r reports/v0.7.0/audit-requirements.txt --format json --timeout 15`.
Pemanggilan aktual juga memakai --output untuk menyimpan [vulnerability-audit.json](vulnerability-audit.json). Baca [log](vulnerability-audit.log).
Audit berjalan pada lingkungan perangkat terpisah. Dependensi perangkat audit tidak termasuk inventaris runtime EPISTARIUM.
Lingkungan rilis memiliki 31 distribusi, termasuk proyek orisinal. Pemindaian advisori mengecualikan paket EPISTARIUM lokal yang tidak terdaftar.
Pip diperbarui ke 26.3 sebelum pemindaian. Baseline awal memakai versi pip bawaan yang tercatat dalam freeze-nya.

Hasil ini menjelaskan advisori yang dikenal untuk versi tersebut pada saat itu. Hasil tidak menetapkan kompatibilitas lisensi, keamanan mendatang, atau provenance sumber.

<!-- section: limits -->
## Batas yang tersisa

Parser PDF, DOCX, dan XLSX memproses berkas tidak tepercaya. Penolakan entitas belum menyediakan isolasi lengkap terhadap archive bomb, memori, atau eksploitasi parser.
Gunakan lingkungan lokal terbatas untuk berkas tidak dikenal. Ekstensi yang valid tidak membuktikan keamanan konten.
Pemindaian byte tidak dapat mendeteksi setiap identitas partisipan, bentuk rahasia, atau makna sensitif dalam dokumen.
Laporan historis dipertahankan sebagai provenance yang diberikan. Laporan tidak mengizinkan pemakaian ulang sumber penelitian eksternal.
Tidak ada PDF penelitian pengguna atau dataset privat yang ditambahkan. Contoh paket tetap ditandai sintetis atau sebagai metadata beratribusi eksplisit.
Izin layanan langsung, akses host native, fuzzing, dan penetration test independen masih NOT_RUN.
Penghalang lisensi tetap terpisah. Baca [LICENSING_AUDIT](LICENSING_AUDIT.id.md).
