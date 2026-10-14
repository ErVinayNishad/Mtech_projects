
# ============================================================
# BUILD STRUCTURED RESUME PROFILE
# ============================================================

def build_resume_profile(
    sections,
    claimed_skills=None,
    skill_evidence=None,
):
    """
    Build a structured resume profile containing:
    - Extracted resume sections
    - Claimed skills
    - Evidence found for claimed skills
    """

    profile = {
        "personal_details": [],
        "career_objective": [],
        "education": [],
        "work_experience": [],
        "projects": [],
        "technical_skills": [],
        "claimed_skills": [],
        "skill_evidence": [],
        "certifications": [],
        "achievements": [],
        "areas_of_interest": [],
        "hobbies_interests": [],
        "languages": [],
    }

    if not isinstance(sections, dict):
        sections = {}

    # Copy available extracted sections.
    for section_name in profile:
        if section_name in ("claimed_skills", "skill_evidence"):
            continue

        content = sections.get(section_name, [])
        profile[section_name] = content if content is not None else []

    # Store claimed skills separately from evidence.
    if isinstance(claimed_skills, (list, tuple)):
        profile["claimed_skills"] = list(claimed_skills)

    if isinstance(skill_evidence, (list, tuple)):
        profile["skill_evidence"] = list(skill_evidence)

    return profile
