import re


# ============================================================
# SKILL DICTIONARY
# ============================================================

SKILL_DICTIONARY = [

    # --------------------------------------------------------
    # Programming Languages
    # --------------------------------------------------------

    "C",
    "C++",
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

    "HTML",
    "HTML5",
    "CSS",
    "CSS3",
    "React",
    "React.js",
    "React Native",
    "React-Redux",
    "Bootstrap",
    "Material UI",
    "Expo",

    # --------------------------------------------------------
    # Backend / Frameworks
    # --------------------------------------------------------

    "Node.js",
    "Node",
    "Express.js",
    "Express",
    "Django",
    "Spring",
    "Spring Boot",
    "Hibernate",
    "gRPC",

    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------

    "SQL",
    "MySQL",
    "MongoDB",
    "SQLite",
    "PostgreSQL",

    # --------------------------------------------------------
    # Cloud / DevOps / Platforms
    # --------------------------------------------------------

    "Git",
    "GitHub",
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

    "Machine Learning",
    "Artificial Intelligence",
    "Natural Language Processing",
    "Data Structures",
    "Algorithms",
    "Data Structures and Algorithms",
    "Computer Networks",
    "DBMS",
    "REST APIs",
    "REST API",
    "OAuth",
    "OAuth 2.0",

]


# ============================================================
# SKILL NORMALIZATION
# ============================================================

SKILL_NORMALIZATION = {

    # JavaScript
    "javascript": "JavaScript",

    # React
    "react.js": "React",
    "reactjs": "React",
    "react": "React",

    # React Native
    "react native": "React Native",

    # HTML
    "html5": "HTML",
    "html": "HTML",

    # CSS
    "css3": "CSS",
    "css": "CSS",

    # Node
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node": "Node.js",

    # Express
    "express.js": "Express.js",
    "express": "Express.js",

    # Git
    "github": "GitHub",
    "git": "Git",

    # Cloud
    "aws": "AWS",
    "gcp": "GCP",

    # Database
    "sql": "SQL",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "postgresql": "PostgreSQL",

    # Java
    "java": "Java",

    # Python
    "python": "Python",

    # C
    "c": "C",
    "c++": "C++",

    # Data structures
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "data structures and algorithms":
        "Data Structures and Algorithms",

    # APIs
    "rest api": "REST API",
    "rest apis": "REST APIs",

    # OAuth
    "oauth": "OAuth",
    "oauth 2.0": "OAuth 2.0",

    # React ecosystem
    "react-redux": "React-Redux",

    # Spring
    "spring boot": "Spring Boot",

}


# ============================================================
# REGEX ESCAPE / MATCHING
# ============================================================

def skill_pattern(skill):

    """
    Creates a regex pattern for a skill.

    Handles skills such as:

    C
    C++
    C#
    React.js
    Node.js
    Spring Boot
    React-Redux
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

    if not text:
        return []

    found_skills = []

    # --------------------------------------------------------
    # Find every skill
    # --------------------------------------------------------

    for skill in SKILL_DICTIONARY:

        pattern = skill_pattern(skill)

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            found_skills.append(skill)

    # --------------------------------------------------------
    # Remove duplicate / overlapping skills
    # --------------------------------------------------------

    # Longest skills first.
    # Example:
    #
    # React Native
    # React
    #
    # We want React Native only.
    #
    found_skills.sort(
        key=len,
        reverse=True
    )

    final_skills = []

    for skill in found_skills:

        is_duplicate = False

        for existing_skill in final_skills:

            if (
                skill.lower()
                == existing_skill.lower()
            ):

                is_duplicate = True
                break

        if not is_duplicate:

            final_skills.append(skill)

    # --------------------------------------------------------
    # Normalize names
    # --------------------------------------------------------

    normalized_skills = []

    for skill in final_skills:

        normalized_skill = (
            SKILL_NORMALIZATION.get(
                skill.lower(),
                skill
            )
        )

        if normalized_skill not in normalized_skills:

            normalized_skills.append(
                normalized_skill
            )

    # --------------------------------------------------------
    # Sort alphabetically
    # --------------------------------------------------------

    normalized_skills.sort(
        key=lambda x: x.lower()
    )

    return normalized_skills


# ============================================================
# GET CLAIMED SKILLS
# ============================================================

def get_claimed_skills(
    text,
    section_name="technical_skills"
):

    skills = extract_skills(text)

    claimed_skills = []

    for skill in skills:

        claimed_skills.append({

            "skill": skill,

            "source": "resume",

            "section": section_name,

            "claimed": True

        })

    return claimed_skills