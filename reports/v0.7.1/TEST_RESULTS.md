# v0.7.1 test results

- Linux x86_64, Python 3.12.14: 380 pytest cases PASS, 0 FAIL, 0 SKIP. See `pytest.xml` and `pytest.log`.
- Six added PDF backend tests cover multiline, Unicode accent, rotation, two columns, repeated anchors, printed versus PDF page, scan-only, damaged PDF, original hash, and annotation integrity. These are synthetic fixtures, not proof of parity for all academic PDFs.
- Wheel build PASS. Fresh non-editable ordinary wheel installation and ZIP-extracted wheel installation PASS with `pip check`, isolated import, and bilingual doctor JSON. PyMuPDF was absent from both environments. The final coordinate guard was also rerun in the full suite.
- EN and ID tutorials: see `tutorial-en.json` and `tutorial-id.json` for command and artifact results. These run through the clean wheel installation.
- Documentation local links and paired sections: `docs-check.json`. Mechanical English: `english-check.json`. Ten canonical skills: `skill-check.json`.
- Release scan: `release-scan.json` reports PASS for high-confidence patterns and excluded paths. This is not an exhaustive secret audit.
- Native AI-host activation and remote 9-job CI: NOT_RUN. No Windows/macOS runtime result is asserted.
