# EPISTARIUM v0.8.0 | Test Evidence

Environment: Linux container, Python 3.13.5, Node 22, headless Chromium. Code baseline: EPISTARIUM v0.7.1 sorted GitHub source, with v0.8.0 Observatory patch. Latest remote GitHub brand artwork and optimized CI remain protected by the overlay approach.

| Test | Result | Scope |
|---|---|---|
| Python full suite | **399 PASS / 399** | Existing EPISTARIUM and 19 new Observatory tests |
| CLI `observatory --help` | **PASS** | Parser and optional arguments |
| Synthetic Jorhas run | **PASS** | Actual Path Finding, events, manifest, artifacts, approval pause |
| Approval enforcement | **PASS** | Pre-network request, final artifact, rejection and change requests, immutable recorded decisions |
| HTTP/SSE loopback integration | **PASS** | Health, API, token checks, Host/Origin guards, stream update, static assets |
| Persistent status safety | **PASS** | Interrupted active run becomes BLOCKED after server restart |
| JSON schema | **PASS** | Run, event and approval payloads |
| Offline Chromium UI | **PASS** | Ten symbolic personas, EN/ID, dark/light, human approval dialog, no JS page errors |
| JavaScript syntax | **PASS** | Node `--check` |
| Skills | **PASS** | 10 canonical skills and 16 CLI commands |
| Docs | **PASS** | 102 active documents, 31 EN/ID pairs, 565 local links, no broken links |
| SimpleEnglish mechanical check | **PASS** | No issues in checked active English documents |
| Bilingual synthetic tutorial | **PASS** | English and Indonesian, 11 scripted commands in each workflow |
| Wheel build | **PASS** | Wheel generated with UI HTML, CSS and JS in package data |
| Native desktop browser connected to localhost | **BLOCKED** | The container browser was blocked by administrator policy. Tested browser UI offline and HTTP/SSE separately. |
| Windows/macOS/Linux GitHub Actions v0.8.0 | **NOT_RUN** | Requires feature-branch push, not yet authorized. |
| Fresh isolated dependency resolution | **NOT_RUN** | This Python environment has pypdf 5.9.0 and pypdfium2 5.8.0. The declared requirements are newer. Core tests passed, but this cannot substitute for a clean install. |

**Provenance:** Screenshots use a real Jorhas Python execution with a **synthetic fixture**. They do not represent a real scientific finding. The UI mock replaces transport calls only for sandboxed browser rendering. HTTP/SSE transport uses separate live loopback integration tests.

**Limitations:** Unit and integration passes do not guarantee platform-wide native activation, document correctness or secure public deployment. A human and CI review are required before main-branch publication.
