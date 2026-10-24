
# ============================================================
# SEMANTIC SKILL GAP CALCULATION
# ============================================================

from functools import lru_cache

from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

HIGH_MATCH_THRESHOLD = 0.85
MEDIUM_MATCH_THRESHOLD = 0.70


SKILL_ALIASES = {
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "express": "express.js",
    "expressjs": "express.js",
    "express.js": "express.js",
    "react.js": "react",
    "reactjs": "react",
    "react": "react",
    "react native": "react native",
    "react-native": "react native",
    "html5": "html",
    "html": "html",
    "css3": "css",
    "css": "css",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "c sharp": "c#",
    "c#": "c#",
    "javascript": "javascript",
    "python": "python",
    "django": "django",
    "mongodb": "mongodb",
    "mysql": "mysql",
    "aws": "aws",
    "docker": "docker",
    "git": "git",
    "github": "github",
    "rest api": "rest api",
    "rest apis": "rest api",
}


def normalize_skill(skill):
    """Normalize a skill name and resolve known aliases."""
    if not isinstance(skill, str):
        return ""

    skill = " ".join(skill.strip().casefold().split())

    if not skill:
        return ""

    return SKILL_ALIASES.get(skill, skill)


@lru_cache(maxsize=1)
def get_semantic_model():
    """Load MiniLM on first semantic inference and reuse the model."""
    # Keep API startup and unit-test collection independent of the optional
    # model import; the dependency is loaded only when semantic matching runs.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def classify_similarity(score):
    """Classify semantic similarity using project thresholds."""
    if score >= HIGH_MATCH_THRESHOLD:
        return "HIGH", "Well claimed"

    if score >= MEDIUM_MATCH_THRESHOLD:
        return "MEDIUM", "Uncertain"

    return "LOW", "Potential gap"


def calculate_semantic_skill_matches(
    claimed_skills,
    required_skills,
    skill_evidence=None,
):
    """
    Compare required skills with resume-claimed skills
    using MiniLM embeddings and cosine similarity.

    Each resume skill can be assigned to at most one
    required skill.

    Semantic similarity does not prove practical proficiency.
    """
    if not isinstance(claimed_skills, (list, tuple)):
        claimed_skills = []

    if not isinstance(required_skills, (list, tuple)):
        required_skills = []
    evidence_by_skill = {}
    if isinstance(skill_evidence, (list, tuple)):
        for record in skill_evidence:
            if not isinstance(record, dict):
                continue
            evidence_skill = normalize_skill(record.get("skill"))
            evidence_items = record.get("evidence", [])
            if evidence_skill:
                evidence_by_skill.setdefault(evidence_skill, [])
                if isinstance(evidence_items, (list, tuple)):
                    evidence_by_skill[evidence_skill].extend(
                        item for item in evidence_items if isinstance(item, dict)
                    )

    def add_evidence_fields(result, matched_skill):
        # Evidence is optional for backwards-compatible direct M04 calls.
        if skill_evidence is None:
            return result
        normalized = normalize_skill(matched_skill)
        evidence_items = evidence_by_skill.get(normalized, [])
        result["evidence_found"] = bool(evidence_items)
        result["evidence"] = evidence_items
        if not evidence_items and result.get("matched_resume_skill") is not None:
            result["status"] = "Claimed; evidence not found"
        return result

    # --------------------------------------------------------
    # STEP 1: Normalize claimed skills
    # --------------------------------------------------------
    claimed = {}

    for item in claimed_skills:
        skill = item.get("skill") if isinstance(item, dict) else item
        normalized = normalize_skill(skill)

        if normalized:
            claimed.setdefault(normalized, skill.strip())

    # --------------------------------------------------------
    # STEP 2: Normalize required skills
    # --------------------------------------------------------
    required = {}

    for skill in required_skills:
        normalized = normalize_skill(skill)

        if normalized:
            required.setdefault(normalized, skill.strip())

    # No required skills
    if not required:
        return []

    # No claimed skills
    if not claimed:
        return [
            add_evidence_fields({
                "required_skill": skill,
                "matched_resume_skill": None,
                "similarity": 0.0,
                "classification": "LOW",
                "status": "Potential gap",
            }, None)
            for skill in sorted(required.values())
        ]

    claimed_items = list(claimed.items())
    required_items = list(required.items())

    # Exact normalized matches need no embedding model. This avoids an
    # unnecessary model load/download for fully covered JDs and keeps exact
    # matching deterministic even when the semantic model is unavailable.
    if all(required_key in claimed for required_key, _ in required_items):
        return [
            add_evidence_fields({
                "required_skill": required_name,
                "matched_resume_skill": claimed[required_key],
                "similarity": 1.0,
                "classification": "HIGH",
                "status": "Well claimed",
            }, claimed[required_key])
            for required_key, required_name in required_items
        ]

    # --------------------------------------------------------
    # STEP 3: Generate MiniLM embeddings for unresolved comparisons
    # --------------------------------------------------------
    model = get_semantic_model()

    claimed_embeddings = model.encode(
        [item[1] for item in claimed_items],
        normalize_embeddings=True,
    )

    required_embeddings = model.encode(
        [item[1] for item in required_items],
        normalize_embeddings=True,
    )

    similarity_matrix = cosine_similarity(
        required_embeddings,
        claimed_embeddings,
    )

    # --------------------------------------------------------
    # STEP 4: Reserve exact normalized matches first
    # --------------------------------------------------------
    assignments = {}
    used_claimed_indices = set()

    for req_index, (required_key, _) in enumerate(required_items):
        for claim_index, (claimed_key, _) in enumerate(claimed_items):
            if (
                required_key == claimed_key
                and claim_index not in used_claimed_indices
            ):
                assignments[req_index] = claim_index
                used_claimed_indices.add(claim_index)
                break

    # --------------------------------------------------------
    # STEP 5: Build remaining semantic match candidates
    # --------------------------------------------------------
    candidates = []

    for req_index in range(len(required_items)):
        if req_index in assignments:
            continue

        for claim_index in range(len(claimed_items)):
            if claim_index in used_claimed_indices:
                continue

            score = float(
                similarity_matrix[req_index][claim_index]
            )

            candidates.append(
                (score, req_index, claim_index)
            )

    candidates.sort(reverse=True)

    # Ignore candidates below the medium threshold.
    candidates = [
        candidate
        for candidate in candidates
        if candidate[0] >= MEDIUM_MATCH_THRESHOLD
    ]

    # --------------------------------------------------------
    # STEP 6: Assign each resume skill at most once
    # --------------------------------------------------------
    for score, req_index, claim_index in candidates:
        if req_index in assignments:
            continue

        if claim_index in used_claimed_indices:
            continue

        assignments[req_index] = claim_index
        used_claimed_indices.add(claim_index)

    # --------------------------------------------------------
    # STEP 7: Build results for all required skills
    # --------------------------------------------------------
    results = []

    for req_index, (required_key, required_name) in enumerate(
        required_items
    ):
        if req_index not in assignments:
            results.append(
                add_evidence_fields({
                    "required_skill": required_name,
                    "matched_resume_skill": None,
                    "similarity": 0.0,
                    "classification": "LOW",
                    "status": "Potential gap",
                }, None)
            )
            continue

        claim_index = assignments[req_index]
        matched_key, matched_name = claimed_items[claim_index]

        score = float(
            similarity_matrix[req_index][claim_index]
        )

        # Exact normalized matches always receive score 1.0.
        if required_key == matched_key:
            score = 1.0

        classification, status = classify_similarity(score)

        results.append(
            add_evidence_fields({
                "required_skill": required_name,
                "matched_resume_skill": matched_name,
                "similarity": round(score, 4),
                "classification": classification,
                "status": status,
            }, matched_name)
        )

    return results


