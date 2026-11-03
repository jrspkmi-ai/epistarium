[English](COMPATIBILITY_MATRIX.md) | Bahasa Indonesia

<!-- section: scope -->
# Matriks kompatibilitas

Tanggal dokumentasi: 2026-11-03. Versi aplikasi yang diuji: belum ada. Aktivasi native PASS: 0/10, NOT_RUN: 10/10.
Telaah sumber resmi: PASS 9/10, BLOCKED 1/10. Validasi metadata skill tidak membuktikan dukungan aplikasi native.

| Platform | Telaah sumber | Jalur paket | Eksekusi native |
|---|---|---|---|
| [OpenCode](../../docs/id/platforms/opencode.md) | PASS | Skill proyek .agents kanonis | NOT_RUN |
| [Google Antigravity](../../docs/id/platforms/antigravity.md) | PASS | Skill proyek .agents kanonis | NOT_RUN |
| [OpenAI Codex](../../docs/id/platforms/codex.md) | PASS | Skill proyek .agents kanonis | NOT_RUN |
| [ChatGPT](../../docs/id/platforms/chatgpt.md) | PASS | Proyek lengkap manual | NOT_RUN |
| [Claude Code and Claude web](../../docs/id/platforms/claude.md) | PASS | Adaptor proyek terkelola | NOT_RUN |
| [Gemini CLI and Gemini web](../../docs/id/platforms/gemini.md) | PASS | Skill proyek .agents kanonis | NOT_RUN |
| [GitHub Copilot](../../docs/id/platforms/copilot.md) | PASS | Skill proyek .agents kanonis | NOT_RUN |
| [Cursor](../../docs/id/platforms/cursor.md) | PASS | Skill proyek .agents kanonis | NOT_RUN |
| [Windsurf](../../docs/id/platforms/windsurf.md) | BLOCKED | Proyek lengkap manual | NOT_RUN |
| [Amp](../../docs/id/platforms/amp.md) | PASS | Skill proyek .agents kanonis | NOT_RUN |

<!-- section: os -->
## Sistem operasi dan Python

| Lingkungan | Runtime lokal | Eksekusi CI | Catatan |
|---|---|---|---|
| Linux x86_64, glibc 2.39, Python 3.12.14 | PASS | NOT_RUN | Tes kontainer, instalasi bersih, dan artefak CLI |
| Instalasi desktop Ubuntu/Debian | NOT_RUN | NOT_RUN | Petunjuk paket resmi ditelaah |
| Windows 10/11 | NOT_RUN | NOT_RUN | python.exe venv eksplisit tanpa perubahan kebijakan aktivasi |
| macOS Intel | NOT_RUN | NOT_RUN | Jalur Python universal2 didokumentasikan |
| macOS Apple Silicon | NOT_RUN | NOT_RUN | Jalur Python universal2 didokumentasikan |
| Windows ARM, Linux ARM, musl/Alpine | NOT_RUN | NOT_RUN | Tidak ada janji kompatibilitas |

Matriks CI yang disiapkan memiliki 9 job: 3 label OS dikalikan Python 3.11, 3.12, dan 3.14.
Hasil job remote: NOT_RUN 9/9. Repositori tidak dibuat dan workflow tidak dijalankan.
Python >=3.11 merupakan persyaratan metadata. Validasi lokal hanya mencakup 3.12.14.

<!-- section: boundaries -->
## Batas integrasi

ZIP lengkap merupakan distribusi proyek. Wheel saja memasang perangkat Python dan tidak membawa direktori .agents.
Adaptor Claude dibuat secara lokal dan dikecualikan dari ZIP rilis. Pemeriksaan hash terpisah dari aktivasi Claude.
Eksekusi manual ChatGPT Work memerlukan tool pada sesi itu. Unggahan web saja tidak memberi filesystem atau terminal lokal.
Skills akun/Claude web, Gemini web, agen cloud Copilot, dan klien coding lokal memiliki siklus serta lingkungan terpisah.
Tidak ada plugin marketplace, jalur npx skills, atau instalasi persona mandiri global yang divalidasi.

Verifikasi sumber Windsurf berstatus BLOCKED. URL resminya mengarah ke dokumentasi Devin yang tidak dapat diakses.
Panduan memberi instruksi pembacaan berkas manual tanpa klaim jalur native atau versi minimum.
Host tanpa tool terminal dapat menelaah sumber, tetapi eksekusi deterministik harus tetap NOT_RUN.
