English | [Bahasa Indonesia](SOURCE_RESEARCH.id.md)

<!-- section: scope -->
# Official source research

Sources were opened or fetched on 2026-11-03. Source review is separate from command execution.
Documentation can change after this date. No minimum host version is asserted without a confirmed source.

| Topic | Official source | Observation |
|---|---|---|
| OpenCode | [Documentation](https://opencode.ai/docs/skills/) | PASS, native execution NOT_RUN |
| Google Antigravity | [Documentation](https://antigravity.google/docs/skills?tab=ide) | PASS, native execution NOT_RUN |
| OpenAI Codex | [Documentation](https://learn.chatgpt.com/docs/build-skills) | PASS, native execution NOT_RUN |
| ChatGPT | [Documentation](https://learn.chatgpt.com/docs/skills-and-plugins) | PASS, native execution NOT_RUN |
| Claude Code and Claude web | [Documentation](https://code.claude.com/docs/en/skills) | PASS, native execution NOT_RUN |
| Gemini CLI and Gemini web | [Documentation](https://geminicli.com/docs/cli/skills/) | PASS, native execution NOT_RUN |
| GitHub Copilot | [Documentation](https://docs.github.com/en/copilot/concepts/customizations/agent-skills) | PASS, native execution NOT_RUN |
| Cursor | [Documentation](https://cursor.com/help/customization/skills) | PASS, native execution NOT_RUN |
| Windsurf | [Documentation](https://docs.windsurf.com/windsurf/cascade/skills) | BLOCKED, native execution NOT_RUN |
| Amp | [Documentation](https://ampcode.com/docs/customize/skills) | PASS, native execution NOT_RUN |

<!-- section: os -->
## Python and OS sources

[Windows](https://docs.python.org/3/using/windows.html) · [macOS](https://docs.python.org/3/using/mac.html) · [venv](https://docs.python.org/3/library/venv.html)

[Python downloads](https://www.python.org/downloads/) · [Ubuntu Python](https://documentation.ubuntu.com/ubuntu-for-developers/howto/python-setup/) · [Debian venv](https://packages.debian.org/stable/python3-venv)

The guides use explicit venv interpreters. Windows avoids Activate.ps1 and global execution-policy changes.
The macOS guide distinguishes Intel and Apple Silicon. Linux privileges are limited to missing OS package installation.
No unverified package-manager commands are supplied for other distributions.

<!-- section: design -->
## Original README design

The inspected reference is [mattpocock/skills README](https://github.com/mattpocock/skills/blob/main/README.md).
Fetched README blob SHA: `f7038f139299985eea6c3e18398dbafb379a0010`.
The study identified useful navigation goals: visible installation, task selection, and linked guides.
EPISTARIUM uses its own research catalog, evidence rules, bilingual scope, and release matrix.
No reference prose, installer command, illustration, unique structure, or asset was copied into the candidate.
No reference repository installation command was renamed for EPISTARIUM.

Licensing sources and alternative backend findings are in [LICENSING_AUDIT](LICENSING_AUDIT.md).
