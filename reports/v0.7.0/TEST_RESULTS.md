English | [Bahasa Indonesia](TEST_RESULTS.id.md)

<!-- section: environment -->
# Test results

EPISTARIUM 0.7.0 RELEASE_CANDIDATE, 2026-11-03. Environment: Linux x86_64, glibc 2.39, Python 3.12.14.
Final pytest result: 374/374 PASS, 0 FAIL, 0 skipped. The direct test process exited 0.
The unchanged v0.6.0 baseline separately passed 341/341 cases. Do not add baseline and final counts as one denominator.
Dependency versions are in [DEPENDENCIES.json](DEPENDENCIES.json). Build used setuptools 84.2.1.
Raw machine logs preserve exact commands, return codes, file names, and hashes.

<!-- section: counts -->
## Results by unit

| Check unit | PASS | FAIL | BLOCKED | NOT_RUN | Evidence |
|---|---:|---:|---:|---:|---|
| Final regression cases | 374 | 0 | 0 | 0 | pytest.xml / pytest.log |
| Canonical persona definitions | 10 | 0 | 0 | 0 | skill-checks.json |
| Schema mirrors | 9 | 0 | 0 | 0 | contract-checks.json |
| Tutorial commands, EN + ID | 22 | 0 | 0 | 0 | tutorial-smoke*.json |
| Tutorial artifact reopen/parse checks | 198 | 0 | 0 | 0 | 108 EN + 90 ID, synthetic |
| Wheel isolated CLI commands | 5 | 0 | 0 | 0 | wheel-smoke.json |
| ZIP isolated CLI commands | 5 | 0 | 0 | 0 | zip-install-smoke.json |
| ORIGO rendered pages | 7 | 0 | 0 | 0 | layout-checks.json, two samples |
| Local Markdown links | 538 | 0 | 0 | 0 | doc-checks.json |
| Paired document editions | 30 | 0 | 0 | 0 | Section parity, not translation certification |
| English static prose files | 52 | 0 | 0 | 0 | english-checks.json, mechanical scope |
| Official host source review | 9 | 0 | 1 | 0 | Windsurf redirect content inaccessible |
| Native host activation | 0 | 0 | 0 | 10 | No app instance exercised |
| Remote CI matrix jobs | 0 | 0 | 0 | 9 | Three OS labels × three Python versions |
| Combined PDF licensing plan | 0 | 0 | 1 | 0 | Public release blocker |

Rows use different units and scopes. Do not sum their denominators or equate an execution PASS with scientific verification.
Final documentation counts are also recorded in doc-checks.json and english-checks.json.

<!-- section: execution -->
## Commands and installation evidence

The project venv ran doctor in EN/ID, verify_skills.py, check_docs.py, check_english.py, pytest, audit_dependencies.py, and package_release.py.
The exact regression command was `python -m pytest -q --junitxml=reports/v0.7.0/pytest.xml`.
The final wheel command was `python -m build --wheel --no-isolation`. The earlier full build also created an sdist.
Only the current wheel is selected for the ZIP. Old wheel and generated build directories are excluded.

The synthetic tutorial runner executed eleven ordered commands per language. Expected Path Finding and Full Research code 3 counts as a passed expectation.
It reopened or parsed every generated artifact. Neither that check nor a valid manifest assesses scientific meaning.

Wheel checks used a separate venv and non-editable installation. ZIP checks extracted a packaged candidate and created another fresh venv.
Both used isolated Python import mode to prevent the source directory from masking the installed package.
Five CLI commands passed for each installation. Doctor stdout parses as JSON in both languages and finds ten skills at the project root.
[Archive checks](archive-install-checks.json) cover the install-test candidate. Final packaging verifies every payload hash again.
The final ZIP can differ in reports and documentation, but its runtime source signature must match zip-install-smoke.json.

<!-- section: findings -->
## Findings fixed during validation

The beginner forward run exposed dictionary keys used as printed-page values in Domares. The fix reads values explicitly and preserves unknown pages as null.
Four EN/ID regression cases now check known and absent printed pages through Domares, Synthia JSON, and the workbook.
The long ORIGO example also reached the footer. Revised margins and footer spacing passed seven rendered-page checks across two language samples.
The original forward artifacts were retained. Their older defects are not presented as current results.

A clean ZIP-process check then exposed a deprecated fitz import warning before doctor JSON.
Runtime imports now use pymupdf. Two fresh-process language tests prevent this regression. The rebuilt ZIP and wheel pass their checks.
The first secret scan's two hits were synthetic negative-test URLs. Exact reviewed exceptions preserve those tests without ignoring additional matches.

Forward-use evidence is in forward-use/. These are manual local workflows, not native app activation certification.
No live provider, empirical finding, model reasoning score, or semantic-support accuracy was established.
A 20-column matrix or exact text match remains a research aid that requires human review.
