# Kompatibilitas v0.6.0

Paket membawa sepuluh persona dengan panduan ID/EN dalam entrypoint yang sama. Buka root proyek yang memuat .agents/skills/ dan pyproject.toml.

Hasil aktual CLI Linux, pengujian dwi bahasa dan pemasangan wheel tercatat di reports/v0.6.0/RELEASE_GATE.md. Kemampuan CLI tidak membuktikan discovery native setiap host.

Uji pada perangkat Mac/Windows pengguna serta Codex, Antigravity dan OpenCode masih perlu dijalankan tersendiri. Konfigurasi CI tersedia, tetapi keberadaan berkas tersebut bukan hasil eksekusi remote.

Bahasa keluaran dipilih melalui --lang, lingkungan atau konfigurasi. API Python tanpa pilihan bahasa tetap ID. Wheel memuat pustaka/CLI, sedangkan ZIP proyek juga membawa panduan persona.
