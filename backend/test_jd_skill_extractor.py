
from app.services.job.jd_skill_extractor import extract_required_skills


JOB_DESCRIPTION_1 = """
We are looking for a Python Developer.

The candidate should have strong knowledge of Python,
Django, REST APIs, SQL, MongoDB and Git.

Experience with AWS and Docker is preferred.
Knowledge of JavaScript and React is an advantage.
"""

JOB_DESCRIPTION_2 = """
We are looking for a Software Developer with strong
experience in Python, Django and React.

The candidate should have knowledge of Docker,
AWS, MongoDB and REST APIs.

Experience with Git and JavaScript is preferred.
"""

EXPECTED_SKILLS_1 = {
    "python",
    "django",
    "rest apis",
    "sql",
    "mongodb",
    "git",
    "aws",
    "docker",
    "javascript",
    "react",
}

EXPECTED_SKILLS_2 = {
    "python",
    "django",
    "react",
    "docker",
    "aws",
    "mongodb",
    "rest apis",
    "git",
    "javascript",
}


def test_extract_required_skills_returns_list():
    result = extract_required_skills(JOB_DESCRIPTION_1)

    assert isinstance(result, list)


def test_extracts_expected_skills_from_first_description():
    result = extract_required_skills(JOB_DESCRIPTION_1)
    normalized_skills = {skill.casefold() for skill in result}

    assert EXPECTED_SKILLS_1.issubset(normalized_skills)


def test_extracts_expected_skills_from_second_description():
    result = extract_required_skills(JOB_DESCRIPTION_2)
    normalized_skills = {skill.casefold() for skill in result}

    assert EXPECTED_SKILLS_2.issubset(normalized_skills)


def test_extraction_has_no_duplicate_skills():
    for job_description in (JOB_DESCRIPTION_1, JOB_DESCRIPTION_2):
        result = extract_required_skills(job_description)
        normalized_skills = [skill.casefold() for skill in result]

        assert len(normalized_skills) == len(set(normalized_skills))


def test_extraction_handles_empty_input():
    assert extract_required_skills("") == []


def test_extraction_handles_invalid_input():
    assert extract_required_skills(None) == []


def test_extracts_tensorflow_and_react_native():
    job_description = """
    Required skills: Python, TensorFlow, React Native.
    """

    result = extract_required_skills(job_description)
    normalized_skills = {skill.casefold() for skill in result}

    assert "tensorflow" in normalized_skills
    assert "react native" in normalized_skills
