
def analyze_skill_gap(skill_gap):
    """
    Analyze the initial skill gap and decide the next stage.
    """

    if not isinstance(skill_gap, dict):
        skill_gap = {}

    matched_skills = skill_gap.get("matched_skills", [])
    missing_skills = skill_gap.get("missing_skills", [])

    total_required = skill_gap.get(
        "total_required_skills",
        skill_gap.get(
            "total_required",
            len(matched_skills) + len(missing_skills),
        ),
    )

    if not isinstance(matched_skills, list):
        matched_skills = []

    if not isinstance(missing_skills, list):
        missing_skills = []

    if not isinstance(total_required, int) or total_required <= 0:
        return {
            "status": "NO_DATA",
            "gap_percentage": 0.0,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "message": "No required skills found in the job description.",
        }

    gap_percentage = len(missing_skills) / total_required * 100

    if missing_skills:
        status = "GAP_FOUND"
        message = "Skill gap detected. Candidate feedback should be generated."
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
        "message": message,
    }
