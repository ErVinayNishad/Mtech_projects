def build_resume_profile(sections, claimed_skills=None):
    """
    Convert extracted resume sections into a structured
    resume profile.
    """

    profile = {
        "personal_details": [],
        "career_objective": [],
        "education": [],
        "work_experience": [],
        "projects": [],
        "technical_skills": [],
        "claimed_skills": [],
        "certifications": [],
        "achievements": [],
        "areas_of_interest": [],
        "hobbies_interests": [],
        "languages": []
    }

    # -----------------------------
    # Copy extracted sections
    # -----------------------------

    for section in profile:

        if section == "claimed_skills":
            continue

        profile[section] = sections.get(section, [])

    # -----------------------------
    # Add structured claimed skills
    # -----------------------------

    if claimed_skills:
        profile["claimed_skills"] = claimed_skills

    return profile