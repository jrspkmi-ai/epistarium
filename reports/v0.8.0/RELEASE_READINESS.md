# EPISTARIUM v0.8.0 | Release Readiness

**Version:** 0.8.0, Release Candidate. **Decision:** GO_BERSYARAT for a review-only GitHub feature branch. HOLD for merging into main or creating a public release until cross-OS CI and live browser tests are completed.

## Implemented
- Original, compact Backlot-inspired four-column dashboard without Backlot code.
- Ten distinct 2D persona symbols and canonical names.
- Default English with Indonesian toggle, plus dark/light switch.
- Real per-step event emission from Jorhas and append-only event history.
- Local SSE transport, run history, record counts, bounded artifact previews.
- Blocking online consent and local final-artifact approval with persisted audit.
- Strict separation of execution status, research evidence status, and authorization.
- Local-only server with basic origin, token, path and HTML protections.
- Updated packaging, schemas, docs, tests and release metadata.

## Open release gates
1. Install the declared dependencies on clean Python environments.
2. Run GitHub Actions across Linux, macOS and Windows from a feature branch.
3. Test `--open`, actual localhost updates, approve, reject and request changes in a real browser on those operating systems.
4. Review dependencies and license notices before the release.
5. Inspect `git diff` to ensure the latest GitHub brand and optimized CI workflows are preserved.

Do not merge to `main`, tag, or upload a release before the open gates pass. A PASS on synthetic fixtures does not establish scientific validity.
