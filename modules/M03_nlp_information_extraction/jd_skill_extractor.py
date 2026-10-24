import re

from modules.M03_nlp_information_extraction.model_skill_extractor import (
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


def _required_skills_section(text):
    """Return an explicitly labelled required-skills section when present.

    This prevents role titles, responsibilities, and soft-skill statements from
    being mistaken for required technical skills. If no recognizable section is
    found, callers retain the previous whole-document fallback behavior.
    """
    lines = text.splitlines()
    start_patterns = (
        r"^\s*(?:required\s+skills|skills\s+required|technical\s+skills|"
        r"must[- ]have\s+skills|key\s+skills)\s*:?\s*$",
    )
    end_pattern = re.compile(
        r"^\s*(?:responsibilities|key responsibilities|what you(?:'|’)ll do|"
        r"qualifications|preferred qualifications|requirements|about the role|"
        r"about us|benefits|nice to have|preferred skills|experience)\s*:?\s*$",
        re.IGNORECASE,
    )
    start_pattern = re.compile(start_patterns[0], re.IGNORECASE)

    for index, line in enumerate(lines):
        # Also support an inline heading such as "Required Skills: Python, Django".
        inline = re.match(
            r"^\s*(?:required\s+skills|skills\s+required|technical\s+skills|"
            r"must[- ]have\s+skills|key\s+skills)\s*:\s*(.+?)\s*$",
            line,
            re.IGNORECASE,
        )
        if inline:
            collected = [inline.group(1)]
            for following in lines[index + 1:]:
                if end_pattern.match(following):
                    break
                collected.append(following)
            return "\n".join(collected).strip()

        if start_pattern.match(line):
            collected = []
            for following in lines[index + 1:]:
                if end_pattern.match(following):
                    break
                collected.append(following)
            section = "\n".join(collected).strip()
            if section:
                return section

    return None


def _clean_skill_list_text(text):
    """Remove list markers while preserving the skill wording for GLiNER."""
    cleaned = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(?:[-*•▪]+|\d+[.)])\s*", "", line).strip()
        if line:
            cleaned.append(line)
    return "\n".join(cleaned)


def extract_required_skills(text):
    """Extract job skills, prioritizing an explicitly labelled skills section.

    GLiNER remains the open-vocabulary extractor. Known-skill matching is only a
    recovery fallback, not the authoritative skill dictionary. If a JD has no
    explicit skills section, the whole JD is scanned for backwards compatibility.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    scoped_text = _required_skills_section(text)
    extraction_text = _clean_skill_list_text(scoped_text) if scoped_text else text

    extracted_skills = extract_skills_with_gliner(extraction_text)
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

    # Recover known skills missed by GLiNER, but only search the scoped skills
    # section when one exists. This avoids treating ordinary responsibility text
    # (for example, "Develop backend applications") as separate required skills.
    sorted_known_skills = sorted(
        KNOWN_SKILLS.items(), key=lambda item: len(item[0]), reverse=True
    )
    for skill_key, display_name in sorted_known_skills:
        pattern = (
            r"(?<![a-zA-Z0-9+#])" + re.escape(skill_key)
            + r"(?![a-zA-Z0-9+#])"
        )
        if re.search(pattern, extraction_text, flags=re.IGNORECASE):
            unique_skills.setdefault(skill_key, display_name)

    # Avoid counting React as a separate skill when it appears only as part of
    # React Native; preserve both if React is independently listed as well.
    if "react native" in unique_skills and "react" in unique_skills:
        standalone_react_pattern = (
            r"(?<![a-zA-Z0-9+#])react(?![a-zA-Z0-9+#]|\s+native\b)"
        )
        if not re.search(standalone_react_pattern, extraction_text, re.IGNORECASE):
            unique_skills.pop("react", None)

    return sorted(unique_skills.values(), key=str.casefold)
