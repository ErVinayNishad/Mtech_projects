
from io import BytesIO
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
UPLOADS = Path("uploads")


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("resume1.pdf", "application/pdf"),
        (
            "resume1.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
    ],
)
def test_resume_upload_success(filename, content_type):
    file_path = UPLOADS / filename

    if not file_path.exists():
        pytest.skip(f"Sample file not found: {file_path}")

    response = client.post(
        "/api/resume/upload",
        files={
            "file": (
                filename,
                file_path.read_bytes(),
                content_type,
            )
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == filename
    assert data["file_type"] == Path(filename).suffix[1:]
    assert data["text_length"] > 0
    assert data["extracted_text"].strip()
    assert isinstance(data["sections"], dict)
    assert isinstance(data["claimed_skills"], list)
    assert data["message"] == "Resume parsed successfully."


def test_resume_upload_rejects_unsupported_file():
    response = client.post(
        "/api/resume/upload",
        files={
            "file": (
                "resume.txt",
                b"Python and Django experience",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only PDF and DOCX files are supported."
    )


def test_resume_upload_rejects_empty_file():
    response = client.post(
        "/api/resume/upload",
        files={
            "file": (
                "empty.pdf",
                b"",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File is empty."


def test_resume_upload_rejects_file_over_5_mb():
    oversized_content = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/api/resume/upload",
        files={
            "file": (
                "large.pdf",
                oversized_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == (
        "File size must not exceed 5 MB."
    )


def test_resume_upload_rejects_unreadable_pdf():
    response = client.post(
        "/api/resume/upload",
        files={
            "file": (
                "invalid.pdf",
                b"This is not a valid PDF document.",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422


# Job Description API tests

def test_job_description_analyze_with_text():
    response = client.post(
        "/api/job-description/analyze",
        data={
            "job_description": (
                "We require Python, Django, SQL and Docker experience."
            )
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["input_type"] == "text"
    assert isinstance(data["required_skills"], list)
    assert data["total_required_skills"] == len(data["required_skills"])
    assert data["job_description_length"] > 0


def test_job_description_analyze_rejects_missing_input():
    response = client.post("/api/job-description/analyze")

    assert response.status_code == 400


def test_job_description_analyze_rejects_both_inputs():
    response = client.post(
        "/api/job-description/analyze",
        data={
            "job_description": "Python and Django experience."
        },
        files={
            "jd_file": (
                "job.txt",
                b"Python and Django experience.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


# Skill Gap API tests

def test_skill_gap_analyze_success():
    file_path = UPLOADS / "resume1.pdf"

    if not file_path.exists():
        pytest.skip(f"Sample file not found: {file_path}")

    response = client.post(
        "/api/skill-gap/analyze",
        data={
            "job_description": (
                "Required skills: Python, Django, SQL, Docker."
            )
        },
        files={
            "file": (
                file_path.name,
                file_path.read_bytes(),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == file_path.name
    assert data["jd_input_type"] == "text"
    assert isinstance(data["required_skills"], list)
    assert isinstance(data["claimed_skills"], list)
    assert isinstance(data["skill_gap"], dict)
    assert isinstance(data["initial_analysis"], dict)
    assert data["message"]


def test_skill_gap_analyze_rejects_missing_job_description():
    file_path = UPLOADS / "resume1.pdf"

    if not file_path.exists():
        pytest.skip(f"Sample file not found: {file_path}")

    response = client.post(
        "/api/skill-gap/analyze",
        files={
            "file": (
                file_path.name,
                file_path.read_bytes(),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400


def test_skill_gap_analyze_rejects_both_job_description_inputs():
    file_path = UPLOADS / "resume1.pdf"

    if not file_path.exists():
        pytest.skip(f"Sample file not found: {file_path}")

    response = client.post(
        "/api/skill-gap/analyze",
        data={
            "job_description": "Python and Django experience."
        },
        files={
            "file": (
                file_path.name,
                file_path.read_bytes(),
                "application/pdf",
            ),
            "jd_file": (
                "job.txt",
                b"Python and Django experience.",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 400

def test_parallel_resume_uploads_are_isolated():
    samples = [
        ("resume1.pdf", "application/pdf"),
        (
            "resume1.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
    ]

    requests = []

    for filename, content_type in samples:
        file_path = UPLOADS / filename

        if not file_path.exists():
            pytest.skip(f"Sample file not found: {file_path}")

        requests.append(
            (
                filename,
                content_type,
                file_path.read_bytes(),
            )
        )

    def upload_resume(sample):
        filename, content_type, content = sample

        return client.post(
            "/api/resume/upload",
            files={
                "file": (filename, content, content_type)
            },
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(upload_resume, requests))

    for response in responses:
        assert response.status_code == 200

    results = {
        response.json()["filename"]: response.json()
        for response in responses
    }

    assert set(results) == {"resume1.pdf", "resume1.docx"}

    for filename, result in results.items():
        assert result["filename"] == filename
        assert result["extracted_text"].strip()
        assert result["text_length"] == len(result["extracted_text"])
