# ============================================================
# BUILD STRUCTURED RESUME PROFILE
# ============================================================

def build_resume_profile(
    sections,
    claimed_skills=None
):
    """
    Convert extracted resume sections into a structured
    resume profile.

    Parameters:
    - sections:
        Dictionary containing extracted resume sections.

    - claimed_skills:
        Structured skills extracted from the resume.

    Returns:
    - Dictionary containing the complete resume profile.
    """

    # --------------------------------------------------------
    # Initialize profile structure
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Copy extracted sections
    # --------------------------------------------------------

    if sections is None:
        sections = {}

    for section in profile:

        # claimed_skills is handled separately
        if section == "claimed_skills":
            continue

        profile[section] = sections.get(
            section,
            []
        )

    # --------------------------------------------------------
    # Add structured claimed skills
    # --------------------------------------------------------

    if claimed_skills is not None:

        profile["claimed_skills"] = claimed_skills

    # --------------------------------------------------------
    # Return final profile
    # --------------------------------------------------------

    return profile