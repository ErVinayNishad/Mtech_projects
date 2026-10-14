
from app.services.skill_analysis.skill_gap import calculate_skill_gap
from app.services.skill_analysis.initial_analysis import analyze_skill_gap


def test_skill_gap_matches_required_skills():
    result = calculate_skill_gap(
        ["Python", "Django", "REST APIs"],
        ["Python", "Django", "REST API", "Docker"],
    )

    assert result["total_required"] == 4
    assert result["total_matched"] == 3
    assert result["total_missing"] == 1
    assert result["missing_skills"] == ["Docker"]


def test_skill_gap_normalizes_case_and_whitespace():
    result = calculate_skill_gap(
        ["  PYTHON  ", "rest api"],
        ["python", "REST APIs"],
    )

    assert result["total_matched"] == 2
    assert result["total_missing"] == 0


def test_skill_gap_handles_empty_inputs():
    result = calculate_skill_gap([], [])

    assert result["total_required"] == 0
    assert result["total_matched"] == 0
    assert result["total_missing"] == 0


def test_initial_analysis_detects_gap():
    result = analyze_skill_gap({
        "matched_skills": ["Python", "Django"],
        "missing_skills": ["Docker"],
        "total_required": 3,
    })

    assert result["status"] == "GAP_FOUND"
    assert result["gap_percentage"] == 33.33


def test_initial_analysis_detects_no_gap():
    result = analyze_skill_gap({
        "matched_skills": ["Python", "Django"],
        "missing_skills": [],
        "total_required": 2,
    })

    assert result["status"] == "NO_GAP"
    assert result["gap_percentage"] == 0.0


def test_initial_analysis_handles_no_required_skills():
    result = analyze_skill_gap({
        "matched_skills": [],
        "missing_skills": [],
        "total_required": 0,
    })

    assert result["status"] == "NO_DATA"
