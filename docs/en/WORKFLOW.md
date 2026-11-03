# Research workflow

Select a persona by task. Each persona keeps one identity across Indonesian and English. Use the JSON files for handoffs between tools.

| Start with | Required input | Main handoff |
|---|---|---|
| Jorhas | One idea and optional source configuration | Ledgers and draft directions to Ideon |
| Ideon | An idea or research design | ORIGO DOCX and JSON to the researcher and Quilo |
| Liora | A topic | candidates.json to Retho |
| Agresa | Journal records and index evidence | Index report to the researcher |
| Retho | Candidates and a local PDF map | articles.json to Domares |
| Domares | Suitable Retho records | critical_readings.json to Synthia or a reviewer |
| Synthia | Domares readings | Workbook, evidence table, and draft synthesis |
| Vanlan | Claims and PDFs | Claim audit and exact text locations |
| Quilo | Manuscript and optional revision | Editing notes and a diff for human review |
| Huxley | DOCX manuscript | Citation-reference audit to the researcher |

Jorhas Full Research calls a stage only when its input is available. It records the input files, output files, status, and hashes.

Huxley does not export claims to Vanlan automatically. Supply those claims and PDFs explicitly. A reference match alone is not evidence of support.

Use --lang en for English reports. Preserve source language in quotes and metadata. Use the language policy for English JSON input aliases and CSV display files.

```bash
python -m epistarium jorhas-full --idea "Digital communication at university" --config examples/bilingual/full.en.json --lang en --as-of 2026-11-03 --out private/full-en-001
```

The example uses synthetic input and returns PARTIAL. Read each stage status instead of describing the whole run as complete research.
