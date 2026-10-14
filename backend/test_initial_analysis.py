from app.services.skill_analysis.initial_analysis import analyze_skill_gap


# -----------------------------
# SAMPLE INITIAL SKILL GAP
# -----------------------------

skill_gap = {
    "matched_skills": [
        "aws",
        "javascript",
        "mongodb",
        "python",
        "react",
        "sql"
    ],
    "missing_skills": [
        "c",
        "django",
        "docker",
        "git",
        "java"
    ],
    "total_required_skills": 11,
    "total_matched_skills": 6,
    "total_missing_skills": 5
}


# -----------------------------
# INITIAL ANALYSIS
# -----------------------------

analysis = analyze_skill_gap(skill_gap)


print("----- INITIAL ANALYSIS -----")

print("\nStatus:")
print(analysis["status"])

print("\nGap Percentage:")
print(analysis["gap_percentage"], "%")

print("\nMatched Skills:")
for skill in analysis["matched_skills"]:
    print(skill)

print("\nMissing Skills:")
for skill in analysis["missing_skills"]:
    print(skill)

print("\nDecision:")
print(analysis["message"])
