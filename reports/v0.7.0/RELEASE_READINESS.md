English | [Bahasa Indonesia](RELEASE_READINESS.id.md)

<!-- section: decision -->
# Release readiness

Decision: HOLD for public release. Owner-review candidate: prepared as EPISTARIUM v0.7.0 RELEASE_CANDIDATE.
The technical local checks pass. The combined PyMuPDF licensing plan remains an unresolved release blocker.
The package is not stable v1.0. No publication action was authorized or performed.

<!-- section: evidence -->
## Current evidence

The final regression suite passes 374/374 cases. Ten canonical personas and nine schema mirrors remain.
English and Indonesian use one implementation. The new guides have paired section and link checks.
Three OS guides, ten platform guides, ten persona tutorials, migration notes, and release notes are included.
MIT covers original work. Separate notices identify dependency and SimpleEnglish terms.
The wheel and extracted ZIP pass isolated install checks. The synthetic tutorial passes in both languages.
Read [TEST_RESULTS](TEST_RESULTS.md), [COMPATIBILITY_MATRIX](COMPATIBILITY_MATRIX.md), and [SECURITY_AUDIT](SECURITY_AUDIT.md).

<!-- section: open -->
## Open items before publication

| Item | Status | Required next step |
|---|---|---|
| Combined PDF distribution licensing | BLOCKED | Select and review AGPL compliance, commercial terms, or a tested permissive replacement. |
| Native AI activation | NOT_RUN 10/10 | Run the documented discovery and real task checks in each claimed host. |
| Windows/macOS runtime and remote CI | NOT_RUN | Run the prepared matrix and inspect OS-specific artifacts. |
| Windsurf native setup source | BLOCKED | Recheck current official documentation before asserting a native path. |
| Live providers | NOT_RUN | Use authorized access and evaluate actual provider behavior separately. |
| General document rendering and parser isolation | Limited local samples | Inspect new inputs and use constrained processing for unknown documents. |

The licensing blocker prevents a GO or GO_BERSYARAT recommendation for public distribution now.
Missing native tests also prevent claims of universal compatibility. Documented support is not an executed result.

<!-- section: approval -->
## Owner publication approval

After the blockers are resolved, obtain separate approval for the actual repository, public visibility, source/artifact scope, and release text.
Approval can then cover a specific reviewed publication action. This candidate does not create a repository, push, PR, or GitHub Release.
It does not change visibility or upload public artifacts.
The checksum manifest covers payload files, excluding itself. The outer ZIP hash is verified separately to avoid a self-reference.
Keep the current ZIP, original supplied baseline, and test evidence when reviewing a later candidate.
