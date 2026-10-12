from gliner import GLiNER


# ============================================================
# LOAD GLINER MODEL
# ============================================================

MODEL_NAME = "urchade/gliner_medium-v2.1"

model = GLiNER.from_pretrained(
    MODEL_NAME
)


# ============================================================
# ENTITY LABELS
# ============================================================

ENTITY_LABELS = [
    "programming language",
    "framework",
    "library",
    "database",
    "cloud platform",
    "devops tool",
    "software tool",
    "technology",
    "technical skill"
]


# ============================================================
# NON-SKILL TERMS
# ============================================================

NON_SKILL_TERMS = {
    "programming languages",
    "programming language",
    "frontend",
    "backend",
    "databases",
    "database",
    "tools",
    "tools and platforms",
    "platforms",
    "technologies",
    "technology",
    "technical skills",
    "technical skill",
    "frameworks",
    "libraries"
}


# ============================================================
# SKILL NORMALIZATION
# ============================================================

SKILL_NORMALIZATION = {

    # React
    "react.js": "React",
    "reactjs": "React",
    "react": "React",

    # Node.js
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",

    # Express
    "express": "Express.js",
    "express.js": "Express.js",

    # HTML
    "html5": "HTML",
    "html": "HTML",

    # CSS
    "css3": "CSS",
    "css": "CSS",

    # JavaScript
    "javascript": "JavaScript",

    # Git
    "github": "GitHub",
    "git": "Git",

    # Cloud
    "aws": "AWS",
    "gcp": "GCP",

    # Databases
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",
    "sqlite": "SQLite",

    # Programming languages
    "python": "Python",
    "java": "Java",
    "c++": "C++",
    "c": "C",
    "typescript": "TypeScript",
    "kotlin": "Kotlin",
    "php": "PHP",
    "go": "Go",
    "rust": "Rust",

    # Frameworks
    "django": "Django",
    "spring": "Spring",
    "spring boot": "Spring Boot",

    # DevOps / Cloud
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",

    # Distributed systems / data
    "kafka": "Kafka",
    "spark": "Spark",

    # Tools
    "grpc": "gRPC",
    "datadog": "Datadog",
    "firebase": "Firebase",

    # Database
    "sql": "SQL",

    # APIs
    "rest api": "REST API",
    "rest apis": "REST APIs",

    # Authentication
    "oauth": "OAuth",
    "oauth 2.0": "OAuth 2.0",

    # AI / ML
    "machine learning": "Machine Learning",
    "artificial intelligence": "Artificial Intelligence",
    "natural language processing":
        "Natural Language Processing",
}


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill):

    if not skill:
        return None

    skill = skill.strip()

    if not skill:
        return None

    key = skill.lower()

    # Remove generic/non-skill terms
    if key in NON_SKILL_TERMS:
        return None

    return SKILL_NORMALIZATION.get(
        key,
        skill
    )


# ============================================================
# EXTRACT SKILLS USING GLINER
# ============================================================

def extract_skills_with_gliner(text):

    if not text:
        return []

    entities = model.predict_entities(
        text,
        ENTITY_LABELS,
        threshold=0.45
    )

    skills = []

    for entity in entities:

        skill = entity["text"].strip()

        normalized_skill = normalize_skill(
            skill
        )

        if not normalized_skill:
            continue

        if normalized_skill not in skills:

            skills.append(
                normalized_skill
            )

    skills.sort(
        key=lambda x: x.lower()
    )

    return skills


# ============================================================
# STRUCTURED CLAIMED SKILLS
# ============================================================

def get_claimed_skills_with_gliner(
    text,
    section_name="technical_skills"
):

    skills = extract_skills_with_gliner(
        text
    )

    claimed_skills = []

    for skill in skills:

        claimed_skills.append({

            "skill": skill,

            "source": "resume",

            "section": section_name,

            "claimed": True,

            "extraction_method": "GLiNER"

        })

    return claimed_skills