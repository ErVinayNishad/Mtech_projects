from app.services.Job.job_skill_extractor import (
    extract_required_skills
)


job_description = """
We are looking for a Software Developer with strong
experience in Python, Django and React.

The candidate should have knowledge of Docker,
AWS, MongoDB and REST APIs.

Experience with Git and JavaScript is preferred.
"""


required_skills = extract_required_skills(
    job_description
)


print("\n----- JOB DESCRIPTION -----")
print(job_description)

print("\n----- REQUIRED SKILLS -----")

for skill in required_skills:
    print(skill)