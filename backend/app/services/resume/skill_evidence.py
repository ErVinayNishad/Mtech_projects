from app.services.resume.model_skill_extractor import (
    extract_skills_with_gliner
)


# ============================================================
# EXTRACT SKILL EVIDENCE
# ============================================================

def extract_skill_evidence(
    sections,
    claimed_skills
):
    """
    Find where each claimed skill appears in the resume.

    Evidence is searched mainly in:
    - work_experience
    - projects
    - certifications
    - career_objective

    For every resume line, GLiNER is used to detect
    the skills mentioned in that line.
    """

    evidence_sections = [
        "work_experience",
        "projects",
        "certifications",
        "career_objective"
    ]

    skill_evidence = []

    # --------------------------------------------------------
    # Process each claimed skill
    # --------------------------------------------------------

    for item in claimed_skills:

        skill = item["skill"]

        evidence = []

        # ----------------------------------------------------
        # Search selected resume sections
        # ----------------------------------------------------

        for section_name in evidence_sections:

            lines = sections.get(
                section_name,
                []
            )

            # Make sure sections are iterable
            if isinstance(lines, str):
                lines = [lines]

            for line in lines:

                if not line:
                    continue

                # ------------------------------------------------
                # Detect skills present in this resume line
                # ------------------------------------------------

                detected_skills = extract_skills_with_gliner(
                    line
                )

                # ------------------------------------------------
                # Compare normalized skill names
                # ------------------------------------------------

                detected_skills_normalized = {
                    detected_skill.strip().lower()
                    for detected_skill in detected_skills
                    if detected_skill
                }

                if skill.strip().lower() in detected_skills_normalized:

                    evidence.append({
                        "section": section_name,
                        "text": line
                    })

        # ----------------------------------------------------
        # Store evidence for this skill
        # ----------------------------------------------------

        skill_evidence.append({

            "skill": skill,

            "claimed": True,

            "evidence": evidence

        })

    return skill_evidence