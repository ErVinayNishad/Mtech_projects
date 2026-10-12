from app.services.skill_analysis.skill_gap_analyzer import analyze_skill_gap


# ============================================================
# SAMPLE JOB REQUIRED SKILLS
# ============================================================

required_skills = [
    "Python",
    "Django",
    "React",
    "Docker",
    "AWS"
]


# ============================================================
# SAMPLE RESUME CLAIMED SKILLS
# ============================================================

claimed_skills = [
    {"skill": "Python"},
    {"skill": "Django"},
    {"skill": "React"},
    {"skill": "AWS"}
]


# ============================================================
# ANALYZE SKILL GAP
# ============================================================

result = analyze_skill_gap(
    required_skills,
    claimed_skills
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n----- INITIAL SKILL GAP ANALYSIS -----")

print("\nRequired Skills:")
for skill in result["required_skills"]:
    print(skill)

print("\nClaimed Skills:")
for skill in result["claimed_skills"]:
    print(skill)

print("\nMatched Skills:")
for skill in result["matched_skills"]:
    print(skill)

print("\nMissing Skills:")
for skill in result["missing_skills"]:
    print(skill)

print(
    "\nTotal Required:",
    result["total_required_skills"]
)

print(
    "Total Matched:",
    result["total_matched_skills"]
)

print(
    "Total Missing:",
    result["total_missing_skills"]
)

print(
    "Skill Gap:",
    result["skill_gap_percentage"],
    "%"
)