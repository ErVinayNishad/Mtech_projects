# M1–M5 review and verification report

## Findings and changes in this revision

- Confirmed that the existing FastAPI layer already orchestrates M1–M5; no duplicate resume pipeline was added.
- M3 preserves unknown skill names returned by GLiNER, and now collapses internal whitespace before de-duplication. Generic entity labels such as `library`, `cloud platforms`, `devops tools`, and `software tools` are filtered.
- Fixed JD extraction to prioritize a labelled `Required Skills`/equivalent section when available. Responsibility and qualification prose is excluded from skill extraction, while GLiNER remains open-vocabulary within the selected skills section. The supplied Python Backend Developer JD is expected to yield its six listed skills rather than 11 mixed phrases.
- Resume claims are now extracted from the full resume, so skills mentioned in work experience/projects (including `REST APIs`) are not omitted merely because they are absent from the technical-skills list. A conservative exact-mention fallback supplements GLiNER for mapped known skills while preserving model-detected open-vocabulary skills. Highly ambiguous short names (`C`, `Go`) are excluded from arbitrary-text fallback to reduce false positives. API responses include `skill_evidence` records from relevant resume sections.
- Fixed JD fallback overlap handling: `React Native` is not counted as `React` by itself, while a JD that explicitly asks for both React and React Native keeps both.
- Expanded M4 canonical aliases for common variants including HTML5/HTML, CSS3/CSS, React Native, and Postgres/PostgreSQL.
- Fixed M4/M5 consistency: M4's public `matched_skills`, `missing_skills`, and totals now align with semantic classifications (HIGH/MEDIUM provisionally covered; LOW unresolved), while `exact_matched_skills` and `exact_missing_skills` preserve exact-match diagnostics. M5 likewise counts only LOW-classified required skills as unresolved initial gaps. This prevents conflicting counts and false missing-skill feedback due to spelling differences.
- Made the SentenceTransformer import lazy so API/test startup does not require importing the ML package until semantic inference is actually requested.
- Removed unreachable duplicate PDF extraction code after the first return.
- Avoids loading MiniLM when all required skills already have exact normalized matches.
- Added deterministic tests for the M1–M5 API flow, PDF/DOCX text extraction, open-vocabulary JD/resume skills, required-skills-section scoping, full-resume claim fallback, returned skill evidence, ambiguous short-name fallback, aliases, React/React Native overlap, M4/M5 count consistency, and feedback behavior.
- Added a regression test for the supplied Python Backend Developer resume/JD pattern: all six listed skills must be recovered, REST APIs evidence must be attached to work experience, and no false gap should be raised when all six are claimed.

## Test results

- Full regression suite after final fixes: **69 passed** on each of three consecutive runs.
- `python -m compileall -q app modules tests`: passed.
- The supplied resume PDF and JD DOCX were exercised through the API in a controlled run with GLiNER outputs deliberately mocked to miss REST APIs and the semantic model disabled for the exact-match case. The known-skill fallback recovered REST APIs, linked its work-experience evidence, extracted exactly six JD skills, and returned `NO_GAP` / `PERSONALIZED_INTERVIEW`. This validates parsing, fallback, matching and API wiring for this example; it is not a live-model accuracy result.
- The automated API regression uses a generated PDF and deterministic mocked GLiNER/embedding outputs to remain repeatable without network downloads.

## Limitations not to overclaim

- Live GLiNER and SentenceTransformer inference was not run in this packaging environment; the test suite uses controlled mocks for model behavior.
- No generalizable precision, recall, or F1 can be claimed from the two preliminary evaluation entries. The referenced resume files are not included in this package, and labels need independent verification.
- Semantic similarity does not prove practical competence; interview-based verification remains future work.
- Scanned/image-only PDFs require OCR, which is not included.
