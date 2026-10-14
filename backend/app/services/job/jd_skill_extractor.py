
import re

from app.services.resume.model_skill_extractor import (
    extract_skills_with_gliner,
)


NON_SKILL_TERMS = {
    "experience",
    "knowledge",
    "developer",
    "software developer",
    "candidate",
    "strong",
    "preferred",
    "required",
    "requirements",
    "skills",
    "skill",
    "work",
    "development",
}


def extract_required_skills(text):
    """
    Extract required skills from a job description using GLiNER.
    Normalize whitespace, remove non-skill terms and duplicates,
    and return a sorted list of skills.
    """

    if not isinstance(text, str) or not text.strip():
        return []

    extracted_skills = extract_skills_with_gliner(text)

    unique_skills = {}

    for skill in extracted_skills:
        if not isinstance(skill, str) or not skill.strip():
            continue

        skill = re.sub(r"\s+", " ", skill.strip())

        if skill.casefold() in NON_SKILL_TERMS:
            continue

        unique_skills.setdefault(skill.casefold(), skill)

    return sorted(unique_skills.values(), key=str.casefold)
