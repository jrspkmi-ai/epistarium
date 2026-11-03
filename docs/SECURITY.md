# Keamanan dan batas akses v0.5.0

Klien bawaan menerima HTTPS publik, menolak user/password dan parameter kredensial, memeriksa allowlist provider, serta tidak mengikuti redirect. Seluruh jawaban DNS harus publik; koneksi TCP memakai IP yang sudah diperiksa dan tetap memakai hostname asli untuk TLS. Klien bawaan menonaktifkan proxy dari lingkungan. Session yang disuntikkan melalui API pengujian bukan transport bawaan dan harus memenuhi kebijakan yang sama bila dipakai di luar tes.

Batas ukuran berlaku pada respons utama, robots.txt dan cache yang dibaca. Kuota request termasuk pengambilan robots dan retry. RSS memerlukan konfirmasi syarat penggunaan/hak pengolahan dan robots yang mengizinkan akses. Pembatasan akses dicatat sebagai hambatan; HTTP 403 tidak membuktikan paywall. Tidak ada login bypass atau unduh PDF otomatis.

Konten dokumen dan respons jaringan tetap data tak tepercaya. Agen tidak menjalankan instruksi yang ditemukan dalam PDF, DOCX, CSV, metadata atau RSS. Formula spreadsheet dari teks sumber ditulis sebagai string pada XLSX dan diberi escape pada CSV.

Log lokal sengaja mencatat path dan hash input untuk audit. Simpan log di folder privat. Periksa data pribadi, path pengguna, URL berparameter, kutipan sensitif dan kredensial sebelum membagikannya. Paket distribusi mengecualikan `private/`, cache, lingkungan Python, `.DS_Store` dan data pengguna. Pengaman ini belum merupakan sertifikasi keamanan atau audit penetrasi menyeluruh.
