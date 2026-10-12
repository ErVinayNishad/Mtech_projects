import re

from app.services.resume.model_skill_extractor import (
    extract_skills_with_gliner,
)


def normalize_evidence_skill(skill):
    """Normalize a skill for case-insensitive comparison."""
    return re.sub(r"\s+", " ", skill.strip()).casefold()


def skill_appears_in_text(skill, text):
    """Check direct skill mentions without matching partial skill names."""
    skill = skill.strip()

    if not skill:
        return False

    escaped_skill = re.escape(skill)

    # Prevent C from matching C++ or C#.
    if skill.casefold() == "c":
        pattern = r"(?<!\w)c(?![\w+#])"
    else:
        pattern = rf"(?<!\w){escaped_skill}(?!\w)"

    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_skill_evidence(sections, claimed_skills):
    """
    Find evidence for claimed skills in selected resume sections.

    GLiNER processes each valid resume line once.
    Direct text matching supplements model detection.
    """

    evidence_sections = [
        "work_experience",
        "projects",
        "certifications",
        "career_objective",
    ]

    detected_lines = []

    # Process each resume line once.
    for section_name in evidence_sections:
        lines = sections.get(section_name, [])

        if isinstance(lines, str):
            lines = [lines]

        if not isinstance(lines, (list, tuple)):
            continue

        for line in lines:
            if not isinstance(line, str) or not line.strip():
                continue

            detected_skills = extract_skills_with_gliner(line)

            normalized_skills = {
                normalize_evidence_skill(skill)
                for skill in detected_skills
                if isinstance(skill, str) and skill.strip()
            }

            detected_lines.append({
                "section": section_name,
                "text": line,
                "skills": normalized_skills,
            })

    skill_evidence = []

    # Match each claimed skill against the processed lines.
    for item in claimed_skills:
        if not isinstance(item, dict):
            continue

        skill = item.get("skill")

        if not isinstance(skill, str) or not skill.strip():
            continue

        skill_key = normalize_evidence_skill(skill)
        evidence = []
        seen_evidence = set()

        for line_data in detected_lines:
            model_match = skill_key in line_data["skills"]

            direct_match = skill_appears_in_text(
                skill,
                line_data["text"],
            )

            if model_match or direct_match:
                evidence_key = (
                    line_data["section"],
                    line_data["text"].strip().casefold(),
                )

                if evidence_key in seen_evidence:
                    continue

                seen_evidence.add(evidence_key)

                evidence.append({
                    "section": line_data["section"],
                    "text": line_data["text"],
                })

        skill_evidence.append({
            "skill": skill,
            "claimed": True,
            "evidence": evidence,
        })

    return skill_evidence
