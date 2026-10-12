import re


# ============================================================
# SKILL DICTIONARY
# ============================================================

SKILL_DICTIONARY = [

    # --------------------------------------------------------
    # Programming Languages
    # --------------------------------------------------------

    "C++",
    "C",
    "Java",
    "Python",
    "PHP",
    "JavaScript",
    "TypeScript",
    "Kotlin",
    "Go",
    "Rust",

    # --------------------------------------------------------
    # Frontend
    # --------------------------------------------------------

    "React Native",
    "React-Redux",
    "React.js",
    "React",
    "HTML5",
    "HTML",
    "CSS3",
    "CSS",
    "Bootstrap",
    "Material UI",
    "Expo",

    # --------------------------------------------------------
    # Backend / Frameworks
    # --------------------------------------------------------

    "Spring Boot",
    "Spring",
    "Node.js",
    "Node",
    "Express.js",
    "Express",
    "Django",
    "Hibernate",
    "gRPC",

    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------

    "PostgreSQL",
    "MongoDB",
    "MySQL",
    "SQLite",
    "SQL",

    # --------------------------------------------------------
    # Cloud / DevOps / Platforms
    # --------------------------------------------------------

    "GitHub",
    "Git",
    "Docker",
    "Jenkins",
    "AWS",
    "GCP",
    "Firebase",
    "Kubernetes",
    "Terraform",
    "Datadog",

    # --------------------------------------------------------
    # Distributed Systems / Data
    # --------------------------------------------------------

    "Kafka",
    "Spark",

    # --------------------------------------------------------
    # CS / Technical Concepts
    # --------------------------------------------------------

    "Data Structures and Algorithms",
    "Machine Learning",
    "Artificial Intelligence",
    "Natural Language Processing",
    "Data Structures",
    "Algorithms",
    "Computer Networks",
    "DBMS",
    "REST APIs",
    "REST API",
    "OAuth 2.0",
    "OAuth",

]


# ============================================================
# SKILL NORMALIZATION
# ============================================================

SKILL_NORMALIZATION = {

    # --------------------------------------------------------
    # Programming Languages
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Frontend
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Backend / Frameworks
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------

    "sql": "SQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "postgresql": "PostgreSQL",

    # --------------------------------------------------------
    # Cloud / DevOps
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Distributed Systems / Data
    # --------------------------------------------------------

    "kafka": "Kafka",
    "spark": "Spark",

    # --------------------------------------------------------
    # CS / Technical Concepts
    # --------------------------------------------------------

    "machine learning": "Machine Learning",

    "artificial intelligence":
        "Artificial Intelligence",

    "natural language processing":
        "Natural Language Processing",

    "data structures":
        "Data Structures",

    "algorithms":
        "Algorithms",

    "data structures and algorithms":
        "Data Structures and Algorithms",

    "computer networks":
        "Computer Networks",

    "dbms":
        "DBMS",

    "rest api":
        "REST API",

    "rest apis":
        "REST APIs",

    "oauth":
        "OAuth",

    "oauth 2.0":
        "OAuth 2.0",

}


# ============================================================
# NON-SKILL TERMS
# ============================================================

NON_SKILL_TERMS = {
    "",
    "skills",
    "skill",
    "technical skills",
    "technical skill",
    "technologies",
    "technology",
    "frameworks",
    "framework",
    "libraries",
    "library",
    "databases",
    "database",
    "tools",
    "platforms",
    "tools and platforms",
}


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill):
    """
    Normalize a detected skill to a standard name.

    Example:

    node      -> Node.js
    nodejs    -> Node.js
    react.js  -> React
    html5     -> HTML
    github    -> GitHub
    """

    if not skill:
        return None

    skill = skill.strip()

    if not skill:
        return None

    key = skill.lower()

    if key in NON_SKILL_TERMS:
        return None

    return SKILL_NORMALIZATION.get(
        key,
        skill
    )


# ============================================================
# REGEX PATTERN
# ============================================================

def skill_pattern(skill):
    """
    Create a safe regex pattern for a skill.

    Examples:

    C
    C++
    React.js
    Node.js
    Spring Boot
    OAuth 2.0
    """

    escaped_skill = re.escape(skill)

    return (
        r"(?<!\w)"
        + escaped_skill
        + r"(?!\w)"
    )


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(text):
    """
    Extract technical skills from text using
    dictionary + regex matching.

    This is the rule-based/baseline skill extractor.
    """

    if not text:
        return []

    found_skills = []

    # --------------------------------------------------------
    # Detect skills
    # --------------------------------------------------------

    for skill in SKILL_DICTIONARY:

        pattern = skill_pattern(skill)

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            normalized_skill = normalize_skill(
                skill
            )

            if normalized_skill:

                if normalized_skill not in found_skills:

                    found_skills.append(
                        normalized_skill
                    )

    # --------------------------------------------------------
    # Remove overlapping duplicate skills
    #
    # Example:
    #
    # React Native
    # React
    #
    # Both can match the same text.
    # Prefer the more specific/longer skill.
    # --------------------------------------------------------

    found_skills.sort(
        key=len,
        reverse=True
    )

    final_skills = []

    for skill in found_skills:

        duplicate = False

        for existing_skill in final_skills:

            if skill.lower() == existing_skill.lower():

                duplicate = True
                break

        if not duplicate:

            final_skills.append(skill)

    # --------------------------------------------------------
    # Sort alphabetically
    # --------------------------------------------------------

    final_skills.sort(
        key=lambda x: x.lower()
    )

    return final_skills


# ============================================================
# GET CLAIMED SKILLS
# ============================================================

def get_claimed_skills(
    text,
    section_name="technical_skills"
):
    """
    Convert extracted skills into structured
    claimed-skill objects.
    """

    skills = extract_skills(text)

    claimed_skills = []

    for skill in skills:

        claimed_skills.append({

            "skill": skill,

            "source": "resume",

            "section": section_name,

            "claimed": True,

            "extraction_method": "dictionary"

        })

    return claimed_skills