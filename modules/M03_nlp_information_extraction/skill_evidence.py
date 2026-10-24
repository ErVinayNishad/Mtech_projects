
import re


def normalize_evidence_skill(skill):
    """Normalize a skill for case-insensitive comparison."""
    if not isinstance(skill, str):
        return ""

    return re.sub(r"\s+", " ", skill.strip()).casefold()


def skill_appears_in_text(skill, text):
    """Match complete skill names without matching partial names."""
    if not isinstance(skill, str) or not isinstance(text, str):
        return False

    skill = skill.strip()

    if not skill:
        return False

    escaped_skill = re.escape(skill)

    # C must not match C++, C#, or words beginning with C.
    if skill.casefold() == "c":
        pattern = r"(?<!\w)c(?![\w+#])"
    else:
        pattern = rf"(?<!\w){escaped_skill}(?!\w)"

    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_skill_evidence(sections, claimed_skills):
    """
    Find direct evidence for claimed skills in relevant resume sections.

    Skills listed only under technical_skills are claims, not evidence
    of practical use. Evidence is searched in experience, projects,
    certifications, and career objective.
    """

    if not isinstance(sections, dict):
        sections = {}

    if not isinstance(claimed_skills, (list, tuple)):
        claimed_skills = []

    evidence_sections = (
        "work_experience",
        "projects",
        "certifications",
        "career_objective",
    )

    evidence_lines = []

    for section_name in evidence_sections:
        lines = sections.get(section_name, [])

        if isinstance(lines, str):
            lines = [lines]

        if not isinstance(lines, (list, tuple)):
            continue

        for line in lines:
            if isinstance(line, str) and line.strip():
                evidence_lines.append({
                    "section": section_name,
                    "text": line.strip(),
                })

    skill_evidence = []

    for item in claimed_skills:
        if not isinstance(item, dict):
            continue

        skill = item.get("skill")

        if not isinstance(skill, str) or not skill.strip():
            continue

        evidence = []
        seen = set()

        for line_data in evidence_lines:
            if not skill_appears_in_text(
                skill,
                line_data["text"],
            ):
                continue

            evidence_key = (
                line_data["section"],
                line_data["text"].casefold(),
            )

            if evidence_key in seen:
                continue

            seen.add(evidence_key)

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
