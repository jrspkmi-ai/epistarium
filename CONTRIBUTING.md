English | [Bahasa Indonesia](CONTRIBUTING.id.md)

<!-- section: scope -->
# Contributing

EPISTARIUM v0.7.0 is a Release Candidate. Read README.md, AGENTS.md, and the licensing gate before proposing changes.
Original contributions use MIT only when the contributor has authority to grant those rights. Retain third-party notices.
Do not paste licensed articles, private style files, participant identities, credentials, or restricted datasets into an issue or patch.

<!-- section: change -->
## Make a focused change

Keep exactly ten persona entrypoints in .agents/skills. Edit that canonical source rather than a generated host adapter.
Keep English and Indonesian coverage aligned through docs/DOCS_MANIFEST.json. Follow SimpleEnglish Plain for English instructions.
Preserve evidence enums, schema keys, DOI values, quotes, author names, and source uncertainty.
A contract change needs a migration explanation and behavior tests. Distinguish a location match from semantic support.
Use synthetic fixtures that you can redistribute. Keep source provenance and fixture status explicit.

<!-- section: checks -->
## Run checks

Install the test extra in the project venv. Run:

```bash
.venv/bin/python -m pip install -e ".[test]"
.venv/bin/python scripts/verify_skills.py
.venv/bin/python scripts/check_docs.py
.venv/bin/python scripts/check_english.py
.venv/bin/python -m pytest -q
.venv/bin/python -m build
```

On Windows, replace the Python path with .\.venv\Scripts\python.exe.
Report your OS, Python version, exact command, exit code, and PASS/FAIL/BLOCKED/NOT_RUN counts.
A mock provider test does not validate live retrieval. A valid skill file does not validate native host activation.

<!-- section: report -->
## Report a problem

Before a public repository exists, give the owner a redacted report. Use the issue template as a local checklist.
Include the persona, command, expected result, actual result, and a small synthetic reproduction.
Use SECURITY.md for private security reports. Do not upload private research to demonstrate a bug.
A future pull request must state its evidence-contract impact, language coverage, tests, and licensing implications.
Creating an issue, PR, repository, or release is a separate external action. This candidate does not perform it.
