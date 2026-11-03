English | [Bahasa Indonesia](SECURITY_AUDIT.id.md)

<!-- section: scope -->
# Security audit

Scope: release-file selection, recognizable secret patterns, installed dependency advisories, and existing evidence-integrity controls.
Date: 2026-11-03. This is a bounded local audit, not a penetration test or a guarantee of safety.
The regression suite has 374 cases, including private-path export, adapter overwrite, XML entity, source identity, and hash controls.
No native AI host permission model or live provider was exercised.

<!-- section: controls -->
## Controls and observed fixes

| Area | Evidence | Result |
|---|---|---|
| Private files | Excluded folders, secret filenames, key suffixes, and generated host state | PASS, tested export selection |
| Recognizable secrets | Selected-file byte scan with redacted findings | PASS, see release-scan.json |
| Synthetic credential URLs | Two exact negative-test URLs, individually reviewed | Retained as synthetic tests |
| Adapter writes | Collision, local edit, traversal, symlink, and temporary-path tests | PASS |
| XML | defusedxml added for RSS and workbook protection | PASS entity rejection tests |
| Evidence files | Source identity, permitted paths, pre/post hashes, annotation reopen | PASS relevant regressions |
| Real numeric example rights | BPS default permission assertion removed | BLOCKED until user confirms applicable rights |
| Doctor machine output | Canonical pymupdf import replaces deprecated fitz import | PASS clean-process EN/ID JSON |

The first byte scan flagged two synthetic URLs. The final scan permits only those exact test strings at their specific files.
It does not exclude whole test folders. An additional real credential is still flagged.
A gitignore rule is not encryption or an authorization boundary. The release selector independently rejects excluded paths.

<!-- section: advisories -->
## Dependency advisory check

pip-audit 2.10.1 checked 30 pinned installed distributions with the PyPI advisory service. Known advisories found: 0.
Command: `python -m pip_audit --disable-pip --no-deps -r reports/v0.7.0/audit-requirements.txt --format json --timeout 15`.
The actual invocation also used --output to retain [vulnerability-audit.json](vulnerability-audit.json). See [the log](vulnerability-audit.log).
The audit ran in a separate tooling environment. Its own dependencies are outside the EPISTARIUM runtime inventory.
The release environment has 31 distributions, including the original project. The advisory scan excludes the unlisted local EPISTARIUM package.
Pip was updated to 26.3 before the scan. The initial baseline used the bundled pip version recorded in its freeze file.

This result describes known advisories for those versions at that time. It does not establish license compatibility, future safety, or source provenance.

<!-- section: limits -->
## Remaining boundaries

PDF, DOCX, and XLSX parsers process untrusted files. Entity blocking does not provide complete archive-bomb, memory, or parser-exploit isolation.
Use a constrained local environment for unknown files. No claim is made that a valid extension establishes safe content.
The byte scan cannot detect every participant identity, secret form, or sensitive meaning inside a document.
Historical reports were retained as supplied provenance. They do not authorize reuse of external research sources.
No user research PDF or private dataset was added. Packaged examples remain identified as synthetic or explicitly attributed metadata.
Live service permissions, native host access, fuzzing, and independent penetration testing remain NOT_RUN.
The licensing blocker remains separate. See [LICENSING_AUDIT](LICENSING_AUDIT.md).
