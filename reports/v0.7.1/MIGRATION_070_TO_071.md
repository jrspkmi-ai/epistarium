# Migration from v0.7.0

- Ordinary install changes from PyMuPDF to pypdfium2 and pypdf. Use a fresh virtual environment and `pip install .` from this release.
- Retho, Domares, and Vanlan import the shared `pdf_backend` adapter. JSON/CSV keys, verification states, CLI commands, and input schemas remain unchanged.
- PDF text ordering and rectangle geometry can differ. Rerun affected audits, compare locations with source PDFs, and keep the original v0.7.0 output and hashes as separate provenance.
- Existing `test` extra still installs PyMuPDF for inherited fixture tests. It is outside the ordinary runtime install.
- Printed page and PDF page remain distinct. A blank printed page remains unknown; scans require OCR or manual work.
- Gate changes from full HOLD on the old PyMuPDF runtime to GO_BERSYARAT for the stated new source/wheel package, with scope-specific holds.
