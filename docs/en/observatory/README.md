<!-- section: start -->
# EPISTARIUM v0.8.0 | Research Observatory (EN)

The Observatory is an **optional local monitor** for actual Jorhas Python runs. It shows the state of ten canonical personas, steps, source/data record counts, artifacts, events, and human approval gates. This is an instrument for supervision, **not an automatic empirical validation service**.

Python 3.11+ is required. Install from the repository root in a virtual environment using the operating system guide: [Windows](../install/windows.md), [macOS](../install/macos.md), [Linux](../install/linux.md). No Node.js, cloud account, React, FastAPI, or paid provider is required by this feature.

With the virtual environment activated:

```bash
python -m epistarium observatory --open
```

The default address is `http://127.0.0.1:4782/`. The `--open` option asks the local operating system to open the browser. If browser launching is blocked, open the printed address manually. Use `--no-browser` for a headless environment. The private store defaults to `~/.epistarium-observatory/`, outside the GitHub project directory. Close the server with Ctrl+C.

To start an **actual Jorhas Path Finding run** with synthetic test data (never present these findings as empirical):

```bash
python -m epistarium observatory --idea "Digital crisis communication" --mode pathfind --fixture examples/f4_synthetic/pathfinder_cases.json --lang en --open
```

For a run based on the supplied research idea without a synthetic fixture:

```bash
python -m epistarium observatory --idea "Consumer complaints in F&B" --mode pathfind --lang en --open
```

If no source adapter or input is configured, the run can legitimately finish with `PARTIAL` or `BLOCKED`. The Observatory never invents sources or verifies claims. The built-in UI can start new **offline** runs only. To supply local file inputs, approved config, or request network access, use the CLI options `--config`, `--fixture`, and `--online` as applicable.

[UI preview, dark mode with synthetic Jorhas records](media/dark_en_synthetic.png). This preview demonstrates rendering. Live network transport was tested separately through local HTTP/SSE integration tests.

<!-- section: monitoring -->
## Live monitoring

The main screen follows the approved **four-column concept: Not run / queued, Running, Needs review, Completed steps**. Each persona uses a role icon, no random human portraits. The header contains the EN/ID selector (default **EN**) and dark/light switch (default **dark**). Preferences persist in the browser. The layout is responsive and reads the same canonical events under both languages.

The server receives progress checkpoints from **real Jorhas functions** through an optional callback. Events are appended to `runs/<run-id>/events.jsonl`. The browser receives SSE notifications and refreshes the corresponding run data. `run.json` records current execution state, while `outputs/<run-id>/` contains the existing Jorhas ledgers and reports.

The nine specialists appear as `NOT_RUN` unless actually invoked. Path Finding ordinarily runs **Jorhas**, not all ten personas. Full Research invokes specialists only when config and material permit. A `SUCCESS` execution means a function completed, not that its claims are proven. `PARTIAL`, `BLOCKED`, `NOT_RUN`, and the evidence status remain visible separately.

Record counts are taken from `SOURCE_LEDGER.json` and `DATA_LEDGER.json`. Unavailable counts show `—`. Artifact preview supports small text/JSON/CSV/Markdown files. The board does not provide a false "accuracy" score, hypothetical ETA, or simulated activity in a real run.

<!-- section: approval -->
## Approval gates

- If `--online` is provided, the run pauses **before external source access**. The user must approve it in the local dashboard. Online requests remain subject to the provider adapter's authorization, rights, and limits.
- After execution, Jorhas pauses before **authorizing the run artifact package**. The user can approve, reject, or request changes. Rejection and change requests require a reason. The `approvals.json` record includes the decision, time, reviewer label, and a manifest hash where available. `release_authorization.json` is written only after explicit final approval.
- Approval is an authorization to proceed or release a package. It does not promote sources to `verified` or authorize publication to GitHub.
- A change request terminates the present run in `NEEDS_CHANGES`. The user can start a new run. Automatic resume/re-execution of individual persona tasks is not yet implemented.

<!-- section: security -->
## Security and data boundaries

The server binds to `127.0.0.1` only and rejects foreign Host/Origin values. State-changing endpoints require a session token in a custom header, and cross-origin responses are not enabled. The session token expires when the server stops. Browser previews are confined to a private run directory, reject symlinks and traversal, and return **text only**, rendered using `textContent` rather than HTML injection. Inputs and paths are not shown in the public activity feed. Keep run folders outside tracked repositories.

**Threat boundary:** A malicious process running under the same local user can potentially inspect localhost traffic or files. This local UI is **not hardened for remote deployment, public port forwarding, or multiple untrusted users**. Do not expose it via a reverse proxy or public tunnel.

<!-- section: limits -->
## Known limits and verification

Local Python regression and loopback HTTP/SSE tests are part of `tests/test_observatory_v080.py`. Visual Chromium testing is optional and is documented by `scripts/observatory_browser_smoke.py`, which requires separate Playwright/Chromium setup. Run `python -m pytest -q` and the repository's GitHub Actions test matrix before publishing a release.

Native browser launch in ChatGPT web/Work, Gemini web, or Claude web is **not** implied. It requires each host's actual filesystem/browser/MCP support. A plugin consisting only of `SKILL.md` cannot itself launch this local process. The Observatory is currently a local Python capability, not a cloud-hosted dashboard. All original Observatory code is MIT under the repository's LICENSE. Prior third-party notices remain applicable.
