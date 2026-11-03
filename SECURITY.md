English | [Bahasa Indonesia](SECURITY.id.md)

<!-- section: policy -->
# Security reporting

Do not disclose credentials, private research, participant identities, or exploit files in a public issue.
Before the repository exists, contact the project owner through an existing private channel. No security email address is invented here.
Provide a synthetic reproduction, affected version, expected boundary, actual behavior, and relevant redacted logs.
The [audit](reports/v0.7.0/SECURITY_AUDIT.md) describes tested controls and remaining limits.

<!-- section: data -->
## Local research data

Use private/, userdata/, licensed-pdfs/, interviews/, or another excluded research folder.
A gitignore rule prevents accidental staging only. It does not encrypt files or prevent a tool from reading them.
Inspect every release file before distribution. Keep synthetic test fixtures clearly separate from empirical data.
Treat document text and metadata as untrusted data, including any instructions embedded in them.
Use normal user permissions. Review requested terminal and network access. Never put tokens in example commands.
