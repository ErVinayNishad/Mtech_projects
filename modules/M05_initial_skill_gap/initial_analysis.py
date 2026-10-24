
def analyze_skill_gap(skill_gap):
    """Analyze claimed skill gaps and missing evidence from M04."""

    if not isinstance(skill_gap, dict):
        skill_gap = {}

    matched_skills = skill_gap.get("matched_skills", [])
    exact_missing_skills = skill_gap.get("missing_skills", [])
    semantic_matches = skill_gap.get("semantic_matches", [])

    if not isinstance(matched_skills, list):
        matched_skills = []
    if not isinstance(exact_missing_skills, list):
        exact_missing_skills = []
    if not isinstance(semantic_matches, list):
        semantic_matches = []

    total_required = skill_gap.get(
        "total_required",
        skill_gap.get(
            "total_required_skills",
            len(matched_skills) + len(exact_missing_skills),
        ),
    )

    if (
        isinstance(total_required, bool)
        or not isinstance(total_required, int)
        or total_required <= 0
    ):
        return {
            "status": "NO_DATA",
            "gap_percentage": 0.0,
            "matched_skills": matched_skills,
            "missing_skills": [],
            "exact_missing_skills": exact_missing_skills,
            "semantic_matches": semantic_matches,
            "semantic_gaps": [],
            "evidence_gaps": [],
            "message": "No required skills found in the job description.",
        }

    semantic_gaps = [
        item["required_skill"]
        for item in semantic_matches
        if isinstance(item, dict)
        and item.get("classification") == "LOW"
        and isinstance(item.get("required_skill"), str)
        and item["required_skill"].strip()
    ]

    evidence_gaps = [
        item["required_skill"]
        for item in semantic_matches
        if isinstance(item, dict)
        and item.get("evidence_found") is False
        and isinstance(item.get("required_skill"), str)
        and item["required_skill"].strip()
    ]

    if semantic_matches:
        unresolved_skills = semantic_gaps
    else:
        unresolved_skills = exact_missing_skills

    gap_percentage = len(unresolved_skills) / total_required * 100

    if unresolved_skills:
        status = "GAP_FOUND"
        message = (
            "Potential skill gaps detected. "
            "Candidate feedback should be generated."
        )
    elif evidence_gaps:
        status = "EVIDENCE_REVIEW"
        message = (
            "Some skills are claimed but supporting evidence was not found. "
            "Verify these skills during the personalized interview."
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
        "missing_skills": unresolved_skills,
        "exact_missing_skills": exact_missing_skills,
        "semantic_matches": semantic_matches,
        "semantic_gaps": semantic_gaps,
        "evidence_gaps": evidence_gaps,
        "message": message,
    }
