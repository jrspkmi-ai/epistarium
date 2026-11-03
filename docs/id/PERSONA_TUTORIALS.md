[English](../en/PERSONA_TUTORIALS.md) | Bahasa Indonesia

<!-- section: start -->
# Tutorial persona

Contoh berikut menjelaskan permintaan, masukan, dan jenis berkas keluaran. Keluaran bersifat ilustratif kecuali log terkini mencatat perintahnya.
Gunakan fixture sintetis untuk latihan. Jawaban yang lancar belum membuktikan eksekusi.
Pasang melalui panduan OS, lalu ikuti [Penelitian Pertama](FIRST_RESEARCH.md).

<!-- section: jorhas-master-diving -->
## Jorhas: The Path Finder

Petakan fenomena dan tiga arah penelitian.

ID: "Carikan bukti dan tiga alternatif fokus penggunaan AI oleh mahasiswa."

EN: "Find evidence and three possible focuses for student AI use."

Masukan: Satu ide, konfigurasi sumber opsional.

Ilustrasi keluaran: Ledger sumber/data, tiga arah tentatif, RUN_MANIFEST.json.

Status: PARTIAL merupakan hasil yang diharapkan. Data yang belum tersedia tetap NOT_RUN atau belum terverifikasi.

Telaah manusia: Kebaruan, sebab akibat, hak akses, dan kelayakan memerlukan penilaian peneliti.

