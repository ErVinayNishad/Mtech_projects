
from app.services.skill_analysis.skill_verification import (
    verify_claimed_skills,
)


def test_skill_verification_counts_evidence_correctly():
    skill_evidence = [
        {
            "skill": "Python",
            "claimed": True,
            "evidence": [
                {
                    "section": "work_experience",
                    "text": "Developed applications using Python.",
                }
            ],
        },
        {
            "skill": "Django",
            "claimed": True,
            "evidence": [
                {
                    "section": "projects",
                    "text": "Built a Django application.",
                }
            ],
        },
        {
            "skill": "Docker",
            "claimed": True,
            "evidence": [],
        },
    ]

    result = verify_claimed_skills(skill_evidence)

    assert result["total_claimed_skills"] == 3
    assert result["total_with_evidence"] == 2
    assert result["total_without_evidence"] == 1
    assert result["resume_evidence_coverage_percentage"] == 66.67

    with_evidence = [
        item["skill"]
        for item in result["skills_with_resume_evidence"]
    ]
    without_evidence = [
        item["skill"]
        for item in result["skills_without_resume_evidence"]
    ]

    assert set(with_evidence) == {"Python", "Django"}
    assert without_evidence == ["Docker"]


def test_skill_verification_handles_empty_input():
    result = verify_claimed_skills([])

    assert result["total_claimed_skills"] == 0
    assert result["total_with_evidence"] == 0
    assert result["total_without_evidence"] == 0
    assert result["resume_evidence_coverage_percentage"] == 0.0


def test_unclaimed_skill_is_not_counted():
    skill_evidence = [
        {
            "skill": "Python",
            "claimed": True,
            "evidence": [
                {
                    "section": "projects",
                    "text": "Built a Python application.",
                }
            ],
        },
        {
            "skill": "Java",
            "claimed": False,
            "evidence": [],
        },
    ]

    result = verify_claimed_skills(skill_evidence)

    assert result["total_claimed_skills"] == 1
    assert result["total_with_evidence"] == 1
    assert result["total_without_evidence"] == 0
    assert result["resume_evidence_coverage_percentage"] == 100.0
