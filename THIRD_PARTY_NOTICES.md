English | [Bahasa Indonesia](THIRD_PARTY_NOTICES.id.md)

<!-- section: scope -->
# Third-party notices

The root LICENSE covers original EPISTARIUM work. It does not relicense dependencies, upstream material, or research inputs.
Dependencies are downloaded separately. The EPISTARIUM wheel does not bundle their native libraries or wheels.
See [licensing](docs/en/LICENSING.md) and [the current report](reports/v0.7.1/LICENSING_RESOLUTION.md).
This notice is a source inventory, not a complete approval of every distribution pattern.

<!-- section: simpleenglish -->
## SimpleEnglish

English guidance adapts [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish), Plain mode, version 2.1.1.
Copyright (c) 2026 AminBlg. MIT. Preserve [its complete license](third_party/SimpleEnglish/LICENSE).
The source record and upstream blob hashes remain in [SOURCE.json](third_party/SimpleEnglish/SOURCE.json).
The adaptation keeps research terms, quotations, source tokens, and uncertainty intact. No ASD-STE100 certification is claimed.

<!-- section: pdf -->
## PDF backend notices

The ordinary runtime requires [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) and [pypdf](https://github.com/py-pdf/pypdf). pypdfium2 declares Apache-2.0 OR BSD-3-Clause for its binding, PDFium has a BSD-style license, and the PDFium binary has component licenses. The tested Linux wheel `pypdfium2 5.14.0` carries `LICENSES/` and 15 entries in `data/linux_x64/BUILD_LICENSES/`. The installed `pypdf 6.21.4` wheel declares BSD-3-Clause and includes a LICENSE file. The exact wheel must be reviewed for each OS and architecture before repackaging it. See [licensing resolution](reports/v0.7.1/LICENSING_RESOLUTION.md).

PyMuPDF is used only by inherited development test fixtures in the optional test extra. Those tests and the test environment must respect its AGPL/commercial terms. No PyMuPDF runtime module is required or bundled in the EPISTARIUM wheel.

<!-- section: inventory -->
## Installed dependency inventory

| Distribution | Observed version | Declared license | Role |
|---|---|---|---|
| attrs | 26.1.0 | MIT | runtime |
| build | 1.6.1 | MIT | test-build-environment |
| certifi | 2026.10.23 | MPL-2.0 | runtime |
| charset-normalizer | 3.5.2 | MIT | runtime |
| defusedxml | 0.7.1 | PSFL | runtime |
| et_xmlfile | 2.0.0 | MIT | runtime |
| idna | 3.20 | BSD-3-Clause | runtime |
| iniconfig | 2.3.1 | MIT | test-build-environment |
| jsonschema | 4.26.0 | MIT | runtime |
| jsonschema-specifications | 2025.9.1 | MIT | runtime |
| lxml | 6.1.3 | BSD-3-Clause | runtime |
| openpyxl | 3.1.5 | MIT | runtime |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | test-build-environment |
| pillow | 13.0.0 | MIT-CMU | test-build-environment |
| pip | 26.3 | MIT | test-build-environment |
| pluggy | 1.7.0 | MIT | test-build-environment |
| Pygments | 2.21.0 | BSD-2-Clause | test-build-environment |
| pymupdf | 1.28.2 | AGPL-3.0 or commercial | test environment only |
| pypdfium2 | 5.14.0 | Apache-2.0 OR BSD-3-Clause plus PDFium component terms | runtime |
| pypdf | 6.21.4 | BSD-3-Clause | runtime |
| pyproject_hooks | 1.3.3 | MIT | test-build-environment |
| pytest | 9.2.0 | MIT | test-build-environment |
| python-docx | 1.2.0 | MIT | runtime |
| PyYAML | 6.0.3 | MIT | test-build-environment |
| referencing | 0.37.0 | MIT | runtime |
| reportlab | 5.1.0 | BSD license (see license.txt for details), Copyright (c) 2000-2025, ReportLab Inc. | test-build-environment |
| requests | 2.34.2 | Apache-2.0 | runtime |
| rpds-py | 2026.9.1 | MIT | runtime |
| setuptools | 84.2.1 | MIT | test-build-environment |
| typing_extensions | 4.16.0 | PSF-2.0 | runtime |
| urllib3 | 2.8.0 | MIT | runtime |
| wheel | 0.48.0 | MIT | test-build-environment |
| tzdata | Windows marker, NOT_RUN | Apache-2.0 plus IANA data notices | Conditional runtime |

These are installed package declarations. Native and vendored components can carry additional terms.
The historical [machine inventory](reports/v0.7.0/DEPENDENCIES.json) records requirements, project URLs, license-file paths, and hashes.
Openpyxl and et_xmlfile have no separate license file listed in their installed wheel metadata here.
Their declared MIT fields are recorded without treating a missing file as a grant or a compatibility verdict.
Certifi's MPL-2.0 terms and lxml's component notices remain distinct. Keep upstream notices when redistributing those packages.
Build/test tools and pip are listed for audit reproducibility. They are not bundled with this project's wheel.

<!-- section: material -->
## Research inputs and design inspiration

Included synthetic PDF/DOCX fixtures were created for regression examples. They are not real studies or licensed journal articles.
The BPS example contains two manually transcribed public numeric values with attribution in docs/F4_EXTERNAL_DISCOVERY.md.
Its shipped rights_confirmed flag is false. Review applicable source terms before enabling it. The project grants no rights to BPS source material.
Private manuscripts, participant data, style presets, and licensed PDFs are excluded from release selection.

The README navigation study used [mattpocock/skills](https://github.com/mattpocock/skills) as a UX reference.
No code, prose, installer, unique illustration, or asset was copied from it. Its README blob hash is in the source-research report.
