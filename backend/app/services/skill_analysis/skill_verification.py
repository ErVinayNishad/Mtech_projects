
# ============================================================
# RESUME EVIDENCE ASSESSMENT
# ============================================================

def verify_claimed_skills(skill_evidence):
    """
    Assess resume evidence for skills explicitly marked as claimed.
    This does not verify actual skill proficiency.
    """

    if not isinstance(skill_evidence, (list, tuple)):
        skill_evidence = []

    skills_with_evidence = []
    skills_without_evidence = []

    for item in skill_evidence:
        if not isinstance(item, dict):
            continue

        # Ignore skills that are not explicitly claimed.
        if item.get("claimed") is not True:
            continue

        skill = item.get("skill")

        if not isinstance(skill, str) or not skill.strip():
            continue

        skill = skill.strip()

        evidence = item.get("evidence", [])
        if not isinstance(evidence, list):
            evidence = []

        result = {
            "skill": skill,
            "evidence": evidence,
            "resume_evidence_found": bool(evidence),
        }

        if evidence:
            skills_with_evidence.append(result)
        else:
            skills_without_evidence.append(result)

    total = len(skills_with_evidence) + len(skills_without_evidence)
    with_evidence = len(skills_with_evidence)

    return {
        "skills_with_resume_evidence": skills_with_evidence,
        "skills_without_resume_evidence": skills_without_evidence,
        "total_claimed_skills": total,
        "total_with_evidence": with_evidence,
        "total_without_evidence": len(skills_without_evidence),
        "resume_evidence_coverage_percentage": round(
            (with_evidence / total * 100) if total else 0.0,
            2,
        ),
    }
