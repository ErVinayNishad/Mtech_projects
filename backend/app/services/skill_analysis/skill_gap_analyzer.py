# ============================================================
# INITIAL SKILL GAP ANALYZER
# ============================================================


# ============================================================
# SKILL NORMALIZATION
# ============================================================

SKILL_ALIASES = {

    "rest api": "rest api",
    "rest apis": "rest api",

    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",

    "express": "express.js",
    "expressjs": "express.js",
    "express.js": "express.js",

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
}


def normalize_skill(skill):
    """
    Convert different names of the same skill
    into a common comparison form.
    """

    if not skill:
        return ""

    skill = skill.strip().lower()

    return SKILL_ALIASES.get(
        skill,
        skill
    )


# ============================================================
# INITIAL SKILL GAP ANALYZER
# ============================================================

def analyze_skill_gap(
    required_skills,
    claimed_skills
):
    """
    Compare job-required skills with
    resume-claimed skills.

    Returns:
    - matched skills
    - missing skills
    - skill gap percentage
    """

    # --------------------------------------------------------
    # Normalize required skills
    # --------------------------------------------------------

    required = {}

    for skill in required_skills:

        if not skill:
            continue

        original_skill = skill.strip()

        if not original_skill:
            continue

        normalized = normalize_skill(
            original_skill
        )

        required[normalized] = original_skill

    # --------------------------------------------------------
    # Normalize claimed skills
    # --------------------------------------------------------

    claimed = {}

    for item in claimed_skills:

        skill = item.get("skill")

        if not skill:
            continue

        original_skill = skill.strip()

        if not original_skill:
            continue

        normalized = normalize_skill(
            original_skill
        )

        claimed[normalized] = original_skill

    # --------------------------------------------------------
    # Find matched and missing skills
    # --------------------------------------------------------

    matched_skills = []
    missing_skills = []

    for normalized_skill, original_skill in required.items():

        if normalized_skill in claimed:

            matched_skills.append(
                original_skill
            )

        else:

            missing_skills.append(
                original_skill
            )

    # --------------------------------------------------------
    # Calculate gap percentage
    # --------------------------------------------------------

    total_required = len(required)

    if total_required == 0:

        gap_percentage = 0.0

    else:

        gap_percentage = (
            len(missing_skills)
            / total_required
        ) * 100

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {

        "required_skills":
            list(required.values()),

        "claimed_skills":
            list(claimed.values()),

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "total_required_skills":
            total_required,

        "total_matched_skills":
            len(matched_skills),

        "total_missing_skills":
            len(missing_skills),

        "skill_gap_percentage":
            round(
                gap_percentage,
                2
            )
    }