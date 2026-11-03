# Migrasi v0.5.0 ke v0.6.0

Ekstrak v0.6.0 ke folder terpisah dan pertahankan hasil lama. Buka root dengan pyproject.toml serta .agents/skills/, lalu pasang versi baru.

Tambahkan --lang id pada skrip lama untuk mempertahankan bahasa presentasi CLI. Tanpa flag, CLI mengikuti prioritas bahasa dan locale sistem. API Python tanpa pilihan bahasa tetap memakai ID.

Data Ledger tetap 48 kolom dan Source Ledger tetap 21 kolom. Kunci JSON, CSV utama, nama berkas dan kode status tidak diganti. Mode EN menambahkan CSV display.

Workbook baru EN memakai heading Inggris. Template lama dengan heading ID tetap dipertahankan ketika digunakan pada run EN. Kedua set header yang dikenal didukung.

Quilo memiliki preset academic-en yang dipilih terpisah dari --lang. Preset menandai isu untuk tinjauan tanpa penulisan ulang otomatis.

Sepuluh persona tetap masing-masing memiliki satu SKILL.md. Panduan guide.id.md dan guide.en.md merupakan rujukan bahasa dalam persona yang sama.

Baca [kebijakan bahasa](LANGUAGE.md) dan [panduan English](en/MIGRATION_0.6.0.md). Hasil historis tidak dihitung sebagai pengujian versi baru.
