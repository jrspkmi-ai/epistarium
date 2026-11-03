# Move from 0.5.0 to 0.6.0

Keep the old project and its run folders. Extract 0.6.0 into a separate folder. Open the root that contains pyproject.toml and .agents/skills/.

Install the new version in a Python environment. Run doctor with an explicit language. Existing command names and file names remain valid.

For existing scripts, add --lang id to keep Indonesian CLI presentation. Without the flag, CLI language follows the documented priority and system locale.

Python entry functions keep Indonesian when no language is selected. Use lang='en' to obtain English program text. Nested research stages inherit that language.

Data Ledger still has 48 columns. Source Ledger still has 21 columns. Language selection does not rename canonical fields or fixed status values.

English runs add display CSV files. New English workbooks use English headings. Both known header sets work as literature templates.

If a template already has Indonesian headings, an English run keeps those headings. It appends English program guidance and unchanged source evidence.

Quilo has an explicit academic-en preset. It reports wording issues without automatic English edits. The report language remains a separate choice.

Every persona still has one SKILL.md. Its references folder contains the two language guides. Do not install them as separate skills.

Historical reports keep their original versions and languages. Read the 0.6.0 release report for current test results.
