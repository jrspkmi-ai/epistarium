English | [Bahasa Indonesia](../id/LICENSING.md)

<!-- section: scope -->
# Licensing

MIT covers original EPISTARIUM code, instructions, and documentation. See the root [LICENSE](../../LICENSE).
Copyright: 2026 John R.S.P.K.M. Isa. The notice follows the project owner's supplied work and explicit MIT instruction.
No corporate rights holder was invented. Any outside contribution still needs valid permission from its rights holder.

The Python metadata's MIT expression describes EPISTARIUM's original work. It does not relicense installed dependencies, user sources, or upstream material.
[Third-party notices](../../THIRD_PARTY_NOTICES.md) define those boundaries. The release gate is GO_BERSYARAT for the stated source/wheel scope.

<!-- section: pdf -->
## PDF backend

The runtime uses pypdfium2 5.14.0 for text coordinates and pypdf 6.21.4 for annotations and page labels. Neither requires PyMuPDF. The project wheel and ZIP do not contain PDFium binaries. Pip installs the dependency wheel separately. The installed Linux wheel includes PDFium, component notices, and licenses under its `BUILD_LICENSES` directory. Preserve these notices when you redistribute that wheel. Linux Python 3.12 tests passed. Windows and macOS CI remain NOT_RUN.

PyMuPDF stays in the optional test extra solely for inherited test fixtures. It is not imported by production code and is not required by the ordinary installation. Installing the test extra brings its AGPL/commercial terms into that local development environment. Do not distribute that environment as an MIT-only binary bundle. See [the comparison](../../reports/v0.7.1/PDF_BACKEND_COMPARISON.md).

<!-- section: routes -->
## Distribution decision

| Distribution | Gate | Evidence and limit |
|---|---|---|
| Project source and wheel, runtime dependencies installed separately | GO_BERSYARAT | Local functional tests pass; preserve PDFium component notices if repackaging dependencies. |
| Bundled third-party wheel/native binary | HOLD_TERBATAS | Review exact target wheel and ship its component notices; no binary is bundled here. |
| Legacy PyMuPDF combined runtime | HOLD_TERBATAS | AGPL/commercial plan was not resolved for that distribution. |
| Cross-OS or native AI host claims | NOT_RUN | Do not advertise those as verified. |

The project license is MIT for its original work. The dependency licenses remain separate. See the [historical v0.7.1 licensing report](../../reports/v0.7.1/LICENSING_RESOLUTION.md).

<!-- section: thirdparty -->
## Other material and dependencies

SimpleEnglish Plain 2.1.1 has its own MIT copyright notice. Its attribution and recorded hashes remain in third_party/SimpleEnglish/.
The project's license does not override that notice. No upstream installer, README prose, or illustration from mattpocock/skills was copied.
That repository informed navigation goals only.

Requests uses Apache-2.0. python-docx, openpyxl, and jsonschema state MIT licenses. Transitive packages include other licenses, such as MPL-2.0 and BSD.
Windows tzdata has Apache-2.0 and time-zone data notices. It was not executed on Windows here.
Installed test/build tools are audited separately in [the current licensing report](../../reports/v0.7.1/LICENSING_RESOLUTION.md).
No third-party dependency wheel or native library is bundled in the project ZIP or EPISTARIUM wheel.
Pip obtains dependencies separately. Their obligations still apply.

User manuscripts, licensed PDFs, datasets, and interview materials retain their own rights. Keep them outside public packages.
Synthetic fixtures are marked as training/test material. The legacy BPS numeric transcription is separately attributed and grants no source-content license.
See [notices](../../THIRD_PARTY_NOTICES.md) before reusing any non-original material.
