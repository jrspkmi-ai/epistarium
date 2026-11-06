# EPISTARIUM v0.9.0 release readiness

Decision: **GO_BERSYARAT for local package review; HOLD for merge and public release** pending cross-OS CI and outstanding integration tests. Release metadata records `PENDING_CROSS_OS_CI`. This package does not authorize publication or push.

The implementation adds correlated run IDs, a workflow plan, scoped agent events, schema and artifact hash checks, and spool replay. Agent reports remain distinct from Python observations. A separate review passphrase protects the approval route, and final decisions record artifact hashes. These checks do not establish research validity or reviewer identity.

Hosts must explicitly send checkpoints. Native OpenCode and Antigravity integrations were not tested, and complete host coverage is not claimed. A live browser UI, macOS, and Windows were not tested in this work. Earlier results are not evidence for this version.

The deterministic workflow runs only stages with available inputs. Preserve `NOT_RUN`. Synthetic tests do not assess scholarly quality. An adversary with full control of the same OS account is outside the local boundary. Use one server per private storage root.

Read `TEST_RESULTS.md`, the EN/ID guides, and the changelog. After owner review, run the CI matrix and native host tests on a separate branch before considering a merge.