def calculate_skill_gap(claimed_skills, required_skills, skill_evidence=None):
    """
    Preserve original exact-match fields and add semantic matches.
    """
    if not isinstance(claimed_skills, (list, tuple)):
        claimed_skills = []

    if not isinstance(required_skills, (list, tuple)):
        required_skills = []

    # --------------------------------------------------------
    # STEP 1: Prepare normalized skill dictionaries
    # --------------------------------------------------------
    claimed = {}

    for skill in claimed_skills:
        if isinstance(skill, dict):
            skill = skill.get("skill")

        normalized = normalize_skill(skill)

        if normalized:
            claimed.setdefault(normalized, skill.strip())

    required = {}

    for skill in required_skills:
        normalized = normalize_skill(skill)

        if normalized:
            required.setdefault(normalized, skill.strip())

    # --------------------------------------------------------
    # STEP 2: Keep exact-match diagnostics separately
    # --------------------------------------------------------
    exact_matched_keys = required.keys() & claimed.keys()
    exact_missing_keys = required.keys() - claimed.keys()

    exact_matched_skills = sorted(
        required[key] for key in exact_matched_keys
    )
    exact_missing_skills = sorted(
        required[key] for key in exact_missing_keys
    )

    # --------------------------------------------------------
    # STEP 3: Calculate semantic matches
    # --------------------------------------------------------
    semantic_matches = calculate_semantic_skill_matches(
        claimed_skills,
        required_skills,
        skill_evidence,
    )

    # The public match/gap totals must agree with M05: HIGH and MEDIUM
    # semantic matches are provisionally covered; LOW results remain gaps.
    # Exact fields remain available for debugging/audit transparency.
    semantic_by_required = {
        normalize_skill(item.get("required_skill")): item
        for item in semantic_matches
        if isinstance(item, dict) and item.get("required_skill")
    }
    matched_skills = []
    missing_skills = []
    for normalized, required_name in required.items():
        result = semantic_by_required.get(normalized)
        if result and result.get("classification") in {"HIGH", "MEDIUM"}:
            matched_skills.append(required_name)
        else:
            missing_skills.append(required_name)

    matched_skills.sort(key=str.casefold)
    missing_skills.sort(key=str.casefold)

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_required": len(required),
        "total_matched": len(matched_skills),
        "total_missing": len(missing_skills),
        "exact_matched_skills": exact_matched_skills,
        "exact_missing_skills": exact_missing_skills,
        "total_exact_matched": len(exact_matched_skills),
        "total_exact_missing": len(exact_missing_skills),
        "semantic_matches": semantic_matches,
    }
