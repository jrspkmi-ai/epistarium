# EPISTARIUM v0.8.0 | Observatory Security Review

## Scope
The new Observatory is a localhost-only HTTP application for Jorhas execution. It adds **no new runtime dependency**. It does not copy OpenMontage Backlot source, designs, or assets. Its icons and interface are original project work under MIT.

## Examined safeguards
- `ThreadingHTTPServer` binds to `127.0.0.1` and rejects non-loopback Host/Origin headers.
- Non-read-only API requests require JSON, a valid session token, and a bounded request body.
- Browser-to-server HTTP requests use a same-origin session token; SSE endpoints use a token query because native `EventSource` lacks custom request headers.
- Static responses include no-store/no-cache where applicable, `nosniff`, CSP, and frame protection.
- Artifact preview is text only, with an allowlist for `.md`, `.txt`, `.json`, `.csv`, 150 kB source limits, and no rendered source HTML.
- Run IDs use random 128-bit identifiers and a strict regular expression. Path traversal and symlinked artifact paths are refused.
- The root runs folder uses restrictive directory permissions where the OS supports them. Private output stays outside the repository by default.
- Human approval is persisted before a run can access external adapters or mark a final run package as locally authorized.
- A restart marks interrupted active runs `BLOCKED` rather than pretending the work continues.

## Remaining risk and limits
- Local user processes with the same OS privileges can potentially read localhost traffic, browser context, or private run files.
- Token exposure through local history/process inspection, browser extensions, or crash logs is outside the localhost threat model.
- No TLS, remote deployment, multi-user roles, public access, or network proxy is supported.
- Input archives and untrusted scientific content still need the existing core processing and human evidence review. This is not a penetration test.
- The `APPROVE` decision authorizes local artifact release and does not approve content for GitHub or promote sources to verified.
- Real browser-to-loopback end-to-end smoke could not be tested in this sandbox because browser navigation to localhost was blocked. An offline UI rendering test with real synthetic Jorhas artifacts passed.
- Unrestricted Chrome/Safari/Firefox across macOS, Windows and Linux require manual verification in their respective environments.

## Decision
For a local single-user feature branch: **GO_BERSYARAT**. For main/public v0.8.0 release: **HOLD** until CI and live desktop browser tests pass.
