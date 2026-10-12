
from gliner import GLiNER
import math


# ============================================================
# LOAD GLINER MODEL
# ============================================================

MODEL_NAME = "urchade/gliner_medium-v2.1"
model = GLiNER.from_pretrained(MODEL_NAME)


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
    "technical skill",
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
    "libraries",
}


# ============================================================
# SKILL NORMALIZATION
# ============================================================

SKILL_NORMALIZATION = {
    "react.js": "React",
    "reactjs": "React",
    "react": "React",

    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",

    "express": "Express.js",
    "express.js": "Express.js",

    "html5": "HTML",
    "html": "HTML",

    "css3": "CSS",
    "css": "CSS",

    "javascript": "JavaScript",

    "github": "GitHub",
    "git": "Git",

    "aws": "AWS",
    "gcp": "GCP",

    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",
    "sqlite": "SQLite",

    "python": "Python",
    "java": "Java",
    "c++": "C++",
    "c": "C",
    "typescript": "TypeScript",
    "kotlin": "Kotlin",
    "php": "PHP",
    "go": "Go",
    "rust": "Rust",

    "django": "Django",
    "spring": "Spring",
    "spring boot": "Spring Boot",

    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",

    "kafka": "Kafka",
    "spark": "Spark",

    "grpc": "gRPC",
    "datadog": "Datadog",
    "firebase": "Firebase",

    "sql": "SQL",

    "rest api": "REST API",
    "rest apis": "REST APIs",

    "oauth": "OAuth",
    "oauth 2.0": "OAuth 2.0",

    "machine learning": "Machine Learning",
    "artificial intelligence": "Artificial Intelligence",
    "natural language processing": "Natural Language Processing",
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
# VALIDATE THRESHOLD
# ============================================================

def validate_threshold(threshold):
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(threshold)
        or not 0.0 <= threshold <= 1.0
    ):
        raise ValueError(
            "threshold must be a finite number between 0.0 and 1.0"
        )


# ============================================================
# EXTRACT SKILLS USING GLINER
# ============================================================

def extract_skills_with_gliner(text, threshold=0.30):
    # Validate even when the input text is empty.
    validate_threshold(threshold)

    if not isinstance(text, str) or not text.strip():
        return []

    entities = model.predict_entities(
        text,
        ENTITY_LABELS,
        threshold=threshold,
    )

    skills = []
    seen_skills = set()

    for entity in entities:
        raw_skill = entity.get("text", "")

        if not isinstance(raw_skill, str):
            continue

        # Split merged multiline or comma-separated skill entities.
        parts = (
            raw_skill
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .replace("\n", ",")
            .split(",")
        )

        for part in parts:
            normalized_skill = normalize_skill(part)

            if not normalized_skill:
                continue

            # Deduplicate case-insensitively.
            key = normalized_skill.casefold()

            if key not in seen_skills:
                seen_skills.add(key)
                skills.append(normalized_skill)

    return sorted(skills, key=str.casefold)


# ============================================================
# STRUCTURED CLAIMED SKILLS
# ============================================================

def get_claimed_skills_with_gliner(
    text,
    section_name="technical_skills",
    threshold=0.30,
):
    skills = extract_skills_with_gliner(
        text,
        threshold=threshold,
    )

    return [
        {
            "skill": skill,
            "source": "resume",
            "section": section_name,
            "claimed": True,
            "extraction_method": "GLiNER",
        }
        for skill in skills
    ]
