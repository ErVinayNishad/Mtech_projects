# Backend (M01–M05)

Run commands from this directory.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
python -m compileall -q app modules tests
uvicorn app.main:app --reload
```

The root `README.md` documents the architecture and endpoints. Design and verification notes are in `../docs/`.
