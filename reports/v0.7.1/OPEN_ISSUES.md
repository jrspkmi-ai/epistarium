# Remaining issues and options

1. Native Windows/macOS and Python 3.11/3.14 are NOT_RUN. Run the prepared GitHub Actions matrix or equivalent isolated hosts before claiming them.
2. PDFium binaries differ by platform. Review each installed wheel's `BUILD_LICENSES`, linkage, and notices before bundling any wheels or native files.
3. Complex columns, custom encodings, ligatures, unusual crops, and rotated annotations need a licensed corpus with human coordinate inspection. Ambiguous anchors remain unhighlighted.
4. Scanned PDFs have no OCR. Add an explicit rights-aware OCR workflow later; keep current verification status pending.
5. Inherited tests use PyMuPDF as a development dependency. Rewrite fixtures with reportlab/pypdf to remove it from the test extra.
6. AI host activation is NOT_RUN. Test each native host separately and report the exact host version.
