
import math

from app.services.resume.model_skill_extractor import (
    extract_skills_with_gliner,
    get_claimed_skills_with_gliner,
    normalize_skill,
    validate_threshold,
)


technical_skills_text = """
Programming Languages: Python, Java, JavaScript, C++
Frontend: HTML, CSS, React, Bootstrap
Backend: Node.js, Express.js, Django
Databases: MySQL, MongoDB, SQL
Tools & Platforms: Git, GitHub, Docker, AWS
"""


# ============================================================
# 1. THRESHOLD COMPARISON
# ============================================================

threshold_results = {}

for threshold in [0.30, 0.45]:
    print(f"\n{'=' * 15} THRESHOLD: {threshold} {'=' * 15}")

    skills = extract_skills_with_gliner(
        technical_skills_text,
        threshold=threshold,
    )

    threshold_results[threshold] = skills

    print("\nExtracted skills:")
    for skill in skills:
        print(skill)

    print(f"\nTotal skills: {len(skills)}")

    assert isinstance(skills, list)
    assert all(isinstance(skill, str) and skill for skill in skills)
    assert len(skills) == len(set(skills)), "Duplicate skills found"


# ============================================================
# 2. STRUCTURED CLAIMED SKILLS
# ============================================================

claimed_skills = get_claimed_skills_with_gliner(
    technical_skills_text,
    section_name="technical_skills",
    threshold=0.30,
)

print("\n----- STRUCTURED CLAIMED SKILLS -----")

for item in claimed_skills:
    print(item)

assert isinstance(claimed_skills, list)

for item in claimed_skills:
    assert item["skill"]
    assert item["source"] == "resume"
    assert item["section"] == "technical_skills"
    assert item["claimed"] is True
    assert item["extraction_method"] == "GLiNER"


# ============================================================
# 3. EMPTY INPUT TESTS
# ============================================================

assert extract_skills_with_gliner("") == []
assert extract_skills_with_gliner("   ") == []

print("\nEmpty input tests: PASS")


# ============================================================
# 4. INVALID THRESHOLD TESTS
# ============================================================

invalid_thresholds = [
    -0.1,
    1.1,
    "abc",
    True,
    False,
    float("nan"),
    float("inf"),
    float("-inf"),
]

for threshold in invalid_thresholds:
    try:
        validate_threshold(threshold)
    except ValueError:
        pass
    else:
        raise AssertionError(
            f"Invalid threshold was accepted: {threshold!r}"
        )

print("Invalid threshold tests: PASS")


# Invalid threshold must also be rejected for empty input.
try:
    extract_skills_with_gliner("", threshold=-0.1)
except ValueError:
    pass
else:
    raise AssertionError(
        "Invalid threshold was accepted for empty input"
    )

print("Empty input + invalid threshold test: PASS")


# ============================================================
# 5. NORMALIZATION TESTS
# ============================================================

normalization_cases = {
    " python ": "Python",
    "PYTHON": "Python",
    "react.js": "React",
    "nodejs": "Node.js",
    "HTML5": "HTML",
    "css3": "CSS",
    "Frontend": None,
    "Databases": None,
    "": None,
    None: None,
}

for raw_skill, expected in normalization_cases.items():
    actual = normalize_skill(raw_skill)

    assert actual == expected, (
        f"Normalization failed for {raw_skill!r}: "
        f"expected {expected!r}, got {actual!r}"
    )

# Similar-looking skills must remain distinct.
assert normalize_skill("C") == "C"
assert normalize_skill("C++") == "C++"
assert normalize_skill("Spring") == "Spring"
assert normalize_skill("Spring Boot") == "Spring Boot"
assert normalize_skill("SQL") == "SQL"
assert normalize_skill("MySQL") == "MySQL"

print("Normalization and edge-case tests: PASS")


# ============================================================
# 6. MULTILINE SKILL EXTRACTION DIAGNOSTIC
# ============================================================

multiline_text = """
Technical Skills:
Kafka
Spark
Python
React
"""

multiline_skills = extract_skills_with_gliner(
    multiline_text,
    threshold=0.30,
)

print("\n----- MULTILINE SKILL DIAGNOSTIC -----")
print("Extracted skills:", multiline_skills)

expected_skills = {"Kafka", "Spark", "Python", "React"}
detected_skills = set(multiline_skills)

print("Detected:", sorted(expected_skills & detected_skills))
print("Not detected:", sorted(expected_skills - detected_skills))


# ============================================================
# FINAL RESULT
# ============================================================

print("\nAll current skill extractor checks completed.")
print(
    "Note: Multiline output is diagnostic, and threshold accuracy "
    "still needs validation on more representative resumes."
)
