from app.services.skill_extractor import (
    extract_skills,
    get_claimed_skills
)

from app.services.resume_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    extract_sections,
    extract_personal_details
)
from app.services.resume_profile import build_resume_profile


# ============================================================
# PDF TEST
# ============================================================

pdf_text = extract_text_from_pdf(
    "uploads/resume1.pdf"
)

pdf_text = clean_text(pdf_text)
# -----------------------------
# PERSONAL DETAILS TEST
# -----------------------------

personal_details = extract_personal_details(
    pdf_text
)

print("\n----- PDF PERSONAL DETAILS -----")

for key, value in personal_details.items():
    print(f"{key}: {value}")

pdf_sections = extract_sections(pdf_text)

print("----- PDF EXTRACTED SECTIONS -----")

for section, content in pdf_sections.items():

    print(f"\n[{section}]")

    for line in content:
        print(line)


# ============================================================
# DOCX TEST
# ============================================================

docx_text = extract_text_from_docx(
    "uploads/resume1.docx"
)

docx_text = clean_text(docx_text)

docx_sections = extract_sections(docx_text)

print("\n----- DOCX EXTRACTED SECTIONS -----")

for section, content in docx_sections.items():

    print(f"\n[{section}]")

    for line in content:
        print(line)


# ============================================================
# PDF SKILL EXTRACTION
# ============================================================

technical_skills_text = "\n".join(
    pdf_sections.get("technical_skills", [])
)

skills = extract_skills(
    technical_skills_text
)

print("\n----- EXTRACTED PDF SKILLS -----")

for skill in skills:
    print(skill)


# ============================================================
# DOCX SKILL EXTRACTION
# ============================================================

docx_technical_skills_text = "\n".join(
    docx_sections.get("technical_skills", [])
)

docx_skills = extract_skills(
    docx_technical_skills_text
)

print("\n----- EXTRACTED DOCX SKILLS -----")

for skill in docx_skills:
    print(skill)


# ============================================================
# STRUCTURED CLAIMED SKILLS
# ============================================================

claimed_skill_data = get_claimed_skills(
    technical_skills_text
)

print("\n----- STRUCTURED CLAIMED SKILLS -----")

for item in claimed_skill_data:
    print(item)


# ============================================================
# STRUCTURED RESUME PROFILE
# ============================================================

resume_profile = build_resume_profile(
    pdf_sections,
    claimed_skill_data
)

print("\n----- STRUCTURED RESUME PROFILE -----")

for section, content in resume_profile.items():

    print(f"\n[{section}]")

    for item in content:
        print(item)