# Kebijakan bahasa v0.6.0

[English](en/LANGUAGE.md) | Bahasa Indonesia

EPISTARIUM tetap memiliki satu implementasi dan sepuluh persona. Setiap SKILL.md mengarahkan agen ke panduan ID atau EN yang sesuai permintaan pengguna.

Gunakan --lang id atau --lang en sebelum atau sesudah subperintah. Urutan pilihan adalah flag eksplisit, EPISTARIUM_LANG, field language pada konfigurasi, lalu locale sistem. Mode auto memakai ID untuk locale Indonesia dan EN untuk locale lain.

API Python menerima lang='id' atau lang='en' pada fungsi masuk penelitian. Tanpa argumen atau konteks bahasa, API tetap memakai ID untuk kompatibilitas. Konteks bahasa dipulihkan setelah pemanggilan selesai.

Pesan CLI, laporan, prosa ORIGO, 21 pertanyaan dan workbook baru mengikuti bahasa pilihan. JSON dan CSV utama mempertahankan kunci, nama berkas serta kode status yang sudah menjadi kontrak.

Mode EN juga membuat *_display.csv dengan label kolom Inggris. Gunakan berkas utama untuk pertukaran data antarmodul. Berkas display tidak menjadi kontrak impor baru.

Kutipan, judul sumber, nama, angka, DOI dan bahan sumber tidak diterjemahkan otomatis. Header dan isian template pengguna dipertahankan. Data asli yang berbahasa Indonesia tetap bisa muncul dalam laporan Inggris dengan konteks yang menjelaskan asalnya.

Input ORIGO dapat memakai alias Inggris seperti idea, phenomenon, theory, paradigm, method, research_question dan data_access. Tabel lengkap terdapat pada panduan English. Jika alias dan kunci utama berbeda isi, program menolak input.

Pilihan --lang tidak memilih bahasa naskah Quilo. Gunakan --preset academic-en untuk naskah Inggris. Preset tersebut menandai isu untuk tinjauan manusia dan tidak menulis ulang teks otomatis.

Prosa Inggris mengikuti SimpleEnglish Plain versi 2.1.1. Istilah ilmiah, tingkat kepastian dan arti bukti dipertahankan. Dokumen historis tetap memakai bahasa aslinya.
