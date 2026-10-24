import math
import re
from functools import lru_cache


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "urchade/gliner_medium-v2.1"
DEFAULT_THRESHOLD = 0.30

@lru_cache(maxsize=1)
def get_model():
    """Load the pretrained extractor once, on first inference."""
    from gliner import GLiNER
    return GLiNER.from_pretrained(MODEL_NAME)


# ============================================================
# ENTITY LABELS - ORIGINAL 9 LABELS
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
    "framework",
    "libraries",
    "library",
    "cloud platforms",
    "devops tools",
    "software tools",
    "technical tools",
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
    "bootstrap": "Bootstrap",
}


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill):
    if not isinstance(skill, str):
        return None

    skill = " ".join(skill.split())

    if not skill:
        return None

    key = skill.casefold()

    if key in NON_SKILL_TERMS:
        return None

    # Return only recognized and normalized technical skills.
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

def extract_skills_with_gliner(
    text,
    threshold=DEFAULT_THRESHOLD,
):
    validate_threshold(threshold)

    if not isinstance(text, str) or not text.strip():
        return []

    prediction_texts = [text]

    # Also evaluate individual lines to recover skills from lists.
    if "\n" in text or "\r" in text:
        prediction_texts.extend(
            line.strip()
            for line in text.splitlines()
            if line.strip()
        )

    skills = {}

    for prediction_text in prediction_texts:
        entities = get_model().predict_entities(
            prediction_text,
            ENTITY_LABELS,
            threshold=threshold,
        )

        for entity in entities:
            raw_skill = entity.get("text", "")

            if not isinstance(raw_skill, str):
                continue

            parts = (
                raw_skill
                .replace("\r\n", "\n")
                .replace("\r", "\n")
                .replace("\n", ",")
                .split(",")
            )

            for part in parts:
                normalized_skill = normalize_skill(part)

                if normalized_skill:
                    skills.setdefault(
                        normalized_skill.casefold(),
                        normalized_skill,
                    )

    return sorted(skills.values(), key=str.casefold)


# ============================================================
# STRUCTURED CLAIMED SKILLS
# ============================================================

def _extract_known_skill_mentions(text):
    """Recover known skill mentions that GLiNER may miss.

    This is a conservative lexical fallback over canonical/alias names already
    represented in SKILL_NORMALIZATION. GLiNER remains the open-vocabulary
    primary extractor, so skills outside this mapping can still be returned by
    the model.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    found = {}
    # Very ambiguous short names are left to GLiNER/context rather than
    # lexically inferred from ordinary prose (e.g. "go to the office", "Grade C").
    ambiguous_aliases = {"c", "go"}
    # Prefer longer aliases first, e.g. REST APIs before REST API.
    for alias in sorted(SKILL_NORMALIZATION, key=len, reverse=True):
        if alias in ambiguous_aliases:
            continue
        pattern = r"(?<![\w+#])" + re.escape(alias) + r"(?![\w+#])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            canonical = SKILL_NORMALIZATION[alias]
            found.setdefault(canonical.casefold(), canonical)

    return sorted(found.values(), key=str.casefold)


def get_claimed_skills_with_gliner(
    text,
    section_name="technical_skills",
    threshold=DEFAULT_THRESHOLD,
):
    """Return GLiNER claims supplemented by exact mentions of known skills.

    The fallback improves recall for familiar skills occasionally missed by the
    model (e.g. REST APIs in an experience bullet) without restricting GLiNER's
    open-vocabulary results to a fixed dictionary.
    """
    model_skills = extract_skills_with_gliner(
        text,
        threshold=threshold,
    )

    skills = {}
    for skill in model_skills:
        if isinstance(skill, str) and skill.strip():
            normalized = normalize_skill(skill)
            if normalized:
                skills.setdefault(normalized.casefold(), (normalized, "GLiNER"))

    for skill in _extract_known_skill_mentions(text):
        skills.setdefault(
            skill.casefold(),
            (skill, "GLiNER+known-skill fallback"),
        )

    return [
        {
            "skill": skill,
            "source": "resume",
            "section": section_name,
            "claimed": True,
            "extraction_method": method,
        }
        for skill, method in sorted(
            skills.values(), key=lambda item: item[0].casefold()
        )
    ]
