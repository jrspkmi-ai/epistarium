English | [Bahasa Indonesia](COMPATIBILITY_MATRIX.id.md)

<!-- section: scope -->
# Compatibility matrix

Documentation date: 2026-11-03. App versions tested: none. Native activation PASS: 0/10, NOT_RUN: 10/10.
Official source review: PASS 9/10, BLOCKED 1/10. Validating skill metadata does not prove native app support.

| Platform | Source review | Package route | Native execution |
|---|---|---|---|
| [OpenCode](../../docs/en/platforms/opencode.md) | PASS | Canonical .agents project skills | NOT_RUN |
| [Google Antigravity](../../docs/en/platforms/antigravity.md) | PASS | Canonical .agents project skills | NOT_RUN |
| [OpenAI Codex](../../docs/en/platforms/codex.md) | PASS | Canonical .agents project skills | NOT_RUN |
| [ChatGPT](../../docs/en/platforms/chatgpt.md) | PASS | Manual complete project | NOT_RUN |
| [Claude Code and Claude web](../../docs/en/platforms/claude.md) | PASS | Managed project adapter | NOT_RUN |
| [Gemini CLI and Gemini web](../../docs/en/platforms/gemini.md) | PASS | Canonical .agents project skills | NOT_RUN |
| [GitHub Copilot](../../docs/en/platforms/copilot.md) | PASS | Canonical .agents project skills | NOT_RUN |
| [Cursor](../../docs/en/platforms/cursor.md) | PASS | Canonical .agents project skills | NOT_RUN |
| [Windsurf](../../docs/en/platforms/windsurf.md) | BLOCKED | Manual complete project | NOT_RUN |
| [Amp](../../docs/en/platforms/amp.md) | PASS | Canonical .agents project skills | NOT_RUN |

<!-- section: os -->
## Operating systems and Python

| Environment | Local runtime | CI execution | Notes |
|---|---|---|---|
| Linux x86_64, glibc 2.39, Python 3.12.14 | PASS | NOT_RUN | Container tests, clean installs, and CLI artifacts |
| Ubuntu/Debian desktop installation | NOT_RUN | NOT_RUN | Official package instructions reviewed |
| Windows 10/11 | NOT_RUN | NOT_RUN | Explicit venv python.exe, no activation-policy change |
| macOS Intel | NOT_RUN | NOT_RUN | Universal2 Python route documented |
| macOS Apple Silicon | NOT_RUN | NOT_RUN | Universal2 Python route documented |
| Windows ARM, Linux ARM, musl/Alpine | NOT_RUN | NOT_RUN | No compatibility promise |

The prepared CI matrix has 9 jobs: 3 OS labels times Python 3.11, 3.12, and 3.14.
Remote job result: NOT_RUN 9/9. No repository was created or workflow dispatched.
Python >=3.11 is the metadata requirement. Local validation covers 3.12.14 only.

<!-- section: boundaries -->
## Integration boundaries

The complete ZIP is the project distribution. The wheel alone installs Python tools and carries no .agents directory.
The Claude adapter is generated locally and excluded from the release ZIP. Its hash check is distinct from Claude activation.
ChatGPT Work manual execution needs tools in that session. Web upload alone does not grant local filesystem or terminal access.
Claude web/account Skills, Gemini web, Copilot cloud agents, and local coding clients have separate lifecycles and environments.
No marketplace plugin, npx skills route, or global standalone persona installation was validated.

Windsurf source verification is BLOCKED. Its official URL redirected to inaccessible Devin documentation.
The guide supplies manual file-reading instructions and makes no native path or version claim.
A host that lacks terminal tools can review source material, but must leave deterministic execution NOT_RUN.
