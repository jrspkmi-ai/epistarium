# Safe GitHub deployment: v0.8.0 Observatory

Repository: https://github.com/jrspkmi-ai/epistarium

**Use the OVERLAY ZIP on a fresh clone of the current repository.** Do not replace the repository wholesale using the older v0.7.1 archive. The remote repository already contains a new brand hero and optimized CI workflow. The overlay deliberately omits both READMEs and the CI YAML, supplying idempotent merger scripts instead.

## macOS and Linux

```bash
git clone https://github.com/jrspkmi-ai/epistarium.git
cd epistarium
git switch -c feature/research-observatory-v0.8.0
# Extract EPISTARIUM_v0.8.0_GITHUB_OVERLAY.zip into this repository root.
# The ZIP has no wrapping folder. Hidden folders must be included.
python scripts/merge_observatory_readme.py
python scripts/merge_observatory_ci.py
python scripts/regenerate_source_checksums.py
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python scripts/verify_skills.py
.venv/bin/python scripts/check_docs.py
.venv/bin/python scripts/check_english.py
.venv/bin/python -m pytest -q
.venv/bin/python -m epistarium observatory --help
.venv/bin/python -m epistarium observatory --idea 'Consumer crisis' --open
```

The screenshot, approval, and live activity test requires a browser that can connect to localhost on that machine. Stop the local server with Ctrl+C.

Review `git status`, scan for secrets or research files, and verify that the original `assets/brand/readme-hero.png` remains present. Commit and push the **feature branch only**:

```bash
git add -A
git diff --cached --stat
git commit -m 'feat: add EPISTARIUM v0.8.0 Research Observatory'
git push -u origin feature/research-observatory-v0.8.0
```

Open a pull request against `main`. Review the GitHub Actions results, including Windows, macOS and Linux. Perform manual live-browser approval tests. Only merge to `main` and create a release after a GO decision. Never use `git push --force`.

## Windows PowerShell differences

Use `py -3 -m venv .venv`, then `.\\.venv\\Scripts\\python.exe -m pip install -e '.[test]'`. Use that Python executable in the checks above. Use GitHub Desktop or PowerShell for the clone, branch, commit and push. In Antigravity, provide this document and the OVERLAY ZIP; instruct the agent to execute only audited commands and **not** merge the PR automatically.

## Current tested and untested claims

Local Python and simulated-browser checks are documented in `reports/v0.8.0/TEST_RESULTS.md`. This archive was built without pushing changes. No GitHub Actions run exists yet for the new v0.8.0 commit. CI and desktop browser tests are mandatory for the main branch release gate.
