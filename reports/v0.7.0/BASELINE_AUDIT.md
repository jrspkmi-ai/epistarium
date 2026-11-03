# v0.6.0 baseline audit before revisions

Recorded 2026-11-03. Source: supplied EPISTARIUM_v0.6.0(1).zip.
SHA-256: `24f4766373cee9a0113c75ed5436057e8f4677cf692e9d4b7e4f14ace02f9bc3`.

Environment: Linux x86_64, Python 3.12.14. Full details: [JSON](BASELINE_AUDIT.json).
The first test attempt was BLOCKED because the base interpreter lacked pytest.
A new virtual environment then installed the unchanged source with its test extra.

| Check | PASS | FAIL | BLOCKED | NOT_RUN | Evidence |
|---|---:|---:|---:|---:|---|
| Regression cases | 341 | 0 | 0 | 0 | baseline-pytest.log |
| Skill definitions | 10 | 0 | 0 | 0 | baseline-skills.json |
| Curated guidance files | 66 | 0 | 0 | 0 | baseline-skills.json |
| English prose files, mechanical check | 24 | 0 | 0 | 0 | baseline-english.json |
| Linux doctor | 1 | 0 | 0 | 0 | baseline-doctor.json |
| Windows/macOS runtime | 0 | 0 | 0 | 2 | Runners unavailable |
| Native AI host activation | 0 | 0 | 0 | 10 | No app session used |

Commands: `python -m pytest -q`, `python scripts/verify_skills.py`,
`python scripts/check_english.py`, `python -m epistarium doctor --lang en`.
The shell wrapper returned zero after the initial failure, so its text is retained as a blocked attempt.
The actual pytest log is the test outcome authority.

## Inspected source

The root has pyproject.toml, the epistarium package, tests, examples, scripts, schemas, docs, reports, and .agents/skills.
Ten bilingual SKILL.md files point to twenty language guides. They define ten personas, not twenty skills.
F1 to F4 schema mirrors match. Canonical JSON/CSV fields and status codes remain shared across languages.
English presentation uses local message catalogs and separate display columns. Source quotations and identifiers stay intact.
SimpleEnglish 2.1.1 has its own MIT notice and recorded source hashes.

The package requires Python 3.11 or later. Runtime dependencies are PyMuPDF, requests, python-docx,
openpyxl, jsonschema, and Windows-only tzdata. Test/build tools are declared separately.
No project LICENSE exists in v0.6.0. PyMuPDF has AGPL/commercial terms that need an explicit release decision.
The unbounded PDF dependency resolved to PyMuPDF 2.1 during this audit.
That install adds layout and ONNX-related dependencies and emits a fitz deprecation warning.
The complete installed versions are in baseline-freeze.txt. They are new observations, not inherited test results.

GitHub Actions already covers three OS names and Python 3.11/3.12. Its remote execution remains NOT_RUN.
Historical reports contain generated demo outputs, old binaries, and archived QA. They are not current test evidence.
The original ZIP and the local baseline commit preserve that history while the release layout is reviewed.

## Privacy and limits

The supplied source uses synthetic examples. No private input was requested or added during the audit.
Existing ignore rules cover private/, userdata/, raw-pdfs/, environment files, keys, and build caches.
A release-file scan and stronger export rules are still required. Absence of a scanner match cannot prove absence of all sensitive data.
No live provider, clinical/legal research result, or native AI integration was assessed by these tests.
A passing text-location test does not establish semantic support for an academic claim.

## Revision priorities

1. Scope MIT to original work and retain dependency notices. Resolve or block the combined PDF distribution claim.
2. Bound the tested PDF dependency and preserve pages, coordinates, highlights, and artifact checks.
3. Add novice OS/platform guides, equivalent language coverage, installation evidence, and release checks.
4. Keep canonical skill paths and evidence contracts. Separate historical generated outputs from current release evidence.

This report was written before source or metadata revisions for v0.7.0.
