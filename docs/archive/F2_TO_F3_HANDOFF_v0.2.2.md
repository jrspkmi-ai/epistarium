# Handoff EPISTARIUM F2 v0.2.2-alpha ke F3

Baseline: F2 v0.2.1-alpha dengan QA tambahan menggunakan enam PDF dan satu workbook hasil pembacaan manusia. Regresi 83 tes lokal lulus. Output nyata pada workbook asli: 6 entri manusia dipertahankan, 0 duplikat ditambahkan, 84 kandidat bukti di sheet Audit F2. Dari 48 perbandingan halaman kandidat dengan lokasi dalam review manusia, 25 memiliki overlap, 9 tidak dan 14 tidak ada kandidat. **Akurasi dan kualitas sintesis semantik BELUM TERUKUR.**

Retho: catatan halaman penerbit tidak membuktikan akses full-text. Pengunduhan otomatis tetap nonaktif. DOI/identitas PDF harus diperiksa sebelum Domares; jika hash berubah, tahan ekstraksi.

Domares: `machine_fulltext_extracted` hanya berarti teks terbaca. Review substansi, analisis metode, angka, dan temuan tetap berada pada pemeriksa manusia. Adaptor `gold_validation` mengukur kesesuaian lokasi, bukan kesesuaian makna.

Synthia: bila workbook sudah berisi artikel, jangan gandakan dan jangan timpa; catat audit kandidat di sheet terpisah. Format 20 kolom tetap. Pelaporan keterbatasan analisis otomatis wajib disertakan.

F3: Ideon, Quilo, Huxley dapat dibangun secara modular dengan semua status kandidat dipertahankan. Dilarang menjadikan cuplikan mesin tanpa validasi sebagai fakta untuk RMC 2.0, kebaruan, argumen disertasi, atau daftar pustaka.

Tindak lanjut terbuka: pembacaan substantif AI yang tervalidasi, deteksi kutipan/tabel yang lebih baik, distribusi legal file PDF, dan tes platform native. GitHub tidak disentuh. Rilis publik HOLD.