Gunakan [panduan lengkap](../../.agents/skills/jorhas-master-diving/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.

<!-- section: ideon-topic-brainstormer -->
## Ideon: The Research Architect

Susun peta penelitian ORIGO.

ID: "Susun tiga alternatif rancangan dari ide penelitian saya."

EN: "Build three research designs from my initial idea."

Masukan: JSON ide, bukti opsional, dan peta sebelumnya untuk revisi.

Ilustrasi keluaran: JSON ORIGO dan satu DOCX dua bagian, enam simpul, serta 21 pertanyaan.

Status: CREATED_AND_REOPENED memastikan DOCX dapat dibuka kembali. Status ini tidak memvalidasi rancangan.

Telaah manusia: Periksa paradigma, ontologi, epistemologi, metode, dan batas penelitian.

Gunakan [panduan lengkap](../../.agents/skills/ideon-topic-brainstormer/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.

<!-- section: liora-literature-scout -->
## Liora: The Literature Scout

Temukan metadata dan kandidat literatur.

ID: "Carikan studi lima tahun terakhir tentang komunikasi krisis digital."

EN: "Find studies from the last five years on digital crisis communication."

Masukan: Topik, rentang waktu, dan fixture metadata luring opsional.

Ilustrasi keluaran: candidates.json dan candidates.csv beserta provenance.

Status: Metadata kandidat belum merupakan pembacaan full-text atau verifikasi dukungan klaim.

Telaah manusia: Baca sumber dan periksa relevansi sebelum memasukkan studi.

Gunakan [panduan lengkap](../../.agents/skills/liora-literature-scout/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.

<!-- section: agresa-index-verifier -->
## Agresa: The Index Sentinel

Cocokkan bukti indeks yang diarsipkan.

ID: "Periksa jurnal ini menggunakan rekaman indeks resmi yang saya berikan."

EN: "Check these journals against the official index records I provide."

Masukan: JSON jurnal dan JSON bukti indeks yang diarsipkan.

Ilustrasi keluaran: JSON/CSV audit indeks dan laporan bertanggal bukti.

Status: Indeks yang belum dikonfirmasi tetap belum terverifikasi. Bukti jurnal tidak membuktikan indeks artikel.

Telaah manusia: Periksa rekaman resmi, tanggal, identitas jurnal, dan cakupan artikel.

Gunakan [panduan lengkap](../../.agents/skills/agresa-index-verifier/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.

<!-- section: retho-fulltext-retriever -->
## Retho: The Paper Retriever

Periksa akses dan identitas full-text lokal.

ID: "Periksa PDF berizin untuk kandidat literatur ini."

EN: "Check the permitted PDFs for these literature candidates."

Masukan: Kandidat Liora dan peta PDF lokal dengan informasi hak akses.

Ilustrasi keluaran: articles.json, retrieval_report.md, hash, serta rekaman akses/versi.

Status: Abstrak saja, identitas berbeda, hak belum jelas, dan teks pindai menjadi hasil yang terpisah.

Telaah manusia: Pastikan hak unduh, identitas, dan versi naskah. Unduhan otomatis tetap dinonaktifkan.

Gunakan [panduan lengkap](../../.agents/skills/retho-fulltext-retriever/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.

<!-- section: domares-critical-reader -->
## Domares: The Critical Reader

Temukan kandidat passage dalam full-text.

ID: "Baca artikel berizin ini dan temukan bagian metode serta temuannya."

EN: "Read these permitted articles and locate their method and findings."

Masukan: Rekaman articles.json Retho yang sesuai dan PDF yang dapat diakses.

Ilustrasi keluaran: critical_readings.json dan reading_report.md dengan kandidat halaman PDF.

Status: Kandidat passage belum merupakan penilaian manusia. Pindaian memerlukan OCR terpisah atau pembacaan manual.

Telaah manusia: Baca konteks lengkap dan pastikan setiap interpretasi.

Gunakan [panduan lengkap](../../.agents/skills/domares-critical-reader/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.

<!-- section: synthia-literature-review -->
## Synthia: The Knowledge Weaver

Susun matriks literatur dan sintesis sementara.

ID: "Susun matriks literatur dari hasil pembacaan kritis ini."

EN: "Build a literature matrix from these critical readings."

Masukan: JSON hasil Domares dan templat XLSX milik pengguna yang opsional.

Ilustrasi keluaran: Matriks 20 kolom, audit bukti, XLSX, dan sintesis sementara.

Status: Pembacaan yang belum tersedia tetap belum dinilai. Pembuatan workbook diperiksa terpisah.

Telaah manusia: Pastikan perbandingan studi, teori, dan sintesis sesuai sumber.

Gunakan [panduan lengkap](../../.agents/skills/synthia-literature-review/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.

<!-- section: vanlan-powerlink-verify -->
## Vanlan: The Evidence Guardian

Temukan bukti literal PDF dan catat keputusan penelaah.

ID: "Periksa apakah paragraf saya didukung oleh PDF terlampir."

EN: "Check whether my paragraph is supported by the attached PDFs."

Masukan: JSON klaim, PDF berizin, anchor literal, dan telaah manusia beratribusi yang opsional.

Ilustrasi keluaran: Audit klaim, koordinat halaman, hash sumber, dan salinan PDF beranotasi jika anchor unik.

Status: Kecocokan teks hanya menetapkan lokasi. Dukungan semantik belum dinilai tanpa telaah manusia yang sah.

Telaah manusia: Baca passage sekitarnya. Keputusan manusia memerlukan nama penelaah dan alasan.

Gunakan [panduan lengkap](../../.agents/skills/vanlan-powerlink-verify/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.

<!-- section: quilo-academic-writer -->
## Quilo: The Academic Scribe

Audit prosa dan lindungi token bukti saat revisi.

ID: "Tinjau draf ini dengan menjaga kutipan, angka, sitasi, dan ketidakpastian."

EN: "Review this draft and preserve quotes, numbers, citations, and uncertainty."

Masukan: Naskah TXT/DOCX, revisi eksternal opsional, dan JSON gaya privat.

Ilustrasi keluaran: Catatan editorial, pemeriksaan token bukti, dan laporan perbandingan opsional.

Status: Bahasa laporan terpisah dari preset naskah. semantic_validity tetap NOT_ASSESSED.

Telaah manusia: Tinjau makna, klaim kausal, suara penulis, dan revisi yang ditandai.

Gunakan [panduan lengkap](../../.agents/skills/quilo-academic-writer/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.

<!-- section: huxley-citation-auditor -->
## Huxley: The Citation Cartographer

Cocokkan sitasi dan referensi dalam dua arah.

ID: "Periksa semua sitasi terhadap daftar pustaka dalam naskah ini."

EN: "Check all citations against the references in this manuscript."

Masukan: Naskah DOCX dan fixture metadata kandidat sintetis yang opsional.

Ilustrasi keluaran: Audit sitasi/referensi, entri tanpa pasangan, dan salinan DOCX bertanda yang opsional.

Status: Pasangan referensi tidak memverifikasi klaim. Parser mencakup sebagian format APA nama-tahun.

Telaah manusia: Tinjau nama ambigu, rincian referensi, field dinamis, dan makna sumber.

Gunakan [panduan lengkap](../../.agents/skills/huxley-citation-auditor/references/guide.id.md) untuk perintah dan handoff.
Jika berkas atau izin belum tersedia, catat BLOCKED atau NOT_RUN. Jangan mengarang berkas keluaran.
