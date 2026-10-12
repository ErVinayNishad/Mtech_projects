from app.services.resume.resume_parser import (
    extract_text_from_pdf,
    clean_text,
    extract_sections
)

from app.services.resume.skill_extractor import (
    get_claimed_skills
)

from app.services.jd_skill_extractor import (
    extract_required_skills
)

from app.services.skill_gap import (
    calculate_skill_gap
)


# ---------------------------------
# 1. EXTRACT RESUME TEXT
# ---------------------------------

pdf_text = extract_text_from_pdf(
    "uploads/resume1.pdf"
)

pdf_text = clean_text(pdf_text)


# ---------------------------------
# 2. EXTRACT RESUME SECTIONS
# ---------------------------------

pdf_sections = extract_sections(pdf_text)


# ---------------------------------
# 3. GET RESUME TECHNICAL SKILLS
# ---------------------------------

technical_skills_text = "\n".join(
    pdf_sections.get("technical_skills", [])
)


# ---------------------------------
# 4. GET CLAIMED SKILLS
# ---------------------------------

claimed_skill_data = get_claimed_skills(
    technical_skills_text
)

claimed_skills = [
    item["skill"]
    for item in claimed_skill_data
]


print("----- RESUME CLAIMED SKILLS -----")

for skill in claimed_skills:
    print(skill)


# ---------------------------------
# 5. SAMPLE JOB DESCRIPTION
# ---------------------------------

job_description = """
We are looking for a Python Developer.

The candidate should have strong knowledge of Python,
Django, REST APIs, SQL, MongoDB and Git.

Experience with AWS and Docker is preferred.
Knowledge of JavaScript and React is an advantage.
"""


# ---------------------------------
# 6. EXTRACT REQUIRED JD SKILLS
# ---------------------------------

required_skills = extract_required_skills(
    job_description
)


print("\n----- JD REQUIRED SKILLS -----")

for skill in required_skills:
    print(skill)


# ---------------------------------
# 7. CALCULATE INITIAL SKILL GAP
# ---------------------------------

result = calculate_skill_gap(
    claimed_skills,
    required_skills
)


# ---------------------------------
# 8. DISPLAY SKILL GAP
# ---------------------------------

print("\n----- INITIAL SKILL GAP -----")


print("\nMatched Skills:")

for skill in result["matched_skills"]:
    print(skill)


print("\nMissing Skills:")

for skill in result["missing_skills"]:
    print(skill)


print("\nTotal Required Skills:",
      result["total_required"])

print("Total Matched Skills:",
      result["total_matched"])

print("Total Missing Skills:",
      result["total_missing"])