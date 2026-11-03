# Platform test scope

The Python CLI and the skill guides are separate surfaces. A working CLI does not establish native skill discovery in an AI host.

Open the project root with .agents/skills/ and pyproject.toml. Each persona keeps the same entrypoint in both languages. Read only its selected guide.

The current release report records actual Linux tests and wheel installation. Native macOS, Windows, Codex, Antigravity, and OpenCode tests on user devices require separate execution.

The repository includes a CI matrix for Linux, macOS, and Windows. Its presence is not a successful remote CI run.

The wheel contains the library and CLI. The project ZIP also contains persona guides and documentation. No global personal skill installation is performed.
