English | [Bahasa Indonesia](../../id/install/linux.md)

<!-- section: identity -->
# Install on Linux: Ubuntu and Debian

EPISTARIUM v0.9.0 RELEASE_CANDIDATE. Minimum package requirement: Python 3.11.
Only Linux x86_64 with Python 3.12.14 ran locally. This OS guide is documentation, not proof of native testing.

Read [licensing](../LICENSING.md) before installing the PDF runtime.
MIT covers original work. The runtime uses pypdfium2 and pypdf. See the v0.9.0 release gate.

<!-- section: python -->
## 1. Check Python and open a terminal

Open your distribution's Terminal application. Run `python3 --version`.
Ubuntu 24.04 and Debian 12/13 provide suitable Python families. Distribution installation was not run in this container.
If Python or venv is missing on Ubuntu/Debian, an authorized system administrator can install the missing OS packages:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

These two OS package commands need system privileges. The EPISTARIUM commands below do not.
Do not replace system Python or use sudo pip. If Python is below 3.11, use a supported distribution or separately managed interpreter.
Other distributions: use their official Python/venv package instructions. No unverified Fedora, Arch, or Alpine command is supplied.
See [Ubuntu guidance](https://documentation.ubuntu.com/ubuntu-for-developers/howto/python-setup/) and [Debian's venv package](https://packages.debian.org/stable/python3-venv).
Musl, Alpine, and Linux ARM are NOT_RUN. This candidate was tested on glibc Linux x86_64.

<!-- section: download -->
## 2. Extract and find the project root

On the GitHub repository page, select **Code > Download ZIP** or download the versioned ZIP asset from Releases when available.
Use your file manager's Extract All or Extract action. Keep the complete directory, including .agents/skills/.
Open the extracted project folder (for example, `epistarium-main` or `EPISTARIUM_v0.9.0`). Its root contains pyproject.toml, epistarium/, AGENTS.md, and .agents/skills/.
In the terminal, change to that folder. Replace this example path with your own:

```bash
cd "/home/YourName/Downloads/EPISTARIUM_v0.9.0"
ls -a
```

A virtual environment is a private Python installation folder for this project. It avoids mixing project packages with system packages.

<!-- section: install -->
## 3. Install and run doctor

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -m pip check
.venv/bin/python -m epistarium --version
.venv/bin/python -m epistarium doctor --lang en
```

No activation script is required. A normal user account is sufficient for these commands.
Pip needs network access to download dependencies. Research examples below are offline.
The runtime requires pypdfium2>=5.14,<6 and pypdf>=6.21,<7. PDFium wheels include component license notices.
It does not resolve AGPL obligations. Do not reuse a mixed 2.x environment. Create a new environment for this candidate.

Doctor checks dependency imports, time zone data, and write access. It does not test native AI activation or source truth.
Expect version 0.7.1, execution_status SUCCESS, and skill_count_at_project_root 10 at the correct project root.
This is an expected field summary. Exact observed Linux output is in [historical doctor evidence](../../../reports/v0.7.0/doctor-en.json).

<!-- section: example -->
## 4. Run the first example and read its files

```bash
.venv/bin/python -m epistarium ideon-origo --input examples/bilingual/origo.en.json --lang en --out private/first-map-en
.venv/bin/python -m epistarium ideon-origo --input examples/bilingual/origo.id.json --lang id --out private/first-map-id
```

Use a fresh folder name if you repeat a command. Open private/first-map-en in your file manager.
Read ideon_origo.json. Its output names identify the generated DOCX. Open that DOCX with your document reader.
Confirm docx_status CREATED_AND_REOPENED. Review the six nodes and 21 questions. The input is synthetic and the content remains a draft.
Select --lang auto to use the locale fallback. Explicit language overrides the environment and input configuration.
Jorhas keeps Asia/Jakarta unless --timezone sets another zone. Language selection does not change that time zone.
Read [First Research](../FIRST_RESEARCH.md) and the [persona tutorials](../PERSONA_TUTORIALS.md) next.

<!-- section: update -->
## 5. Update and uninstall

Back up private research outside the extracted project. Download a newer owner-approved package into a separate folder.
Read its migration guide. Create a fresh virtual environment, reinstall, and rerun doctor and the example.
Do not overwrite your only private data copy. If you generated a Claude adapter, remove it before deleting the old project.

To uninstall, close agents using this project. Remove only its .venv folder with your file manager.
Then remove the extracted project if no needed files remain. Deleting a venv removes its installed packages without changing system Python.
If you installed EPISTARIUM into another environment, run that environment's Python with `-m pip uninstall epistarium`.
Do not remove dependencies shared by other projects.

<!-- section: troubleshooting -->
## 6. Troubleshooting and validation limits

| Symptom | Action |
|---|---|
| pyproject.toml is missing | Open the complete extracted project root. |
| No module named epistarium | Install with the same venv interpreter used to run the command. |
| pypdfium2 or pypdf import fails | Create a clean venv and reinstall the bounded dependency. |
| No matching distribution | Check CPython version, CPU architecture, OS, and the pypdfium2 wheel support. Record BLOCKED if unavailable. |
| Folder already exists | Choose a new output folder. Do not overwrite a prior run. |
| Doctor reports zero skills | The wheel alone has no skills. Open the full ZIP project root. |
| Network or certificate error | Check your authorized proxy/certificate setup. Do not disable TLS verification. |
| Exit code 2 | Fix invalid input or contract fields. |
| Exit code 3 | Read the partial result and its stage statuses. |
| Exit code 4 | Read the blocked step and missing artifacts or dependencies. |

A zero exit code describes execution only. It does not verify scientific claims.
No live provider or paid AI service is required for these examples.
See [historical test results](../../../reports/v0.7.0/TEST_RESULTS.md) for actual commands and denominators.

Official references checked 2026-11-03: [venv](https://docs.python.org/3/library/venv.html) and the Python/OS references above. Native Linux: Ubuntu and Debian installation is PASS for the container flow only.
