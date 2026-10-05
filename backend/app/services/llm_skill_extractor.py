from gliner import GLiNER


# ============================================================
# PRETRAINED GLINER MODEL
# ============================================================

MODEL_NAME = "gliner-community/gliner_small-v2.5"

model = GLiNER.from_pretrained(MODEL_NAME)


# ============================================================
# SKILL LABELS
# ============================================================

SKILL_LABELS = [
    "programming language",
    "framework",
    "library",
    "database",
    "cloud platform",
    "devops tool",
    "software tool",
    "technology",
    "technical concept",
    "api technology",
    "machine learning technology",
    "data technology"
]


# ============================================================
# SKILL NORMALIZATION
# ============================================================

NORMALIZATION = {
    "javascript": "JavaScript",
    "javascript es6": "JavaScript",

    "react": "React",
    "react.js": "React",
    "reactjs": "React",

    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",

    "express": "Express.js",
    "express.js": "Express.js",

    "html": "HTML",
    "html5": "HTML",

    "css": "CSS",
    "css3": "CSS",

    "python": "Python",
    "java": "Java",
    "php": "PHP",
    "c++": "C++",
    "typescript": "TypeScript",
    "kotlin": "Kotlin",
    "rust": "Rust",
    "go": "Go",

    "django": "Django",
    "spring": "Spring",
    "spring boot": "Spring Boot",

    "sql": "SQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",
    "sqlite": "SQLite",

    "aws": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",

    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",

    "git": "Git",
    "github": "GitHub",

    "kafka": "Kafka",
    "spark": "Spark",

    "grpc": "gRPC",

    "rest api": "REST API",
    "rest apis": "REST APIs",

    "oauth": "OAuth",
    "oauth 2.0": "OAuth 2.0",

    "machine learning": "Machine Learning",
    "artificial intelligence": "Artificial Intelligence",
    "natural language processing": "Natural Language Processing",
}


# ============================================================
# NORMALIZE
# ============================================================

def normalize_skill(skill):

    skill = skill.strip()

    return NORMALIZATION.get(
        skill.lower(),
        skill
    )


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicate_skills(skills):

    final_skills = []
    seen = set()

    for skill in skills:

        normalized = normalize_skill(skill)

        key = normalized.lower()

        if key not in seen:

            seen.add(key)

            final_skills.append(
                normalized
            )

    return sorted(
        final_skills,
        key=lambda x: x.lower()
    )


# ============================================================
# MODEL-BASED SKILL EXTRACTION
# ============================================================

def extract_skills_with_model(
    text,
    threshold=0.45
):

    if not text:
        return []

    entities = model.predict_entities(
        text,
        SKILL_LABELS,
        threshold=threshold
    )

    skills = []

    for entity in entities:

        skill = entity.get(
            "text",
            ""
        ).strip()

        if skill:

            skills.append(skill)

    return remove_duplicate_skills(
        skills
    )


# ============================================================
# STRUCTURED CLAIMED SKILLS
# ============================================================

def get_model_claimed_skills(
    text,
    section_name="technical_skills",
    threshold=0.45
):

    skills = extract_skills_with_model(
        text,
        threshold
    )

    return [
        {
            "skill": skill,
            "source": "resume",
            "section": section_name,
            "claimed": True,
            "extraction_method": "GLiNER"
        }
        for skill in skills
    ]