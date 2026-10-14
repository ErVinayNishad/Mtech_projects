import re

from app.services.resume.model_skill_extractor import (
    extract_skills_with_gliner,
)


NON_SKILL_TERMS = {
    "experience",
    "knowledge",
    "developer",
    "software developer",
    "candidate",
    "strong",
    "preferred",
    "required",
    "requirements",
    "skills",
    "skill",
    "work",
    "development",
}


# Known technical skills used as a fallback when GLiNER misses them.
KNOWN_SKILLS = {
    "python": "Python",
    "django": "Django",
    "rest api": "REST API",
    "rest apis": "REST APIs",
    "sql": "SQL",
    "mongodb": "MongoDB",
    "git": "Git",
    "aws": "AWS",
    "docker": "Docker",
    "javascript": "JavaScript",
    "react": "React",
    "react native": "React Native",
    "tensorflow": "TensorFlow",
    "java": "Java",
    "kubernetes": "Kubernetes",
    "bootstrap": "Bootstrap",
    "node.js": "Node.js",
    "express.js": "Express.js",
    "mysql": "MySQL",
    "c++": "C++",
    "html": "HTML",
    "css": "CSS",
}


def extract_required_skills(text):
    """
    Extract skills from a job description using GLiNER,
    then recover known technical skills that GLiNER may miss.

    Normalize whitespace, remove non-skill terms and duplicates,
    and return a sorted list of skills.
    """

    if not isinstance(text, str) or not text.strip():
        return []

    # Primary extraction using GLiNER.
    extracted_skills = extract_skills_with_gliner(text)

    if not isinstance(extracted_skills, (list, tuple, set)):
        extracted_skills = []

    unique_skills = {}

    for skill in extracted_skills:
        if not isinstance(skill, str) or not skill.strip():
            continue

        skill = re.sub(r"\s+", " ", skill.strip())
        normalized_skill = skill.casefold()

        if normalized_skill in NON_SKILL_TERMS:
            continue

        unique_skills.setdefault(normalized_skill, skill)

    # Fallback: check known skills in the original job description.
    # Longer names are checked first to prioritize multi-word skills
    # such as React Native over React.
    sorted_known_skills = sorted(
        KNOWN_SKILLS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for skill_key, display_name in sorted_known_skills:
        pattern = (
            r"(?<![a-zA-Z0-9+#])"
            + re.escape(skill_key)
            + r"(?![a-zA-Z0-9+#])"
        )

        if re.search(pattern, text, flags=re.IGNORECASE):
            unique_skills.setdefault(skill_key, display_name)

    # If React Native is explicitly mentioned, remove a separate
    # React entry so the same mention is not counted as two skills.
    if "react native" in unique_skills:
        unique_skills.pop("react", None)

    return sorted(unique_skills.values(), key=str.casefold)
