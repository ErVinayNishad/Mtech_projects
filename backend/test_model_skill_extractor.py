
import pytest

from app.services.resume.model_skill_extractor import (
    extract_skills_with_gliner,
    get_claimed_skills_with_gliner,
    normalize_skill,
    validate_threshold,
)


TECHNICAL_SKILLS_TEXT = """
Programming Languages: Python, Java, JavaScript, C++
Frontend: HTML, CSS, React, Bootstrap
Backend: Node.js, Express.js, Django
Databases: MySQL, MongoDB, SQL
Tools & Platforms: Git, GitHub, Docker, AWS
"""

INVALID_THRESHOLDS = [
    -0.1,
    1.1,
    "abc",
    True,
    False,
    float("nan"),
    float("inf"),
    float("-inf"),
]


def test_threshold_030_extracts_skills():
    skills = extract_skills_with_gliner(
        TECHNICAL_SKILLS_TEXT,
        threshold=0.30,
    )

    assert isinstance(skills, list)
    assert all(isinstance(skill, str) and skill for skill in skills)
    assert len(skills) == len(set(skills))
    assert skills


def test_threshold_045_extracts_skills():
    skills = extract_skills_with_gliner(
        TECHNICAL_SKILLS_TEXT,
        threshold=0.45,
    )

    assert isinstance(skills, list)
    assert all(isinstance(skill, str) and skill for skill in skills)
    assert len(skills) == len(set(skills))
    assert skills


def test_structured_claimed_skills():
    claimed_skills = get_claimed_skills_with_gliner(
        TECHNICAL_SKILLS_TEXT,
        section_name="technical_skills",
        threshold=0.30,
    )

    assert isinstance(claimed_skills, list)
    assert claimed_skills

    for item in claimed_skills:
        assert item["skill"]
        assert item["source"] == "resume"
        assert item["section"] == "technical_skills"
        assert item["claimed"] is True
        assert item["extraction_method"] == "GLiNER"


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_input_returns_empty_list(text):
    assert extract_skills_with_gliner(text) == []


@pytest.mark.parametrize("threshold", INVALID_THRESHOLDS)
def test_invalid_threshold_is_rejected(threshold):
    with pytest.raises(ValueError):
        validate_threshold(threshold)


def test_invalid_threshold_rejected_for_empty_input():
    with pytest.raises(ValueError):
        extract_skills_with_gliner("", threshold=-0.1)


@pytest.mark.parametrize(
    ("raw_skill", "expected"),
    [
        (" python ", "Python"),
        ("PYTHON", "Python"),
        ("react.js", "React"),
        ("nodejs", "Node.js"),
        ("HTML5", "HTML"),
        ("css3", "CSS"),
        ("Frontend", None),
        ("Databases", None),
        ("", None),
        (None, None),
    ],
)
def test_skill_normalization(raw_skill, expected):
    assert normalize_skill(raw_skill) == expected


def test_similar_skills_remain_distinct():
    assert normalize_skill("C") == "C"
    assert normalize_skill("C++") == "C++"
    assert normalize_skill("Spring") == "Spring"
    assert normalize_skill("Spring Boot") == "Spring Boot"
    assert normalize_skill("SQL") == "SQL"
    assert normalize_skill("MySQL") == "MySQL"


def test_multiline_skill_extraction_diagnostic():
    multiline_text = """
    Technical Skills:
    Kafka
    Spark
    Python
    React
    """

    skills = extract_skills_with_gliner(
        multiline_text,
        threshold=0.30,
    )

    assert isinstance(skills, list)
    assert len(skills) == len(set(skills))

    expected_skills = {"Kafka", "Spark", "Python", "React"}
    print("Detected:", sorted(expected_skills & set(skills)))
    print("Not detected:", sorted(expected_skills - set(skills)))
