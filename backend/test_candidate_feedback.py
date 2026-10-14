from app.services.feedback.candidate_feedback import generate_candidate_feedback

from app.services.skill_analysis.skill_gap import calculate_skill_gap
from app.services.skill_analysis.initial_analysis import analyze_skill_gap
from app.services.feedback.candidate_feedback import generate_candidate_feedback

def test_feedback_generated_when_skills_are_missing():
    analysis = {
        "status": "GAP_FOUND",
        "gap_percentage": 50.0,
        "matched_skills": ["Python", "SQL"],
        "missing_skills": ["Django", "Docker"],
    }

    feedback = generate_candidate_feedback(analysis)

    assert feedback["status"] == "GAP_FOUND"
    assert feedback["missing_skills"] == ["Django", "Docker"]
    assert len(feedback["learning_suggestions"]) == 2
    assert feedback["next_step"] == "CANDIDATE_FEEDBACK"


def test_no_gap_returns_interview_recommendation():
    analysis = {
        "status": "NO_GAP",
        "gap_percentage": 0.0,
        "matched_skills": ["Python", "SQL"],
        "missing_skills": [],
    }

    feedback = generate_candidate_feedback(analysis)

    assert feedback["status"] == "NO_GAP"
    assert feedback["learning_suggestions"] == []
    assert feedback["next_step"] == "PERSONALIZED_INTERVIEW"


def test_no_data_does_not_generate_skill_feedback():
    analysis = {
        "status": "NO_DATA",
        "gap_percentage": 0.0,
        "matched_skills": [],
        "missing_skills": [],
    }

    feedback = generate_candidate_feedback(analysis)

    assert feedback["status"] == "NO_DATA"
    assert feedback["learning_suggestions"] == []
    assert feedback["next_step"] == "PROVIDE_VALID_JOB_DESCRIPTION"


def test_nine_required_skills_generate_correct_gap_and_feedback():
    claimed_skills = [
        "AWS", "Bootstrap", "C++", "CSS", "Django", "Docker",
        "Express.js", "Git", "GitHub", "HTML", "Java",
        "JavaScript", "MongoDB", "MySQL", "Node.js", "Python",
        "React", "SQL",
    ]

    required_skills = [
        "AWS", "Django", "Docker", "Java", "Kubernetes",
        "Python", "React Native", "SQL", "TensorFlow",
    ]

    gap_result = calculate_skill_gap(claimed_skills, required_skills)
    initial_result = analyze_skill_gap(gap_result)
    feedback = generate_candidate_feedback(initial_result)

    assert gap_result["total_required"] == 9
    assert gap_result["total_matched"] == 6
    assert gap_result["total_missing"] == 3

    assert set(gap_result["missing_skills"]) == {
        "Kubernetes",
        "React Native",
        "TensorFlow",
    }

    assert initial_result["status"] == "GAP_FOUND"
    assert initial_result["gap_percentage"] == 33.33

    assert feedback["next_step"] == "CANDIDATE_FEEDBACK"
    assert len(feedback["learning_suggestions"]) == 3

