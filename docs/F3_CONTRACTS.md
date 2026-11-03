# Kontrak Fase III, baseline 0.3.1-alpha

## Ideon/ORIGO
Kontrak default `epistarium.origo.ideon.rfs.v1`. Input JSON minimal `ide_awal` (atau alias legacy `ide`/`topik`), `mode` salah satu QUICK_MAP (default), ELABORATE_21, BLUEPRINT, REVISION. `--previous-map` diperlukan bagi REVISION; output `ideon_origo.json`, `ringkasan_origo.md`, dan DOCX dua bagian. Enam simpul vertikal dan Q01-Q21 wajib ada. `literature_status` tidak boleh menyatakan penelusuran telah dijalankan jika belum. RMC lama hanya lewat `--legacy-rmc`. Seluruh keluaran baru berstatus `DRAFT_PERLU_REVIEW_MANUSIA`.

## Quilo
Input naskah teks dan revisi opsional; output diff, usulan editor, JSON audit. `protected_tokens_unchanged` terpisah dari `semantic_validity=NOT_ASSESSED`. `safe_to_propose` hanya indikator candidate berisiko rendah yang dapat diperiksa, bukan sertifikasi makna.

## Huxley
Input DOCX; output `huxley_audit.json`, `sitasi.csv`, `daftar_pustaka.csv`, `laporan_huxley.md`, `referensi_kandidat_DRAFT.json`, salinan DOCX opsional. Status MATCHED/UNMATCHED_CITATION/UNCITED_REFERENCE/AMBIGUOUS/MANUAL_REVIEW. Anotasi presisi + komentar native Word hanya jika span dan input aman; field dinamis disalin byte-identik. Tidak ada sumber baru yang otomatis dimasukkan ke daftar pustaka final.

## Ke F4
Jorhas harus memanggil masing-masing modul yang benar-benar tersedia, mencatat path artefak, timestamp, versi, outcome dan status. Tidak boleh mempromosikan draft ORIGO, hasil mismatch, atau edit Quilo menjadi temuan empiris final. Semua integrasi live dan kompatibilitas native lintas platform tetap NOT RUN bila belum diuji.
