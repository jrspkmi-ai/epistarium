# v0.7.1 Release Candidate

- Replace the required PyMuPDF backend with pypdfium2 and pypdf for Retho, Domares, and Vanlan.
- Keep page locations, source hashes, human review states, and annotation reopen checks.
- Add regression cases for multiline text, Unicode, rotation, columns, repeated anchors, scan-only and damaged PDFs.
- Keep PyMuPDF only in the optional test extra for inherited fixtures.
- Split release decisions by distribution form and tested scope.
- Record PDFium component notices and remaining platform tests.
