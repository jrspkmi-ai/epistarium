[English](CONTRIBUTING.md) | Bahasa Indonesia

<!-- section: scope -->
# Kontribusi

EPISTARIUM v0.7.0 merupakan Release Candidate. Baca README.id.md, AGENTS.md, dan gerbang lisensi sebelum mengusulkan perubahan.
Kontribusi orisinal memakai MIT hanya jika kontributor berwenang memberikan hak tersebut. Pertahankan pemberitahuan pihak ketiga.
Jangan menempelkan artikel berlisensi, berkas gaya privat, identitas partisipan, kredensial, atau dataset terbatas ke isu maupun patch.

<!-- section: change -->
## Buat perubahan terarah

Pertahankan tepat sepuluh entrypoint persona dalam .agents/skills. Sunting sumber kanonis, bukan adaptor host hasil generasi.
Selaraskan cakupan Inggris dan Indonesia melalui docs/DOCS_MANIFEST.json. Ikuti SimpleEnglish Plain untuk instruksi Inggris.
Pertahankan enum bukti, kunci schema, DOI, kutipan, nama penulis, dan ketidakpastian sumber.
Perubahan kontrak memerlukan penjelasan migrasi serta tes perilaku. Bedakan kecocokan lokasi dari dukungan semantik.
Gunakan fixture sintetis yang boleh didistribusikan. Nyatakan provenance sumber dan status fixture secara eksplisit.

<!-- section: checks -->
## Jalankan pemeriksaan

Pasang extra test pada venv proyek. Jalankan:

```bash
.venv/bin/python -m pip install -e ".[test]"
.venv/bin/python scripts/verify_skills.py
.venv/bin/python scripts/check_docs.py
.venv/bin/python scripts/check_english.py
.venv/bin/python -m pytest -q
.venv/bin/python -m build
```

Pada Windows, ganti jalur Python dengan .\.venv\Scripts\python.exe.
Laporkan OS, versi Python, perintah persis, exit code, dan jumlah PASS/FAIL/BLOCKED/NOT_RUN.
Tes provider tiruan tidak memvalidasi pengambilan langsung. Berkas skill yang valid tidak membuktikan aktivasi host native.

<!-- section: report -->
## Laporkan masalah

Sebelum repositori publik tersedia, berikan laporan yang telah disamarkan kepada pemilik. Gunakan templat isu sebagai panduan lokal.
Sertakan persona, perintah, hasil yang diharapkan, hasil aktual, dan reproduksi sintetis kecil.
Gunakan SECURITY.md untuk laporan keamanan privat. Jangan mengunggah penelitian privat untuk memperagakan bug.
Pull request kelak perlu menjelaskan dampak kontrak bukti, cakupan bahasa, tes, dan implikasi lisensi.
Membuat isu, PR, repositori, atau rilis merupakan tindakan eksternal terpisah. Kandidat ini tidak melakukannya.
