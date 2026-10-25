"""Validate uploaded inputs before any parsing or model inference."""
from pathlib import Path
from fastapi import HTTPException, UploadFile

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

def validate_file_metadata(filename: str | None, content: bytes) -> str:
    name = (filename or "").strip()
    extension = Path(name).suffix.lower()
    if not name or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
    if not content:
        raise HTTPException(status_code=400, detail="File is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size must not exceed 5 MB.")
    return extension

def resolve_jd_input(job_description: str | None, jd_file: UploadFile | None) -> str:
    has_text = bool(job_description and job_description.strip())
    has_file = jd_file is not None
    if has_text == has_file:
        raise HTTPException(status_code=400, detail="Provide exactly one JD input: text or a PDF/DOCX file.")
    return "text" if has_text else "file"
