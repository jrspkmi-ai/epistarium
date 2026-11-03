English | [Bahasa Indonesia](LICENSING_AUDIT.id.md)

<!-- section: decision -->
# Licensing audit

Decision: HOLD for public distribution. Original-work MIT grant: PASS within its stated scope.
Combined PyMuPDF runtime compliance: BLOCKED. This is a release blocker, not a claim that MIT and AGPL can never coexist.
No commercial agreement or complete corresponding-source distribution plan was supplied.
The owner must choose a reviewed route before public release.

The copyright notice follows the established owner identity, John R.S.P.K.M. Isa, and the supplied project.
The owner explicitly requested MIT for original code. No organization, contributor assignment, or third-party ownership was invented.

<!-- section: evidence -->
## Evidence inspected

The installed environment has 31 distributions, including EPISTARIUM and test/build tools.
Its active runtime closure has 17 external distributions on Linux. Windows tzdata is conditional and NOT_RUN.
[DEPENDENCIES.json](DEPENDENCIES.json) records every installed distribution and available license-file hashes.
The inventory is environment-specific. It does not approve all future versions allowed by pyproject.toml.

Direct runtime terms: PyMuPDF AGPL/commercial, requests Apache-2.0, python-docx/openpyxl/jsonschema MIT, and defusedxml PSF-family terms.
Transitive terms include MIT, BSD, MPL-2.0, and PSF-2.0. Test/build licenses are listed separately in the inventory.
Openpyxl and et_xmlfile lack a separate license file in the observed wheel records. Their MIT metadata and source references remain identified.
No dependency binaries are bundled. Separate downloading does not remove their obligations.

[THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md) retains SimpleEnglish's independent MIT notice and source hashes.

<!-- section: pdf -->
## PyMuPDF mitigation

The code imports PyMuPDF in-process in Retho, Domares, and Vanlan. Required dependency status is retained and disclosed.
The tested bound >=1.28.2,<2 avoids the 2.x layout/ONNX chain observed during baseline installation.
The bound does not establish a permissive license. Vanlan's page, coordinate, highlight, hash, and reopen checks remain intact.

An optional extra does not establish the legal boundary. A command-line subprocess alone also needs an assessed separation argument.
No such separation is claimed here. No PDF backend was replaced or renamed to conceal its license.

| Alternative | Evidence needed | Status |
|---|---|---|
| AGPL-compliant combined runtime | Reviewed corresponding source, notices, recipient rights, and network distribution plan | BLOCKED |
| Artifex commercial terms | Valid agreement covering use and redistribution | NOT_RUN |
| pypdfium2 plus pypdf | Implement equivalent behavior and retain all PDFium component notices | NOT_RUN |
| Separately scoped instructions-only package | Review real functional separation and distribution boundaries | NOT_RUN |

A replacement needs page labels, rotations, Unicode, repeated anchors, coordinate bounds, highlight placement, unchanged source hashes, and reopen tests.
Its licensing also needs a component audit. The current candidate cannot be described as an evaluated replacement.

<!-- section: sources -->
## Official sources checked on 2026-11-03

[MIT text](https://opensource.org/license/mit) · [PyMuPDF licensing](https://pymupdf.io/licensing) · [Artifex licensing](https://artifex.com/licensing)

[PyMuPDF COPYING](https://github.com/pymupdf/PyMuPDF/blob/main/COPYING) · [requests LICENSE](https://github.com/psf/requests/blob/main/LICENSE)

[python-docx LICENSE](https://github.com/python-openxml/python-docx/blob/master/LICENSE) · [jsonschema COPYING](https://github.com/python-jsonschema/jsonschema/blob/main/COPYING)

[openpyxl license declaration](https://openpyxl.readthedocs.io/en/stable/) · [tzdata LICENSE](https://github.com/python/tzdata/blob/master/LICENSE)

[pypdfium2 terms](https://pypdfium2-team.github.io/pypdfium2/readme.html) · [pypdf license](https://pypdf.readthedocs.io/en/stable/meta/faq.html)

The alternative libraries were researched only. They are not installed, integrated, or approved as replacements.
Official documentation and installed metadata support this audit. Legal clearance for a public combined distribution remains unresolved.
