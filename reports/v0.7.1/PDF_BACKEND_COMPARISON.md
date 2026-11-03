# PDF backend comparison, v0.7.1

| Behavior | v0.7.0 PyMuPDF | v0.7.1 PDFium plus pypdf | Evidence and limit |
|---|---|---|---|
| Text and page coordinates | PyMuPDF search quads | PDFium character boxes, grouped by visual line | Synthetic line, two-column, rotation, Unicode, and repeated-text tests; no universal equivalence claim. |
| Highlights | PyMuPDF mutation | pypdf Highlight annotations, native PDF coordinates | Reopen, page count, text equality, annotation count, source hash. |
| PDF labels and printed numbers | PDF labels plus visual corroboration | pypdf labels plus PDFium visible footer zones | Existing pagination tests, including different printed and PDF page numbers. |
| Source identity and DOI | First-page evidence | Same Vanlan/Retho logic over new backend | Existing DOI conflict and collision tests. |
| Damaged or scan-only PDF | Reject or ask for OCR | Reject or ask for OCR | Synthetic corrupt and scan fixtures; no OCR claim. |
| Multi-line anchors | Search quads | PDFium phrase search with whitespace normalization; separate rectangles | Two-line synthetic fixture passed; complex typography remains a limit. |
| Scientific interpretation | Human review | Human review | Literal match never implies semantic support. |

The new adapter is `epistarium/pdf_backend.py`. It keeps the old caller contract but translates coordinate systems. PDFium boxes are in the unrotated PDF canvas. Output rectangles are transformed for page rotation. pypdf annotations use the native boxes. Candidate bounds must be inside the visible page. Repeated anchors refuse highlights. No OCR, layout-reading guarantee for arbitrary columns, or full parity across all publisher PDFs is claimed. A future corpus should include licensed real PDFs and manual location checks.
