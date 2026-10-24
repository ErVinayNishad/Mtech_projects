
SKILL_LEARNING_SUGGESTIONS = {
    "python": "Practice Python fundamentals, functions, OOP, and small projects.",
    "django": "Learn Django models, views, URLs, templates, and REST API development.",
    "docker": "Practice Docker images, containers, Dockerfiles, and container networking.",
    "git": "Practice Git commits, branches, merges, and conflict resolution.",
    "java": "Study Java fundamentals, OOP, collections, and exception handling.",
    "sql": "Practice SQL queries, joins, grouping, and database design.",
    "aws": "Learn core AWS services and deploy a small application.",
    "javascript": "Practice JavaScript fundamentals, asynchronous code, and DOM operations.",
    "react": "Practice React components, props, state, hooks, and API integration.",
    "mongodb": "Practice MongoDB CRUD operations, queries, indexes, and schema design.",
}


def generate_candidate_feedback(analysis):
    if not isinstance(analysis, dict):
        analysis = {}

    status = analysis.get("status", "NO_DATA")
    matched_skills = analysis.get("matched_skills", [])
    missing_skills = analysis.get("missing_skills", [])
    evidence_gaps = analysis.get("evidence_gaps", [])

    if not isinstance(matched_skills, list):
        matched_skills = []

    if not isinstance(missing_skills, list):
        missing_skills = []

    if not isinstance(evidence_gaps, list):
        evidence_gaps = []

    learning_suggestions = []

    for skill in missing_skills:
        if not isinstance(skill, str) or not skill.strip():
            continue

        normalized_skill = skill.strip().casefold()
        suggestion = SKILL_LEARNING_SUGGESTIONS.get(
            normalized_skill,
            f"Study {skill}, practice it with hands-on exercises, and build a small project.",
        )
        learning_suggestions.append({
            "skill": skill,
            "suggestion": suggestion,
        })

    if status == "GAP_FOUND":
        return {
            "status": status,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "gap_percentage": analysis.get("gap_percentage", 0.0),
            "learning_suggestions": learning_suggestions,
            "next_step": "CANDIDATE_FEEDBACK",
            "message": (
                "Some required skills were not identified in the resume. "
                "Review the suggestions to improve your profile."
            ),
        }

    if status in ("NO_GAP", "EVIDENCE_REVIEW"):
        if status == "EVIDENCE_REVIEW":
            message = (
                "Required skills were identified, but some claims lack supporting "
                "resume evidence. Verify these skills during the personalized interview."
            )
        else:
            message = (
                "No initial skill gap was detected. "
                "Proceed to the personalized interview for further assessment."
            )

        return {
            "status": status,
            "matched_skills": matched_skills,
            "missing_skills": [],
            "evidence_gaps": evidence_gaps,
            "gap_percentage": analysis.get("gap_percentage", 0.0),
            "learning_suggestions": [],
            "next_step": "PERSONALIZED_INTERVIEW",
            "message": message,
        }

    return {
        "status": "NO_DATA",
        "matched_skills": matched_skills,
        "missing_skills": [],
        "evidence_gaps": [],
        "gap_percentage": 0.0,
        "learning_suggestions": [],
        "next_step": "PROVIDE_VALID_JOB_DESCRIPTION",
        "message": "Required job skills were not available for analysis.",
    }
