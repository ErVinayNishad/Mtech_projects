# Resume Skill Verification — M1–M5

Maintainable modular FastAPI project. Backend code, modules, tests, and evaluation assets are grouped under `backend/`; documentation is grouped under `docs/`. The five modules are connected through one API workflow; they are not separate applications.

## Architecture

- `backend/modules/M01_input_sources`: input constraints and JD input selection.
- `backend/modules/M02_document_processing`: PDF/DOCX text extraction and validation errors.
- `backend/modules/M03_nlp_information_extraction`: resume parsing, claimed-skill extraction and JD required-skill extraction. Uses the existing pretrained GLiNER pipeline; no fine-tuning is claimed.
- `backend/modules/M04_semantic_skill_matching`: current skill comparison and gap calculation implementation.
- `backend/modules/M05_initial_skill_gap`: initial gap interpretation and candidate feedback.
- `backend/app/api/routes.py`: HTTP request/response and orchestration only.
- `backend/app/core/config.py`: central app configuration.
- `backend/tests/`: API, unit and regression tests.

## Setup (Windows PowerShell)

Use Python 3.11 or 3.12 for the most predictable ML dependency compatibility.

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload
```

If Python 3.11 is not installed, check `py -0p`. Do not pin an unavailable NumPy version. Model weights are downloaded on first model inference and require internet access then.

## Endpoints

- `GET /health`
- `POST /api/resume/upload` (multipart `file`)
- `POST /api/job-description/analyze` (multipart `job_description` OR `jd_file`)
- `POST /api/skill-gap/analyze` (multipart `file` plus exactly one of `job_description` or `jd_file`)

## Limitations and honesty

- Scanned PDFs need OCR, which is not included.
- Skill extraction results are model predictions and may contain false positives/negatives.
- Similarity is not proof of competence.
- Run the complete test suite and live model-backed API tests in your target environment before presenting the project as validated.
- This package only covers the five agreed modules; adaptive interview is out of scope.

## M1–M5 request flow

1. M1 checks that the request contains one supported resume and exactly one JD input.
2. M2 extracts readable text from PDF/DOCX and returns a clear client error for invalid/unreadable documents.
3. M3 uses the cached pretrained GLiNER model for open-vocabulary resume claims and JD requirements. Exact-mention fallback recovers known skill names the model may miss (for example, REST APIs in work experience); ambiguous short names such as `C` and `Go` are not inferred by lexical fallback from arbitrary prose. Unknown model-detected skills are preserved instead of being discarded solely because they are not in an alias dictionary.
4. M4 compares normalized names first and uses MiniLM semantic similarity for non-exact names. Semantic scores are similarity signals, not verified proficiency.
5. M5 uses M4's semantic results to decide which skills remain unresolved. A HIGH/MEDIUM semantic match is not reported as missing just because the spelling differs; LOW matches remain candidates for feedback.

## Regression checks

```powershell
python -m pytest -q
python -m compileall -q app modules tests
```

The automated suite includes deterministic API-flow tests with model calls mocked, PDF/DOCX parsing tests, open-vocabulary skill tests, alias handling, and M5 feedback decisions. These tests validate wiring and deterministic logic, not real-model accuracy. Run model-backed smoke tests in the target environment after installing `requirements.txt` and downloading the pretrained weights.
