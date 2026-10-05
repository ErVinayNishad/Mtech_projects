def analyze_skill_gap(skill_gap):
    """
    Analyze the initial skill gap and determine
    whether the candidate should receive feedback
    or proceed to the interview phase.
    """

    matched_skills = skill_gap.get("matched_skills", [])
    missing_skills = skill_gap.get("missing_skills", [])
    total_required = skill_gap.get("total_required_skills", 0)

    # Avoid division by zero
    if total_required == 0:
        return {
            "status": "NO_DATA",
            "gap_percentage": 0,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "message": "No required skills found in the job description."
        }

    # Calculate gap percentage
    gap_percentage = (
        len(missing_skills) / total_required
    ) * 100

    # Decision
    if len(missing_skills) > 0:
        status = "GAP_FOUND"
        message = (
            "Skill gap detected. "
            "Candidate feedback should be generated."
        )
    else:
        status = "NO_GAP"
        message = (
            "No initial skill gap detected. "
            "Candidate can proceed to personalized interview."
        )

    return {
        "status": status,
        "gap_percentage": round(gap_percentage, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "message": message
    }