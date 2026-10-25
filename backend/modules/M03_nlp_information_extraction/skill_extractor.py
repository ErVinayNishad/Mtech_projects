import re


# ============================================================
# SKILL DICTIONARY
# ============================================================

SKILL_DICTIONARY = [
    "C++", "C", "Java", "Python", "PHP", "JavaScript",
    "TypeScript", "Kotlin", "Go", "Rust",
    "React Native", "React-Redux", "React.js", "React",
    "HTML5", "HTML", "CSS3", "CSS", "Bootstrap",
    "Material UI", "Expo",
    "Spring Boot", "Spring", "Node.js", "Node",
    "Express.js", "Express", "Django", "Hibernate", "gRPC",
    "PostgreSQL", "MongoDB", "MySQL", "SQLite", "SQL",
    "GitHub", "Git", "Docker", "Jenkins", "AWS", "GCP",
    "Firebase", "Kubernetes", "Terraform", "Datadog",
    "Kafka", "Spark",
    "Data Structures and Algorithms", "Machine Learning",
    "Artificial Intelligence", "Natural Language Processing",
    "Data Structures", "Algorithms", "Computer Networks",
    "DBMS", "REST APIs", "REST API", "OAuth 2.0", "OAuth",
]


# ============================================================
# SKILL NORMALIZATION
# ============================================================

SKILL_NORMALIZATION = {
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "python": "Python",
    "java": "Java",
    "php": "PHP",
    "kotlin": "Kotlin",
    "go": "Go",
    "rust": "Rust",
    "c": "C",
    "c++": "C++",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "react native": "React Native",
    "react-redux": "React-Redux",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "bootstrap": "Bootstrap",
    "material ui": "Material UI",
    "expo": "Expo",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "django": "Django",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "hibernate": "Hibernate",
    "grpc": "gRPC",
    "sql": "SQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "postgresql": "PostgreSQL",
    "git": "Git",
    "github": "GitHub",
    "docker": "Docker",
    "jenkins": "Jenkins",
    "aws": "AWS",
    "gcp": "GCP",
    "firebase": "Firebase",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",
    "datadog": "Datadog",
    "kafka": "Kafka",
    "spark": "Spark",
    "machine learning": "Machine Learning",
    "artificial intelligence": "Artificial Intelligence",
    "natural language processing": "Natural Language Processing",
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "data structures and algorithms": "Data Structures and Algorithms",
    "computer networks": "Computer Networks",
    "dbms": "DBMS",
    "rest api": "REST API",
    "rest apis": "REST APIs",
    "oauth": "OAuth",
    "oauth 2.0": "OAuth 2.0",
}


# ============================================================
# NON-SKILL TERMS
# ============================================================

NON_SKILL_TERMS = {
    "", "skills", "skill", "technical skills", "technical skill",
    "technologies", "technology", "frameworks", "framework",
    "libraries", "library", "databases", "database", "tools",
    "platforms", "tools and platforms",
}


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill):
    if not isinstance(skill, str):
        return None

    skill = skill.strip()

    if not skill:
        return None

    key = skill.casefold()

    if key in NON_SKILL_TERMS:
        return None

    return SKILL_NORMALIZATION.get(key, skill)


# ============================================================
# REGEX PATTERN
# ============================================================

def skill_pattern(skill):
    """Create a regex pattern with safe skill-name boundaries."""

    escaped_skill = re.escape(skill)

    # Prevent C from matching C++, C#, or words starting with C.
    if skill.casefold() == "c":
        return r"(?<!\w)C(?![\w+#])"

    return r"(?<!\w)" + escaped_skill + r"(?!\w)"


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(text):
    """
    Rule-based baseline extractor.
    Prefer specific skill names over overlapping shorter names.
    """

    if not isinstance(text, str) or not text.strip():
        return []

    found_skills = {}

    for skill in SKILL_DICTIONARY:
        if re.search(skill_pattern(skill), text, re.IGNORECASE):
            normalized_skill = normalize_skill(skill)

            if normalized_skill:
                found_skills.setdefault(
                    normalized_skill.casefold(),
                    normalized_skill,
                )

    # Longer names first, so Spring Boot is considered before Spring.
    candidates = sorted(
        found_skills.values(),
        key=lambda skill: (-len(skill), skill.casefold()),
    )

    final_skills = []

    for skill in candidates:
        duplicate = False

        for existing_skill in final_skills:
            if skill.casefold() == existing_skill.casefold():
                duplicate = True
                break

            # Avoid returning React when the text only matched React Native.
            if re.search(
                skill_pattern(skill),
                existing_skill,
                re.IGNORECASE,
            ):
                duplicate = True
                break

        if not duplicate:
            final_skills.append(skill)

    return sorted(final_skills, key=str.casefold)


# ============================================================
# GET CLAIMED SKILLS
# ============================================================

def get_claimed_skills(text, section_name="technical_skills"):
    """Return extracted skills as structured claimed-skill records."""

    skills = extract_skills(text)

    return [
        {
            "skill": skill,
            "source": "resume",
            "section": section_name,
            "claimed": True,
            "extraction_method": "dictionary",
        }
        for skill in skills
    ]
