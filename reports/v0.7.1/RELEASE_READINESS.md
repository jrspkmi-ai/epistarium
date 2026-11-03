# Release readiness, v0.7.1

**Decision: GO_BERSYARAT for evaluation of an MIT original-work source/wheel release. Publication is not authorized.**

| Scope | Gate | Evidence / required action |
|---|---|---|
| Production PDF functions on Linux Python 3.12 | GO_BERSYARAT | Full suite and clean ordinary-install smoke must pass. New PDFium/pypdf adapter tested on synthetic corpus. State limits for complex layouts. |
| Bundling native PDFium or dependency wheels | HOLD_TERBATAS | The project package does not bundle them. Check target wheel and ship its component notices if distribution changes. |
| AGPL PyMuPDF development test environment | HOLD_TERBATAS | Optional tests use it; do not market that environment as an MIT-only binary. |
| Core research workflow failure | HOLD_PENUH if regressions occur | No failing tests may be ignored. |
| Native AI-host integration | NOT_RUN | Do not assert host activation. This does not hold the tested Python package. |
| Windows/macOS/Python 3.11/3.14 | NOT_RUN | Nine-job matrix prepared, not triggered. No compatibility claim. |
| Extra features/OCR | Documented limit | OCR not available; scan remains pending human/OCR work. |

The owner's separate approval is needed before any public repository action. See [test results](TEST_RESULTS.md), [backend comparison](PDF_BACKEND_COMPARISON.md), and [licensing](LICENSING_RESOLUTION.md).
