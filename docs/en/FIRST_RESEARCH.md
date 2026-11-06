English | [Bahasa Indonesia](../id/FIRST_RESEARCH.md)

<!-- section: purpose -->
# First Research in EPISTARIUM

This tutorial uses synthetic, redistributable examples included in the project. No login, external API, or licensed journal PDF is needed.
The topic is university communication and student AI use. Treat every record and proposed design as training material.

Install with your [Windows](install/windows.md), [macOS](install/macos.md), or [Linux](install/linux.md) guide.
Read the [licensing gate](LICENSING.md). Open the project root and run doctor first.

<!-- section: ask -->
## Ask an agent

ID: "Gunakan Jorhas untuk memetakan bukti penggunaan AI oleh mahasiswa. Jalankan contoh sintetis lokal, lalu jelaskan batasnya."

EN: "Use Jorhas to map evidence about student AI use. Run the local synthetic example and explain its limits."

Ask the agent to read .agents/skills/jorhas-master-diving/SKILL.md and its matching language guide.
If native discovery is unavailable, this is manual instructions mode. It does not install a skill or grant terminal access.
Select a [platform guide](INDEX.md) for native setup. You can also run every command directly.

<!-- section: run -->
## Run the synthetic workflow

Use the commands in this order. All paths are relative to the complete project root.
On Windows, replace .venv/bin/python with .\.venv\Scripts\python.exe. The arguments are the same.

```bash
.venv/bin/python -m epistarium jorhas-pathfind --idea 'Student AI use' --fixture examples/bilingual/pathfinder.en.json --lang en --as-of 2026-11-03 --out private/first-research/path
.venv/bin/python -m epistarium ideon-origo --input examples/bilingual/origo.en.json --lang en --out private/first-research/map
.venv/bin/python -m epistarium liora-search --topic 'University communication' --fixture examples/f4_synthetic/full_crossref.json --as-of 2026-11-03 --lang en --out private/first-research/liora
.venv/bin/python -m epistarium retho-retrieve --candidates private/first-research/liora/candidates.json --library examples/f2_synthetic/library.json --lang en --out private/first-research/retho
.venv/bin/python -m epistarium domares-read --articles private/first-research/retho/articles.json --lang en --out private/first-research/domares
.venv/bin/python -m epistarium synthia-review --readings private/first-research/domares/critical_readings.json --lang en --out private/first-research/synthia
.venv/bin/python -m epistarium agresa-audit --journals examples/journals.json --evidence examples/index_evidence.json --lang en --out private/first-research/agresa
.venv/bin/python -m epistarium vanlan-audit --claims examples/claims.json --pdf-dir examples/pdfs --lang en --out private/first-research/vanlan
.venv/bin/python -m epistarium quilo-audit --text examples/f3_synthetic/draf.txt --lang en --out private/first-research/quilo
.venv/bin/python -m epistarium huxley-audit --docx examples/f3_synthetic/naskah_sintetis.docx --annotate-copy --lang en --out private/first-research/huxley
.venv/bin/python -m epistarium jorhas-full --idea 'University communication' --config examples/bilingual/full.en.json --lang en --as-of 2026-11-03 --out private/first-research/full
```

The first command returns 3/PARTIAL. Continue with the next command after reading that result.
The last command also returns 3/PARTIAL. Do not join these commands with && because partial status is expected.
Intermediate commands return 0 when their output files are created. Read the artifact statuses as well.
For Indonesian reports, change --lang en to --lang id. Use a different private output base when repeating the tutorial.
The manuscript language remains unchanged. Select --preset academic-en only for an English manuscript.

<!-- section: read -->
## Inspect the results

Open private/first-research in your file manager. Each persona has its own folder.
Read the reports and canonical JSON files before opening generated DOCX/XLSX files.
Jorhas lists output hashes in RUN_MANIFEST.json. Full Research lists the actual specialist calls and stage status.

Check the ORIGO DOCX, Synthia workbook, Vanlan annotated copy, and Huxley annotated DOCX.
A file that opens is an artifact check. It is not scientific validation.
Vanlan's example includes a wrong number and a missing PDF. A highlight locates text but cannot approve either claim.
Liora's candidates include synthetic metadata. Agresa's index evidence is also simulated.
Retho keeps missing, scanned, and mismatched sources separate. Domares and Synthia preserve missing evidence.

The [historical demo log](../../reports/v0.7.0/tutorial-smoke.json) records actual exit codes and file checks.
Native agent execution remains separate from this deterministic CLI run.

<!-- section: next -->
## Move to real research

Copy only permitted source files into a new private workspace. Replace synthetic metadata with examined, attributed evidence.
Record dates, source identity, rights, definitions, units, and denominators. Read each source before making an interpretive claim.
Use a new output directory. Never reuse synthetic records as findings.
Human review is required for source relevance, semantics, novelty, methods, and conclusions.
If a source needs login, payment, or unavailable permission, record BLOCKED and stop that access attempt.
See [persona tutorials](PERSONA_TUTORIALS.md) and [workflow handoffs](WORKFLOW.md).
