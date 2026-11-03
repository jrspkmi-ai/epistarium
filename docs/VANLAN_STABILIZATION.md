# Vanlan F1 Stabilization | 3 November 2026

## Status
Versi `0.1.1a1` adalah prototipe internal. Pemutakhiran dibatasi pada Vanlan dan kontrak buktinya. Liora dan Agresa masih dalam kondisi baseline F1 sebelumnya.

## Perubahan
- P01: Angka 2026 pada footer yang berdiri sendiri tidak lagi otomatis dianggap nomor halaman cetak. Penomoran divalidasi berdasarkan penanda eksplisit dan pola antarahalaman.
- P02: Penelusuran PDF dengan DOI sekarang bisa berjalan jika DOI utama dalam PDF teridentifikasi secara unik. Jika lebih dari satu PDF cocok atau DOI bertentangan, proses dihentikan dengan status ambigu. Tidak ada pencarian internet otomatis dalam Vanlan.
- `printed_page_method`, `source_identity_verified`, `source_match_method`, `anchor_text_match_status`, `semantic_support_status` ditambahkan untuk mengurangi ambiguitas audit.
- Multi-anchor lintas halaman didukung. Highlight ganda untuk koordinat yang sama dihilangkan.
- Ligatur Unicode yang setara (`ﬁ`, `ﬂ`, dll.) dapat dicari tanpa memalsukan lokasi koordinat.
- Kecocokan frasa tidak lagi membuat status semantik `terverifikasi` secara otomatis. Setelah pengguna mengimpor penilaian manusia, status semantik mengikuti keputusan itu dengan atribusi yang jelas.
- PDF anotasi diverifikasi ulang menggunakan dua instance dokumen baru. Jika jumlah halaman atau teks hasil ekstraksi berubah, keluaran anotasi dibatalkan.
- Uji regresi lama telah diperbarui sesuai perubahan semantik status. Ini perubahan kontrak keluaran yang harus dipahami oleh modul pemanggil di fase berikutnya.

## Bukti pengujian
- Regresi sintetik: 28 PASS dari 28 tes, `pytest` pada lingkungan Linux dalam sesi pengembangan.
- PDF nyata milik pengguna: enam PDF akademik dengan total 97 halaman, enam klaim parafrasa, dua belas anchor literal berkoordinat yang ditemukan pada halaman kunci jawaban; angka halaman cetak sesuai kunci untuk anchor yang diuji.
- Lima klaim tepat dan satu didukung sebagian merupakan **label penilaian manusia yang diimpor**, bukan prediksi atau evaluasi semantik independen oleh program. Tanpa review, keenamnya berstatus `belum dapat diverifikasi` pada tingkat substansi.
- Seluruh enam PDF anotasi dapat dibuka dan teks ekstraksinya sama per halaman dengan PDF sumber, berdasarkan pemeriksaan setelah menyimpan file.
- PDF Ma & Zheng 2025 memunculkan peringatan objek xref dalam proses MuPDF. Output masih terbaca dan preservasi teks lulus; audit PDF struktur lanjutan tetap direkomendasikan.
- PDF tidak disertakan dalam berkas kode publik karena hak penerbit dan pembatasan penggunaan.

## Fitur belum selesai
- Penilaian substansi/konteks otomatis oleh model yang dapat dibuktikan; pemeriksaan angka, negasi dan perbedaan metode masih membutuhkan peninjau manusia.
- Ekstraksi naskah DOCX dan pemetaan sitasi ke PDF dari daftar pustaka.
- OCR opt-in serta ekstraksi tabel, diagram, dan bahan scan tanpa teks.
- DOI resolver lintas sumber daring dan penelusuran bibliografi otomatis (hubungan dengan Liora/Retho/Huxley belum dibangun).
- Verifikasi koordinat dan penomoran lintas beragam tata letak/OS; pengujian saat ini berbasis 6 PDF nyata dan sejumlah dokumen sintetis.
- P03 Agresa (konflik ISSN) dan P04 Liora (batas tahun empiris) belum diperbaiki, di luar lingkup stabilisasi Vanlan giliran ini.

## Kelayakan
Layak sebagai *baseline internal untuk pengembangan F2 bersyarat*, dengan pembatasan semantik dan integrasi tertulis. Belum layak untuk rilis publik sebagai verifier otomatis yang mengklaim substansi benar. Gerbang GitHub tetap memerlukan izin terpisah.
