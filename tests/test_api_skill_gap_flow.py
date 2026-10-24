
from io import BytesIO

import numpy as np
import pymupdf
from fastapi.testclient import TestClient

from app.main import app
from modules.M03_nlp_information_extraction import jd_skill_extractor
from modules.M03_nlp_information_extraction import model_skill_extractor
from modules.M04_semantic_skill_matching import skill_matching


client = TestClient(app)


class DeterministicEmbeddingModel:
    """Tiny deterministic fake: only identical skill strings have cosine 1."""

    def encode(self, texts, normalize_embeddings=True):
        dimensions = {
            "pytorch lightning": 0,
            "rust": 1,
            "python": 2,
            "react": 3,
            "react native": 4,
        }
        vectors = np.zeros((len(texts), len(dimensions)), dtype=float)
        for row, text in enumerate(texts):
            vectors[row, dimensions.get(text.casefold(), 5)] = 1.0
        return vectors


def make_resume_pdf(text: str) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def test_skill_gap_api_connects_m01_to_m05_and_reports_new_skill_gap(monkeypatch):
    monkeypatch.setattr(
        model_skill_extractor,
        "get_claimed_skills_with_gliner",
        lambda text, section_name="technical_skills", threshold=0.30: [
            {
                "skill": "PyTorch Lightning",
                "source": "resume",
                "section": section_name,
                "claimed": True,
                "extraction_method": "GLiNER",
            }
        ],
    )
    monkeypatch.setattr(
        jd_skill_extractor,
        "extract_required_skills",
        lambda text: ["PyTorch Lightning", "Rust"],
    )
    monkeypatch.setattr(
        skill_matching,
        "get_semantic_model",
        lambda: DeterministicEmbeddingModel(),
    )

    resume_bytes = make_resume_pdf(
        "VINAY KUMAR\nTECHNICAL SKILLS\nPyTorch Lightning\n"
        "PROJECTS\nBuilt a text classifier."
    )
    response = client.post(
        "/api/skill-gap/analyze",
        files={"file": ("resume.pdf", BytesIO(resume_bytes), "application/pdf")},
        data={"job_description": "Need PyTorch Lightning and Rust."},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["required_skills"] == ["PyTorch Lightning", "Rust"]
    assert body["claimed_skills"] == ["PyTorch Lightning"]
    assert body["initial_analysis"]["status"] == "GAP_FOUND"
    assert body["initial_analysis"]["missing_skills"] == ["Rust"]
    assert body["candidate_feedback"]["next_step"] == "CANDIDATE_FEEDBACK"
    assert body["candidate_feedback"]["learning_suggestions"][0]["skill"] == "Rust"


def test_skill_gap_api_rejects_unsupported_resume_file():
    response = client.post(
        "/api/skill-gap/analyze",
        files={"file": ("resume.txt", b"plain text", "text/plain")},
        data={"job_description": "Need Python."},
    )
    assert response.status_code == 400


def test_semantic_skill_normalization_handles_common_aliases():
    assert skill_matching.normalize_skill("HTML5") == "html"
    assert skill_matching.normalize_skill("React Native") == "react native"
    assert skill_matching.normalize_skill("postgres") == "postgresql"


def test_resume_claim_extraction_receives_full_resume_text(monkeypatch):
    captured = {}

    def fake_claim_extractor(
        text, section_name="technical_skills", threshold=0.30
    ):
        captured["text"] = text
        captured["section_name"] = section_name
        return [
            {
                "skill": "REST APIs",
                "source": "resume",
                "section": section_name,
                "claimed": True,
                "extraction_method": "GLiNER",
            }
        ]

    monkeypatch.setattr(
        model_skill_extractor,
        "get_claimed_skills_with_gliner",
        fake_claim_extractor,
    )
    resume_bytes = make_resume_pdf(
        "VINAY KUMAR\nTECHNICAL SKILLS\nPython\nWORK EXPERIENCE\n"
        "Worked with REST APIs in production."
    )
    response = client.post(
        "/api/resume/upload",
        files={"file": ("resume.pdf", BytesIO(resume_bytes), "application/pdf")},
    )

    assert response.status_code == 200, response.text
    assert "Worked with REST APIs in production." in captured["text"]
    assert captured["section_name"] == "resume"
    assert any(
        item["skill"] == "REST APIs"
        for item in response.json()["claimed_skills"]
    )


def test_resume_api_returns_experience_evidence_for_claimed_skill(monkeypatch):
    monkeypatch.setattr(
        model_skill_extractor,
        "get_claimed_skills_with_gliner",
        lambda text, section_name="technical_skills", threshold=0.30: [
            {
                "skill": "REST APIs",
                "source": "resume",
                "section": section_name,
                "claimed": True,
                "extraction_method": "GLiNER",
            }
        ],
    )
    resume_bytes = make_resume_pdf(
        "VINAY KUMAR\nTECHNICAL SKILLS\nPython\nWORK EXPERIENCE\n"
        "Worked with REST APIs in production."
    )
    response = client.post(
        "/api/resume/upload",
        files={"file": ("resume.pdf", BytesIO(resume_bytes), "application/pdf")},
    )

    assert response.status_code == 200, response.text
    evidence = response.json()["skill_evidence"]
    rest_api_evidence = next(
        item for item in evidence if item["skill"] == "REST APIs"
    )
    assert rest_api_evidence["claimed"] is True
    assert rest_api_evidence["evidence"] == [
        {
            "section": "work_experience",
            "text": "Worked with REST APIs in production.",
        }
    ]


def test_all_exact_skill_matches_do_not_load_semantic_model(monkeypatch):
    monkeypatch.setattr(
        skill_matching,
        "get_semantic_model",
        lambda: (_ for _ in ()).throw(
            AssertionError("embedding model should not load")
        ),
    )

    results = skill_matching.calculate_semantic_skill_matches(
        ["Python", "REST APIs", "Git"],
        ["Python", "REST API", "Git"],
    )

    assert len(results) == 3
    assert all(item["classification"] == "HIGH" for item in results)
    assert all(item["similarity"] == 1.0 for item in results)


def test_standard_resume_jd_flow_recovers_rest_apis_and_avoids_false_gap(
    monkeypatch,
):
    """Regression test for REST APIs matching and Docker evidence review."""
    monkeypatch.setattr(
        model_skill_extractor,
        "extract_skills_with_gliner",
        lambda text, threshold=0.30: [
            "Python", "Django", "MySQL", "Git", "Docker"
        ],
    )
    monkeypatch.setattr(
        jd_skill_extractor,
        "extract_skills_with_gliner",
        lambda text: [],
    )
    monkeypatch.setattr(
        skill_matching,
        "get_semantic_model",
        lambda: (_ for _ in ()).throw(
            AssertionError(
                "exactly covered JD should not load the semantic model"
            )
        ),
    )

    resume_bytes = make_resume_pdf(
        "RAHUL SHARMA\n"
        "Technical Skills\nPython, Django, MySQL, Git, Docker\n"
        "Work Experience\nWorked with Git and REST APIs.\n"
        "Projects\nBuilt a Django application with MySQL."
    )
    jd_text = (
        "Job Title: Python Backend Developer\n"
        "Required Skills:\n"
        "1. Python\n2. Django\n3. REST APIs\n4. MySQL\n5. Git\n6. Docker\n"
        "Responsibilities:\nDevelop backend applications using Python and Django.\n"
        "Qualifications:\nGood problem-solving skills."
    )

    response = client.post(
        "/api/skill-gap/analyze",
        files={"file": ("resume.pdf", BytesIO(resume_bytes), "application/pdf")},
        data={"job_description": jd_text},
    )

    assert response.status_code == 200, response.text
    body = response.json()

    expected = {"Python", "Django", "REST APIs", "MySQL", "Git", "Docker"}
    assert set(body["required_skills"]) == expected
    assert expected.issubset(set(body["claimed_skills"]))

    # All required skills are claimed, so there is no claim-based missing skill.
    assert body["skill_gap"]["total_matched"] == 6
    assert body["skill_gap"]["total_missing"] == 0

    # Docker is claimed but has no supporting evidence in the resume.
    assert body["initial_analysis"]["status"] == "EVIDENCE_REVIEW"
    assert "Docker" in body["initial_analysis"]["evidence_gaps"]
    assert (
        body["candidate_feedback"]["next_step"] == "PERSONALIZED_INTERVIEW"
    )

    docker_match = next(
        item
        for item in body["skill_gap"]["semantic_matches"]
        if item["required_skill"] == "Docker"
    )
    assert docker_match["classification"] == "HIGH"
    assert docker_match["evidence_found"] is False
    assert docker_match["status"] == "Claimed; evidence not found"

    rest_match = next(
        item
        for item in body["skill_gap"]["semantic_matches"]
        if item["required_skill"] == "REST APIs"
    )
    assert rest_match["evidence_found"] is True

    rest_evidence = next(
        item for item in body["skill_evidence"] if item["skill"] == "REST APIs"
    )
    assert any(
        evidence["section"] == "work_experience"
        and "REST APIs" in evidence["text"]
        for evidence in rest_evidence["evidence"]
    )


def test_m04_marks_exact_claim_without_supporting_evidence():
    gap = skill_matching.calculate_skill_gap(
        [{"skill": "Docker"}, {"skill": "Python"}],
        ["Docker", "Python"],
        [
            {"skill": "Docker", "evidence": []},
            {
                "skill": "Python",
                "evidence": [
                    {
                        "section": "work_experience",
                        "text": "Used Python to build a service.",
                    }
                ],
            },
        ],
    )

    matches = {
        item["required_skill"]: item for item in gap["semantic_matches"]
    }
    assert gap["total_matched"] == 2
    assert matches["Docker"]["classification"] == "HIGH"
    assert matches["Docker"]["evidence_found"] is False
    assert matches["Docker"]["status"] == "Claimed; evidence not found"
    assert matches["Python"]["evidence_found"] is True
    assert matches["Python"]["status"] == "Well claimed"
