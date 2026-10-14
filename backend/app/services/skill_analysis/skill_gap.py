
# ============================================================
# SKILL GAP CALCULATION
# ============================================================

SKILL_ALIASES = {
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "express": "express.js",
    "expressjs": "express.js",
    "express.js": "express.js",
    "react.js": "react",
    "reactjs": "react",
    "react": "react",
    "javascript": "javascript",
    "python": "python",
    "django": "django",
    "mongodb": "mongodb",
    "mysql": "mysql",
    "aws": "aws",
    "docker": "docker",
    "git": "git",
    "github": "github",
    "rest api": "rest api",
    "rest apis": "rest api",
}


def normalize_skill(skill):
    if not isinstance(skill, str):
        return ""

    skill = " ".join(skill.strip().casefold().split())

    if not skill:
        return ""

    return SKILL_ALIASES.get(skill, skill)


def calculate_skill_gap(claimed_skills, required_skills):
    if not isinstance(claimed_skills, (list, tuple)):
        claimed_skills = []

    if not isinstance(required_skills, (list, tuple)):
        required_skills = []

    claimed = {}
    for skill in claimed_skills:
        if isinstance(skill, dict):
            skill = skill.get("skill")

        normalized = normalize_skill(skill)
        if normalized:
            claimed.setdefault(normalized, skill.strip())

    required = {}
    for skill in required_skills:
        normalized = normalize_skill(skill)
        if normalized:
            required.setdefault(normalized, skill.strip())

    matched_keys = required.keys() & claimed.keys()
    missing_keys = required.keys() - claimed.keys()

    matched_skills = sorted(required[key] for key in matched_keys)
    missing_skills = sorted(required[key] for key in missing_keys)

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_required": len(required),
        "total_matched": len(matched_skills),
        "total_missing": len(missing_skills),
    }
