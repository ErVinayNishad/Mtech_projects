from app.services.jd_skill_extractor import extract_required_skills


# -----------------------------
# SAMPLE JOB DESCRIPTION
# -----------------------------

job_description = """
We are looking for a Python Developer.

The candidate should have strong knowledge of Python,
Django, REST APIs, SQL, MongoDB and Git.

Experience with AWS and Docker is preferred.
Knowledge of JavaScript and React is an advantage.
"""


# -----------------------------
# REQUIRED SKILL EXTRACTION
# -----------------------------

required_skills = extract_required_skills(
    job_description
)


print("----- REQUIRED JD SKILLS -----")

for skill in required_skills:
    print(skill)