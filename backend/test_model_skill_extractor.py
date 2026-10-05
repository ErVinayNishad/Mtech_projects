from app.services.resume_parser import (
    extract_text_from_pdf,
    clean_text,
    extract_sections
)

from app.services.llm_skill_extractor import (
    extract_skills_with_model,
    get_model_claimed_skills
)


# ============================================================
# LOAD RESUME
# ============================================================

pdf_text = extract_text_from_pdf(
    "uploads/resume1.pdf"
)

pdf_text = clean_text(
    pdf_text
)


# ============================================================
# EXTRACT SECTIONS
# ============================================================

sections = extract_sections(
    pdf_text
)


# ============================================================
# TECHNICAL SKILLS SECTION
# ============================================================

technical_skills_text = "\n".join(
    sections.get(
        "technical_skills",
        []
    )
)


print("\n----- TECHNICAL SKILLS TEXT -----")

print(
    technical_skills_text
)


# ============================================================
# GLINER EXTRACTION
# ============================================================

skills = extract_skills_with_model(
    technical_skills_text
)


print("\n----- GLINER EXTRACTED SKILLS -----")

for skill in skills:

    print(skill)


# ============================================================
# STRUCTURED CLAIMED SKILLS
# ============================================================

claimed_skills = get_model_claimed_skills(
    technical_skills_text
)


print("\n----- GLINER STRUCTURED CLAIMED SKILLS -----")

for item in claimed_skills:

    print(item)