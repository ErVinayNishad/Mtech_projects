from app.services.skill_analysis.skill_verification import (
    verify_claimed_skills
)

# ============================================================
# TEST SKILL VERIFICATION
# ============================================================

skill_evidence = [

    {
        "skill": "Python",
        "claimed": True,
        "evidence": [
            {
                "section": "work_experience",
                "text": "Developed web applications using Python, Django and SQL."
            }
        ]
    },

    {
        "skill": "Django",
        "claimed": True,
        "evidence": [
            {
                "section": "work_experience",
                "text": "Developed web applications using Python, Django and SQL."
            }
        ]
    },

    {
        "skill": "React",
        "claimed": True,
        "evidence": [
            {
                "section": "projects",
                "text": "Built a React and Node.js application with MongoDB."
            }
        ]
    },

    {
        "skill": "Docker",
        "claimed": True,
        "evidence": []
    },

    {
        "skill": "AWS",
        "claimed": True,
        "evidence": [
            {
                "section": "certifications",
                "text": "AWS Cloud Fundamentals Certification"
            }
        ]
    }
]


# ============================================================
# RUN VERIFICATION
# ============================================================

result = verify_claimed_skills(
    skill_evidence
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n----- SKILL VERIFICATION -----\n")

print("Verified Skills:")

for item in result["verified_skills"]:

    print(
        item["skill"]
    )


print("\nUnverified Skills:")

for item in result["unverified_skills"]:

    print(
        item["skill"]
    )


print(
    "\nTotal Claimed:",
    result["total_claimed_skills"]
)

print(
    "Total Verified:",
    result["total_verified_skills"]
)

print(
    "Total Unverified:",
    result["total_unverified_skills"]
)

print(
    "Verification Percentage:",
    result["verification_percentage"],
    "%"
)