English | [Bahasa Indonesia](../id/PERSONA_TUTORIALS.md)

<!-- section: start -->
# Persona tutorials

These examples describe requests, inputs, and expected file types. Example outputs are illustrative unless a current log names the command.
Use synthetic fixtures for practice. A fluent answer alone does not prove execution.
Install with the OS guide, then follow [First Research](FIRST_RESEARCH.md).

<!-- section: jorhas-master-diving -->
## Jorhas: The Path Finder

Map a phenomenon and three research directions.

ID: "Carikan bukti dan tiga alternatif fokus penggunaan AI oleh mahasiswa."

EN: "Find evidence and three possible focuses for student AI use."

Input: One idea, optional source configuration.

Illustrative output: Source/data ledgers, three draft directions, RUN_MANIFEST.json.

Status: PARTIAL is expected. Missing data stays NOT_RUN or unverified.

Human review: Novelty, causation, access rights, and feasibility need a researcher.

Use [the full guide](../../.agents/skills/jorhas-master-diving/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.

<!-- section: ideon-topic-brainstormer -->
## Ideon: The Research Architect

Build an ORIGO research map.

ID: "Susun tiga alternatif rancangan dari ide penelitian saya."

EN: "Build three research designs from my initial idea."

Input: Idea JSON, optional evidence and previous map for revision.

Illustrative output: ORIGO JSON and one DOCX with two parts, six nodes, and 21 questions.

Status: CREATED_AND_REOPENED confirms the DOCX was reopened. It does not validate the design.

Human review: Check paradigm, ontology, epistemology, method, and scope.

Use [the full guide](../../.agents/skills/ideon-topic-brainstormer/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.

<!-- section: liora-literature-scout -->
## Liora: The Literature Scout

Find literature metadata and candidates.

ID: "Carikan studi lima tahun terakhir tentang komunikasi krisis digital."

EN: "Find studies from the last five years on digital crisis communication."

Input: Topic, date window, optional offline metadata fixture.

Illustrative output: candidates.json and candidates.csv with provenance.

Status: Candidate metadata is not full-text reading or verified claim support.

Human review: Read sources and check relevance before including a study.

Use [the full guide](../../.agents/skills/liora-literature-scout/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.

<!-- section: agresa-index-verifier -->
## Agresa: The Index Sentinel

Compare archived index evidence.

ID: "Periksa jurnal ini menggunakan rekaman indeks resmi yang saya berikan."

EN: "Check these journals against the official index records I provide."

Input: Journal JSON and archived index-evidence JSON.

Illustrative output: Index audit JSON/CSV and a report with evidence dates.

Status: An unconfirmed index remains unverified. Journal evidence does not prove article indexing.

Human review: Check official records, dates, journal identity, and article coverage.

Use [the full guide](../../.agents/skills/agresa-index-verifier/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.

<!-- section: retho-fulltext-retriever -->
## Retho: The Paper Retriever

Check local full-text access and identity.

ID: "Periksa PDF berizin untuk kandidat literatur ini."

EN: "Check the permitted PDFs for these literature candidates."

Input: Liora candidates and a local PDF map with rights information.

Illustrative output: articles.json, retrieval_report.md, hashes, and access/version records.

Status: Abstract-only, identity mismatch, missing rights, and scanned text remain separate outcomes.

Human review: Confirm download rights, identity, and manuscript version. Automatic download stays disabled.

Use [the full guide](../../.agents/skills/retho-fulltext-retriever/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.

<!-- section: domares-critical-reader -->
## Domares: The Critical Reader

Locate candidate passages in full-text.

ID: "Baca artikel berizin ini dan temukan bagian metode serta temuannya."

EN: "Read these permitted articles and locate their method and findings."

Input: Suitable Retho articles.json records and accessible PDFs.

Illustrative output: critical_readings.json and reading_report.md with PDF page candidates.

Status: A passage candidate is not a human judgment. Scans need separate OCR or manual reading.

Human review: Read the full context and confirm each interpretation.

Use [the full guide](../../.agents/skills/domares-critical-reader/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.

<!-- section: synthia-literature-review -->
## Synthia: The Knowledge Weaver

Organize a literature matrix and draft synthesis.

ID: "Susun matriks literatur dari hasil pembacaan kritis ini."

EN: "Build a literature matrix from these critical readings."

Input: Domares readings JSON, optional user-owned XLSX template.

Illustrative output: 20-column matrix, evidence audit, XLSX, and draft synthesis.

Status: Missing readings stay unassessed. Workbook creation is checked separately.

Human review: Confirm study comparisons, theory, and synthesis against the sources.

Use [the full guide](../../.agents/skills/synthia-literature-review/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.

<!-- section: vanlan-powerlink-verify -->
## Vanlan: The Evidence Guardian

Locate exact PDF evidence and record review decisions.

ID: "Periksa apakah paragraf saya didukung oleh PDF terlampir."

EN: "Check whether my paragraph is supported by the attached PDFs."

Input: Claims JSON, permitted PDFs, literal anchors, optional attributed human reviews.

Illustrative output: Claim audit, page coordinates, source hashes, annotated PDF copies when an anchor is unique.

Status: Text matches establish locations only. Semantic support stays unassessed without a valid human review.

Human review: Read surrounding passages. A reviewer name and reason are required for human adjudication.

Use [the full guide](../../.agents/skills/vanlan-powerlink-verify/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.

<!-- section: quilo-academic-writer -->
## Quilo: The Academic Scribe

Audit prose and protect evidence tokens during revision.

ID: "Tinjau draf ini dengan menjaga kutipan, angka, sitasi, dan ketidakpastian."

EN: "Review this draft and preserve quotes, numbers, citations, and uncertainty."

Input: TXT/DOCX manuscript, optional external revision and private style JSON.

Illustrative output: Editorial issues, protected-token checks, optional comparison report.

Status: Report language and manuscript preset are separate. semantic_validity stays NOT_ASSESSED.

Human review: Review meaning, causal claims, author voice, and flagged edits.

Use [the full guide](../../.agents/skills/quilo-academic-writer/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.

<!-- section: huxley-citation-auditor -->
## Huxley: The Citation Cartographer

Compare citations and references in both directions.

ID: "Periksa semua sitasi terhadap daftar pustaka dalam naskah ini."

EN: "Check all citations against the references in this manuscript."

Input: DOCX manuscript, optional synthetic candidate metadata fixture.

Illustrative output: Citation/reference audit, unmatched entries, optional highlighted DOCX copy.

Status: A reference match does not verify a claim. The parser covers a limited APA author-date subset.

Human review: Review ambiguous names, reference details, dynamic fields, and source meaning.

Use [the full guide](../../.agents/skills/huxley-citation-auditor/references/guide.en.md) for commands and handoffs.
If required files or permissions are missing, record BLOCKED or NOT_RUN. Do not invent an output file.
