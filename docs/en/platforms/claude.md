English | [Bahasa Indonesia](../../id/platforms/claude.md)

<!-- section: scope -->
# Claude Code and Claude web

EPISTARIUM v0.7.1 RELEASE_CANDIDATE. Documentation checked 2026-11-03.
Official [skill documentation](https://code.claude.com/docs/en/skills) and [product site](https://claude.com).
Source verification: PASS. Native EPISTARIUM activation: NOT_RUN. App version tested: none.
The minimum app version for this complete package is not established. Use a vendor-supported version and verify the required feature.

Claude Code documents native .claude/skills discovery. Generate a managed copy from .agents/skills. This is a project adapter, not a marketplace plugin.

No marketplace/plugin installation command is provided. This candidate has no tested native plugin manifest.

<!-- section: setup -->
## 1. Prepare the project

Follow the [Windows](../install/windows.md), [macOS](../install/macos.md), or [Linux](../install/linux.md) guide first.
Read [licensing](../LICENSING.md). Keep private sources outside public files.

Install Claude Code from its official setup instructions. Open the complete project root. Run the adapter commands below with the project venv.

| Scope | Documented location or boundary |
|---|---|
| Project | `.claude/skills/ via a generated project adapter` |
| User/global | `~/.claude/skills/ is documented, but this package does not install there` |
| EPISTARIUM route | Complete project, canonical .agents/skills, local venv |

Global locations are reference information. This candidate does not copy skills into your home directory.
The guides need the complete project. Copying a standalone SKILL.md omits the Python runtime and shared evidence documents.

```bash
.venv/bin/python scripts/sync_host_skills.py --host claude --apply
.venv/bin/python scripts/sync_host_skills.py --host claude --check
```

The adapter copies all ten skills and guides byte for byte. A hash manifest records their canonical origin and version.
Rerun --apply after updates. It refuses unmanaged files, modified adapter files, and symlinks.
If a generated file was edited, preserve that edit before removing or refreshing the adapter.
The generator is tested locally. Native Claude activation remains NOT_RUN.

<!-- section: activate -->
## 2. Select a persona

In local Claude Code, enter /jorhas-master-diving. Use /huxley-citation-auditor for citation work or another exact persona name.

ID: "Gunakan Jorhas untuk memetakan penggunaan AI oleh mahasiswa. Jalankan contoh sintetis lokal dan tampilkan berkas yang benar-benar dibuat."

EN: "Use Jorhas to map student AI use. Run the local synthetic example and show the files actually created."

For a first file check, ask Ideon to use examples/bilingual/origo.en.json.
Jorhas coordinates nine specialists only when their required inputs exist. Missing stages stay NOT_RUN or BLOCKED.
Read [all ten tutorials](../PERSONA_TUTORIALS.md) for task selection.

<!-- section: runtime -->
## 3. Link the local Python runtime

Ask the agent to use the project venv interpreter from the project root. The shell command is not a host-specific installation command.

```bash
.venv/bin/python -m epistarium doctor --lang en
.venv/bin/python -m epistarium ideon-origo --input examples/bilingual/origo.en.json --lang en --out private/host-map-en-001
```

On Windows, replace .venv/bin/python with .\.venv\Scripts\python.exe. No activation script is required.
For Indonesian reports, use --lang id and the Indonesian input where appropriate. Choose a fresh output folder.
Doctor checks dependencies and reports skill_count_at_project_root 10. It does not prove host activation.
If the host has no terminal, run these commands yourself and upload only permitted outputs. Record agent execution NOT_RUN.

<!-- section: permissions -->
## 4. Review permissions

Allow the agent to read the project and explicitly selected research files. Keep writes inside the chosen private output folder.
Allow terminal execution only for commands you can inspect. Installing dependencies needs network access to your approved package source.
Synthetic research examples need no internet. Live providers require separate user authorization and the command's network option where supported.
A skill cannot grant filesystem, terminal, login, or network rights. Do not bypass workspace policy, CAPTCHA, paywalls, or access restrictions.
Cloud or remote hosts need their own uploaded project, dependencies, and writable output folder. Your computer's venv is not transferred automatically.

<!-- section: verify -->
## 5. Verify actual execution

Inspect the slash-command list and loaded skill trace. Run --check on the adapter. Confirm doctor and the requested artifacts in the tool transcript.

Compare claimed output names with real files. Open the JSON status and any DOCX/XLSX/PDF copy.
Separate discovery, skill loading, CLI execution, artifact validity, and research judgment. A PASS at one level does not establish the others.
If a tool is denied, record BLOCKED with the denied step. If a step was not attempted, record NOT_RUN.
This guide contains a real request example, but no native host success claim.

<!-- section: limits -->
## 6. Limits, update, and removal

Claude web and Cowork account skills have a different lifecycle from local folders. Account sync does not install EPISTARIUM Python. Cloud project threads have additional limits.

Update the complete project in a separate folder. Recreate the venv and rerun doctor.
For canonical native routes, reopen or refresh the host's skills after replacing the project. Avoid same-name copies in user/global locations.
For the Claude adapter, rerun --apply and --check. To remove only its managed copies, run:

```bash
.venv/bin/python scripts/sync_host_skills.py --host claude --remove
```

Use that removal command only if you created the Claude adapter. Other hosts need no generated adapter removal.
Close the old workspace and remove its extracted folder after backing up research. This does not uninstall the AI application.
For manual mode, remove the attached instructions/context from the chat. It has no global skill installation to remove.

See [compatibility evidence](../../../reports/v0.7.0/COMPATIBILITY_MATRIX.md) and [source research](../../../reports/v0.7.0/SOURCE_RESEARCH.md).
A verified npx skills installation is not included. No public repository URL is assumed.
