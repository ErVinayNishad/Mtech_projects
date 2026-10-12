from app.services.resume.model_skill_extractor import (
    extract_skills_with_gliner
)


# ============================================================
# NON-SKILL TERMS
# ============================================================

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


# ============================================================
# EXTRACT REQUIRED SKILLS
# ============================================================

def extract_required_skills(job_description):

    if not job_description:
        return []

    extracted_skills = extract_skills_with_gliner(
        job_description
    )

    required_skills = []

    for skill in extracted_skills:

        if skill.lower() in NON_SKILL_TERMS:
            continue

        if skill not in required_skills:
            required_skills.append(skill)

    required_skills.sort(
        key=lambda x: x.lower()
    )

    return required_skills