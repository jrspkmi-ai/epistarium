[English](THIRD_PARTY_NOTICES.md) | Bahasa Indonesia

<!-- section: scope -->
# Pemberitahuan pihak ketiga

LICENSE pada root mencakup karya orisinal EPISTARIUM. Lisensi tidak menggantikan lisensi dependensi, materi upstream, atau masukan penelitian.
Dependensi diunduh secara terpisah. Wheel EPISTARIUM tidak membundel pustaka native atau wheel dependensi tersebut.
Baca [lisensi](docs/id/LICENSING.md) dan [audit](reports/v0.7.0/LICENSING_AUDIT.id.md).
Pemberitahuan ini merupakan inventaris sumber, bukan persetujuan lengkap atas setiap pola distribusi.

<!-- section: simpleenglish -->
## SimpleEnglish

Panduan Inggris mengadaptasi [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish), mode Plain versi 2.1.1.
Copyright (c) 2026 AminBlg. MIT. Pertahankan [lisensi lengkapnya](third_party/SimpleEnglish/LICENSE).
Rekaman sumber dan hash blob upstream tetap ada dalam [SOURCE.json](third_party/SimpleEnglish/SOURCE.json).
Adaptasi mempertahankan istilah penelitian, kutipan, token sumber, dan ketidakpastian. Tidak ada klaim sertifikasi ASD-STE100.

<!-- section: pdf -->
## Pemberitahuan backend PDF

Runtime biasa memerlukan [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) dan [pypdf](https://github.com/py-pdf/pypdf). Binding pypdfium2 menyatakan Apache-2.0 OR BSD-3-Clause, PDFium memakai lisensi bergaya BSD, dan binari PDFium memuat lisensi komponen. Wheel Linux `pypdfium2 5.14.0` yang diuji memiliki `LICENSES/` serta 15 berkas pada `data/linux_x64/BUILD_LICENSES/`. Wheel `pypdf 6.21.4` yang terpasang menyatakan BSD-3-Clause dan memuat LICENSE. Periksa wheel yang tepat untuk setiap OS serta arsitektur sebelum mengemas ulang. Baca [penyelesaian lisensi](reports/v0.7.1/LICENSING_RESOLUTION.md).

PyMuPDF hanya dipakai oleh fixture tes pengembangan warisan pada extra tes opsional. Tes dan lingkungan itu tetap tunduk pada ketentuan AGPL/komersialnya. Modul runtime PyMuPDF tidak diperlukan dan tidak dibundel dalam wheel EPISTARIUM.

<!-- section: inventory -->
## Inventaris dependensi terpasang

| Distribusi | Versi teramati | Lisensi yang dinyatakan | Peran |
|---|---|---|---|
| attrs | 26.1.0 | MIT | runtime |
| build | 1.6.1 | MIT | test-build-environment |
| certifi | 2026.10.23 | MPL-2.0 | runtime |
| charset-normalizer | 3.5.2 | MIT | runtime |
| defusedxml | 0.7.1 | PSFL | runtime |
| et_xmlfile | 2.0.0 | MIT | runtime |
| idna | 3.20 | BSD-3-Clause | runtime |
| iniconfig | 2.3.1 | MIT | test-build-environment |
| jsonschema | 4.26.0 | MIT | runtime |
| jsonschema-specifications | 2025.9.1 | MIT | runtime |
| lxml | 6.1.3 | BSD-3-Clause | runtime |
| openpyxl | 3.1.5 | MIT | runtime |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | test-build-environment |
| pillow | 13.0.0 | MIT-CMU | test-build-environment |
| pip | 26.3 | MIT | test-build-environment |
| pluggy | 1.7.0 | MIT | test-build-environment |
| Pygments | 2.21.0 | BSD-2-Clause | test-build-environment |
| pymupdf | 1.28.2 | AGPL-3.0 or commercial | test environment only |
| pypdfium2 | 5.14.0 | Apache-2.0 OR BSD-3-Clause plus PDFium component terms | runtime |
| pypdf | 6.21.4 | BSD-3-Clause | runtime |
| pyproject_hooks | 1.3.3 | MIT | test-build-environment |
| pytest | 9.2.0 | MIT | test-build-environment |
| python-docx | 1.2.0 | MIT | runtime |
| PyYAML | 6.0.3 | MIT | test-build-environment |
| referencing | 0.37.0 | MIT | runtime |
| reportlab | 5.1.0 | BSD license (see license.txt for details), Copyright (c) 2000-2025, ReportLab Inc. | test-build-environment |
| requests | 2.34.2 | Apache-2.0 | runtime |
| rpds-py | 2026.9.1 | MIT | runtime |
| setuptools | 84.2.1 | MIT | test-build-environment |
| typing_extensions | 4.16.0 | PSF-2.0 | runtime |
| urllib3 | 2.8.0 | MIT | runtime |
| wheel | 0.48.0 | MIT | test-build-environment |
| tzdata | Marker Windows, NOT_RUN | Apache-2.0 serta pemberitahuan data IANA | Runtime kondisional |

Tabel mencatat pernyataan paket terpasang. Komponen native dan vendored dapat memiliki ketentuan tambahan.
[Inventaris mesin](reports/v0.7.0/DEPENDENCIES.json) mencatat requirements, URL proyek, jalur berkas lisensi, dan hash.
Metadata wheel openpyxl serta et_xmlfile yang terpasang di sini tidak mencantumkan berkas lisensi terpisah.
Field MIT yang dinyatakan dicatat tanpa menganggap ketiadaan berkas sebagai pemberian hak atau putusan kompatibilitas.
Ketentuan MPL-2.0 certifi dan pemberitahuan komponen lxml tetap terpisah. Pertahankan pemberitahuan upstream ketika mendistribusikan paket tersebut.
Perangkat build/tes dan pip dicatat untuk reproduksi audit. Paket tersebut tidak dibundel dalam wheel proyek.

<!-- section: material -->
## Masukan penelitian dan acuan desain

Fixture PDF/DOCX sintetis dalam paket dibuat untuk contoh regresi. Fixture bukan studi nyata atau artikel jurnal berlisensi.
Contoh BPS memuat dua angka publik yang ditranskripsi manual dengan atribusi dalam docs/F4_EXTERNAL_DISCOVERY.md.
Flag rights_confirmed bawaan bernilai false. Tinjau ketentuan sumber sebelum mengaktifkannya. Proyek tidak memberi hak atas materi sumber BPS.
Naskah privat, data partisipan, preset gaya, dan PDF berlisensi dikecualikan dari pemilihan rilis.

Kajian navigasi README memakai [mattpocock/skills](https://github.com/mattpocock/skills) sebagai acuan pengalaman pengguna.
Tidak ada kode, prosa, installer, ilustrasi unik, atau aset yang disalin. Hash blob README tercatat dalam laporan penelitian sumber.
