
from pathlib import Path

import pytest

from app.services.resume.resume_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    extract_sections,
    extract_personal_details,
)
from app.services.resume.model_skill_extractor import (
    get_claimed_skills_with_gliner,
    extract_skills_with_gliner,
)
from app.services.resume.skill_extractor import extract_skills
from app.services.resume.skill_evidence import extract_skill_evidence
from app.services.resume.resume_profile import build_resume_profile


UPLOADS_DIR = Path(__file__).parent / "uploads"
PDF_PATH = UPLOADS_DIR / "resume1.pdf"
DOCX_PATH = UPLOADS_DIR / "resume1.docx"


def process_resume(file_path, file_type):
    if file_type.lower() == "pdf":
        text = extract_text_from_pdf(str(file_path))
    elif file_type.lower() == "docx":
        text = extract_text_from_docx(str(file_path))
    else:
        raise ValueError("Unsupported resume format")

    text = clean_text(text)

    if not isinstance(text, str) or not text.strip():
        return None

    sections = extract_sections(text)
    personal_details = extract_personal_details(text)

    sections["personal_details"] = [
        f"{key}: {value}"
        for key, value in personal_details.items()
        if value
    ]

    technical_skills_text = "\n".join(
        sections.get("technical_skills", [])
    )

    claimed_skill_data = get_claimed_skills_with_gliner(
        technical_skills_text
    )

    rule_based_skills = extract_skills(technical_skills_text)

    other_sections_text = "\n".join(
        line
        for section_name, lines in sections.items()
        if section_name != "technical_skills"
        and isinstance(lines, (list, tuple))
        for line in lines
        if isinstance(line, str)
    )

    additional_skill_mentions = extract_skills_with_gliner(
        other_sections_text
    )

    skill_evidence = extract_skill_evidence(
        sections,
        claimed_skill_data,
    )

    resume_profile = build_resume_profile(
        sections,
        claimed_skill_data,
        skill_evidence,
    )

    return {
        "sections": sections,
        "claimed_skills": claimed_skill_data,
        "rule_based_skills": rule_based_skills,
        "additional_skill_mentions": additional_skill_mentions,
        "skill_evidence": skill_evidence,
        "resume_profile": resume_profile,
    }


def test_pdf_resume_processing():
    assert PDF_PATH.is_file()

    result = process_resume(PDF_PATH, "pdf")

    assert result is not None
    assert isinstance(result["sections"], dict)
    assert isinstance(result["claimed_skills"], list)
    assert isinstance(result["skill_evidence"], list)
    assert isinstance(result["resume_profile"], dict)


def test_docx_resume_processing():
    assert DOCX_PATH.is_file()

    result = process_resume(DOCX_PATH, "docx")

    assert result is not None
    assert isinstance(result["sections"], dict)
    assert isinstance(result["claimed_skills"], list)
    assert isinstance(result["skill_evidence"], list)
    assert isinstance(result["resume_profile"], dict)


def test_unsupported_resume_format():
    with pytest.raises(ValueError, match="Unsupported resume format"):
        process_resume("sample.txt", "txt")


def test_clean_text_returns_string():
    result = clean_text("  Python   Django  ")

    assert isinstance(result, str)
    assert result.strip()


def test_extract_sections_returns_dictionary():
    result = extract_sections(
        "Technical Skills\nPython\nDjango\nProjects\nBuilt a web application."
    )

    assert isinstance(result, dict)


def test_skill_evidence_matches_claimed_skills():
    sections = {
        "technical_skills": ["Python", "Docker"],
        "work_experience": ["Developed applications using Python."],
        "projects": [],
    }
    claimed_skills = [
        {
            "skill": "Python",
            "claimed": True,
            "section": "technical_skills",
            "extraction_method": "GLiNER",
        },
        {
            "skill": "Docker",
            "claimed": True,
            "section": "technical_skills",
            "extraction_method": "GLiNER",
        },
    ]

    result = extract_skill_evidence(sections, claimed_skills)

    assert isinstance(result, list)
    assert len(result) == 2
    assert {item["skill"] for item in result} == {"Python", "Docker"}
