# Final M1–M5 verification — revision 1.2

## Code changes in this revision

- Resume skill extraction remains GLiNER-first and open-vocabulary. Exact mentions of mapped known skills are added as a fallback so a model miss such as `REST APIs` in work experience does not silently become a false gap.
- Ambiguous short names (`C`, `Go`) are excluded from arbitrary-prose lexical fallback to reduce accidental claims; GLiNER can still detect them in context.
- M04 now reports public match/gap lists and totals consistently with semantic classifications. Exact-only matches/misses remain available separately for diagnosis.
- M04 skips SentenceTransformer loading when every required skill is already an exact normalized match.
- Existing M01–M05 folder structure and API orchestration are retained; no duplicate resume pipeline was introduced.
- Regression coverage was added for REST APIs fallback/evidence, M04/M05 count consistency, all-exact fast path, and the standard Python Backend Developer resume/JD scenario.

## Verification performed in this packaging environment

- `python -m compileall -q app modules tests`: PASS.
- Full test suite, run three consecutive times: **69 passed** each run.
- The uploaded `test_resume_standard(1).pdf` and `job description.docx` were run through the API in a controlled integration check. GLiNER output was deliberately mocked to omit `REST APIs`, and JD GLiNER output was mocked empty to exercise exact known-skill fallback. Results:
  - Required JD skills: Python, Django, REST APIs, MySQL, Git, Docker (6 total).
  - Resume claims include all six.
  - REST APIs evidence links to the resume's work-experience sentence.
  - M04: 6 matched, 0 missing.
  - M05: `NO_GAP`; next step `PERSONALIZED_INTERVIEW`.
- This controlled integration test validates file parsing, fallback, evidence, matching and route orchestration for the supplied example. It is **not** a live GLiNER/SentenceTransformer accuracy test because model outputs were mocked in this environment.

## Local verification still required

In the user's Windows Python 3.12 environment, install requirements if needed, run `python -m pytest -q`, then repeat the Swagger request with live model inference. A single sample does not establish generalizable precision, recall or F1.
