# Language policy

EPISTARIUM has one implementation and ten persona identities. Indonesian and English are language choices within that package.

## Select the output language

Use --lang id or --lang en before or after the command. --lang auto uses the system language, with English for non-Indonesian locales.

Language priority is the explicit flag, EPISTARIUM_LANG, a configuration language field, then the system locale. Agents must pass an explicit flag that follows the user request.

A configuration can contain `"language":"en"` or `"language":"id"`. This field works in Jorhas configuration files and ORIGO input files.

Python APIs accept lang='en' or lang='id' on research entry functions. Without a language argument or active context, Python APIs keep Indonesian for compatibility.

```python
from epistarium import origo
result = origo.export({"idea": "Digital communication at university"}, "private/map-en-002", lang="en")
```

A language context applies to nested stages and resets after each call. It does not change the process locale or the language of another task.

## Separate presentation from data

| Surface | Language behavior |
|---|---|
| Persona identity and command names | Remain the same |
| CLI help, program messages, and reports | Use the selected language |
| ORIGO generated prose and 21 question labels | Use the selected language |
| New literature workbook | Uses the selected sheet names and column labels |
| Canonical JSON and CSV keys | Keep the existing contract |
| Fixed status and issue codes | Stay stable |
| English *_display.csv files | Use English column labels and known status labels |
| Source titles, quotes, names, numbers, and DOI values | Stay in their source form |
| Existing template headings and human entries | Stay intact |
| Historical reports and source fixtures | Keep their original language |

A record can therefore contain English guidance beside an Indonesian source quote. That mixture preserves evidence rather than translating it silently.

A display CSV is for reading. Do not feed it back as a canonical ledger. Use the original JSON or CSV for data exchange.

## English ORIGO input

| English alias | Canonical key |
|---|---|
| idea | ide_awal |
| topic | topik |
| phenomenon | fenomena |
| focus | fokus |
| theory | teori_pilihan |
| paradigm | paradigma |
| method | metode_pilihan |
| research_question | pertanyaan_penelitian |
| unit_of_analysis | unit_analisis |
| data_access | akses_data |
| title_count | judul_count |
| answers | jawaban_21 |
| changes | perubahan |
| supervisor_feedback | perubahan_pembimbing |
| discipline | bidang_ilmu |
| level | jenjang |
| user_notes | catatan_pengguna |

If both keys disagree, the tool rejects the input. Alias conversion does not modify the supplied text.

Data access can use corpus, participants, and organization as keys. Supported descriptions include available, unavailable, not yet available, restricted, and unconfirmed.

REVISION accepts empirical_context, research_focus, theoretical_basis, method_direction, potential_contribution, and candidate_titles as node aliases. Unchanged previous nodes stay intact across language choices.

## Source language and writing rules

Report language does not select a manuscript style. For an English manuscript, use Quilo with --preset academic-en. Keep --lang as the report choice.

The English preset flags possible issues without automatic rewriting. Numbers, quotes, citations, DOI values, negation, direction, and uncertainty remain protected.

English program prose follows SimpleEnglish Plain mode. Technical meanings take priority over word substitutions. Keep paradigm, ontology, and epistemology when the research uses those concepts.
