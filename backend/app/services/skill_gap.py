# app/services/skill_gap.py


def calculate_skill_gap(claimed_skills, required_skills):

    claimed_set = {
        skill.lower().strip()
        for skill in claimed_skills
    }

    required_set = {
        skill.lower().strip()
        for skill in required_skills
    }

    matched_skills = required_set.intersection(claimed_set)

    missing_skills = required_set - claimed_set

    return {
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "total_required": len(required_set),
        "total_matched": len(matched_skills),
        "total_missing": len(missing_skills)
    }