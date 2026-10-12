# ============================================================
# SKILL VERIFICATION
# ============================================================

def verify_claimed_skills(
    skill_evidence
):
    """
    Verify resume-claimed skills based on
    available resume evidence.

    A skill is considered:
    - verified      -> evidence found
    - unverified    -> no evidence found
    """

    verified_skills = []
    unverified_skills = []

    for item in skill_evidence:

        skill = item["skill"]

        evidence = item.get(
            "evidence",
            []
        )

        if evidence:

            verified_skills.append({
                "skill": skill,
                "verified": True,
                "evidence": evidence
            })

        else:

            unverified_skills.append({
                "skill": skill,
                "verified": False,
                "evidence": []
            })

    total_claimed = (
        len(verified_skills)
        + len(unverified_skills)
    )

    if total_claimed == 0:
        verification_percentage = 0.0
    else:
        verification_percentage = (
            len(verified_skills)
            / total_claimed
        ) * 100

    return {
        "verified_skills": verified_skills,
        "unverified_skills": unverified_skills,
        "total_claimed_skills": total_claimed,
        "total_verified_skills": len(
            verified_skills
        ),
        "total_unverified_skills": len(
            unverified_skills
        ),
        "verification_percentage": round(
            verification_percentage,
            2
        )
    }