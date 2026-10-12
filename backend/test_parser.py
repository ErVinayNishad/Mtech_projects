
# ============================================================
# IMPORTS
# ============================================================

from app.services.resume.skill_evidence import extract_skill_evidence
from app.services.resume.skill_extractor import extract_skills
from app.services.resume.model_skill_extractor import get_claimed_skills_with_gliner

from app.services.resume.resume_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    extract_sections,
    extract_personal_details
)

from app.services.resume.resume_profile import build_resume_profile


# ============================================================
# PDF TEST
# ============================================================

pdf_text = extract_text_from_pdf("uploads/resume1.pdf")
pdf_text = clean_text(pdf_text)


# ============================================================
# PDF PERSONAL DETAILS
# ============================================================

personal_details = extract_personal_details(pdf_text)

print("\n----- PDF PERSONAL DETAILS -----")

for key, value in personal_details.items():
    print(f"{key}: {value}")


# ============================================================
# PDF SECTION EXTRACTION
# ============================================================

pdf_sections = extract_sections(pdf_text)

# Add extracted personal details to the sections
pdf_sections["personal_details"] = [
    f"{key}: {value}"
    for key, value in personal_details.items()
    if value
]

print("\n----- PDF EXTRACTED SECTIONS -----")

for section, content in pdf_sections.items():
    print(f"\n[{section}]")

    for line in content:
        print(line)


# ============================================================
# PDF SKILL EXTRACTION
# ============================================================

technical_skills_text = "\n".join(
    pdf_sections.get("technical_skills", [])
)

skills = extract_skills(technical_skills_text)

print("\n----- EXTRACTED PDF SKILLS -----")

for skill in skills:
    print(skill)


# ============================================================
# GLINER CLAIMED SKILLS
# ============================================================

claimed_skill_data = get_claimed_skills_with_gliner(
    technical_skills_text
)

print("\n----- GLINER STRUCTURED CLAIMED SKILLS -----")

for item in claimed_skill_data:
    print(item)


# ============================================================
# BUILD STRUCTURED RESUME PROFILE
# ============================================================

resume_profile = build_resume_profile(
    pdf_sections,
    claimed_skill_data
)

print("\n----- STRUCTURED RESUME PROFILE -----")


# ============================================================
# SKILL EVIDENCE
# ============================================================

skill_evidence = extract_skill_evidence(
    pdf_sections,
    claimed_skill_data
)

print("\n----- SKILL EVIDENCE -----")

for item in skill_evidence:
    print(f"\nSkill: {item['skill']}")
    print(f"Claimed: {item['claimed']}")

    if item["evidence"]:
        for evidence in item["evidence"]:
            print(
                f"  [{evidence['section']}] "
                f"{evidence['text']}"
            )
    else:
        print("  No evidence found")


# ============================================================
# FINAL STRUCTURED PROFILE
# ============================================================

print("\n----- FINAL STRUCTURED RESUME PROFILE -----")

for section, content in resume_profile.items():
    print(f"\n[{section}]")

    for item in content:
        print(item)


# ============================================================
# DOCX TEST
# ============================================================

docx_text = extract_text_from_docx("uploads/resume1.docx")
docx_text = clean_text(docx_text)

docx_sections = extract_sections(docx_text)

# Add personal details for DOCX as well
docx_personal_details = extract_personal_details(docx_text)

docx_sections["personal_details"] = [
    f"{key}: {value}"
    for key, value in docx_personal_details.items()
    if value
]

print("\n----- DOCX EXTRACTED SECTIONS -----")

for section, content in docx_sections.items():
    print(f"\n[{section}]")

    for line in content:
        print(line)


# ============================================================
# DOCX SKILL EXTRACTION
# ============================================================

docx_technical_skills_text = "\n".join(
    docx_sections.get("technical_skills", [])
)

docx_skills = extract_skills(docx_technical_skills_text)

print("\n----- EXTRACTED DOCX SKILLS -----")

for skill in docx_skills:
    print(skill)
