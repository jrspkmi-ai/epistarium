# Research Kitchen and Agent Observatory Bridge

The built-in one-command workflow is `jorhas-full`. It runs deterministic Python
stages when their input contracts are satisfied and writes `WORKFLOW_PLAN.json`.
Unmet inputs remain `NOT_RUN`. ORIGO is a draft and is not a full literature
review or an autonomous language-model investigation.

```bash
python -m epistarium jorhas-full --idea "Synthetic research topic" --out private/run-001 --lang en
python -m epistarium observatory --idea "Synthetic research topic" --mode full --open
```

Every Observatory run has a research run ID shared by its Python manifest,
event ledger, workflow plan, and external reports. The Observatory starts with
English and dark mode. Users can change language and theme. Python runtime
checkpoints are labeled `runtime_observed`. External host reports are labeled
`agent_reported` and `SELF_REPORTED`. A host report is not independent proof of
execution or evidence quality. A matching artifact hash establishes that the
local file matched the supplied digest when the event was received.

## Enable actual agent checkpoints

An adapter is provided for hosts that can call shell commands. It does not
instrument OpenCode, Antigravity or any other host automatically. The agent
must emit events only when the specified activity actually happens. Native host
integration and complete host monitoring require separate tests.

The operator can find the run ID in the dashboard and explicitly grant the
host read access to the run's `bridge.token` file. This is a secret, scoped to
one run. Never paste its contents into research text, logs, Git or chat.
Use real local paths in place of the placeholders below:

```bash
python -m epistarium.observatory.agent_adapter \
  --server http://127.0.0.1:4782 --run-id RUN_ID \
  --token-file PRIVATE_ROOT/runs/RUN_ID/bridge.token \
  --spool PRIVATE_SPOOL report --persona Liora --actor opencode \
  --step-id liora-1 --parent-step-id jorhas --operation start --status RUNNING
```

To report `SUCCESS`, supply `--operation finish --status SUCCESS`,
`--artifact-root PRIVATE_ROOT/outputs/RUN_ID`, and `--artifact RELATIVE_PATH`.
The file must already exist within that output root. Symbolic links, traversal,
external paths and wrong hashes are rejected. For a failure or partial result,
use the matching operational status. Never report approval, source verification,
or a persona event on behalf of work that did not happen. Provide an event ID
using `--event-id` for idempotent retries.

If the server is temporarily unreachable, the adapter stores a private event
in the spool and returns exit 3. Replay uses the same common arguments followed
by `replay`. The capability is read at sending time and is never put in the
spool. Rejected 4xx requests are not silently replayed. Keep all run, spool,
and capability files outside the Git checkout.

## Approval and limits

At startup in an interactive terminal, set a private review passphrase of at
least 12 characters. Type it in the dashboard for each approval decision. If
startup is noninteractive or the passphrase is left blank, approval is disabled
until the server is restarted with a passphrase. The passphrase is kept in
server memory and is not sent to the agent bridge or stored in the event log.
The bridge capability cannot authorize a decision. The local session and
passphrase are not proof of identity or human presence. An adversary with full
access to the same operating-system account is outside this boundary.

Final approval records a manifest hash and a snapshot of artifact hashes.
Inspect the artifacts and compare these hashes again before sharing: later
filesystem changes are not automatically prevented. Approval does not validate
evidence and does not authorize publication. The server binds only to loopback.
Do not expose it through a public tunnel or reverse proxy.
Use only one Observatory server process per private root directory. Concurrent
servers sharing a root are not supported.

```bash
python -m epistarium.observatory.verify_approval --root PRIVATE_ROOT --run-id RUN_ID
```

This command detects changed, missing, or added files. It does not assess
research quality or identify the reviewer.

`--allow-partial` changes only the exit code of `jorhas-pathfind` and
`jorhas-full` for `PARTIAL`. It does not change the manifest status. Blocked,
failed or incomplete results remain nonzero.
