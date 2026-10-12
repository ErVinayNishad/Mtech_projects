from app.services.resume.model_skill_extractor import (
    extract_skills_with_gliner,
    get_claimed_skills_with_gliner
)

# ============================================================
# TEST TEXT
# ============================================================

technical_skills_text = """
Programming Languages: Python, Java, JavaScript, C++
Frontend: HTML, CSS, React, Bootstrap
Backend: Node.js, Express.js, Django
Databases: MySQL, MongoDB, SQL
Tools & Platforms: Git, GitHub, Docker, AWS
"""


# ============================================================
# GLINER SKILL EXTRACTION
# ============================================================

skills = extract_skills_with_gliner(
    technical_skills_text
)


print("\n----- TECHNICAL SKILLS TEXT -----")

print(technical_skills_text)


print("\n----- GLINER FILTERED SKILLS -----")

for skill in skills:
    print(skill)


# ============================================================
# STRUCTURED CLAIMED SKILLS
# ============================================================

claimed_skills = get_claimed_skills_with_gliner(
    technical_skills_text
)


print("\n----- GLINER STRUCTURED CLAIMED SKILLS -----")

for item in claimed_skills:
    print(item)