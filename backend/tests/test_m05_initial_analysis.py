from modules.M05_initial_skill_gap.initial_analysis import analyze_skill_gap
from modules.M05_initial_skill_gap.candidate_feedback import generate_candidate_feedback


def test_semantic_match_does_not_remain_a_false_missing_skill():
    gap = {
        "matched_skills": [],
        "missing_skills": ["React.js"],
        "total_required": 1,
        "semantic_matches": [
            {
                "required_skill": "React.js",
                "matched_resume_skill": "React",
                "similarity": 0.96,
                "classification": "HIGH",
                "status": "Well claimed",
            }
        ],
    }

    analysis = analyze_skill_gap(gap)
    feedback = generate_candidate_feedback(analysis)

    assert analysis["status"] == "NO_GAP"
    assert analysis["missing_skills"] == []
    assert analysis["exact_missing_skills"] == ["React.js"]
    assert feedback["next_step"] == "PERSONALIZED_INTERVIEW"
    assert feedback["learning_suggestions"] == []


def test_low_semantic_match_triggers_feedback_for_that_skill_only():
    gap = {
        "matched_skills": ["Python"],
        "missing_skills": ["Rust", "React.js"],
        "total_required": 3,
        "semantic_matches": [
            {"required_skill": "Python", "classification": "HIGH"},
            {"required_skill": "React.js", "classification": "HIGH"},
            {"required_skill": "Rust", "classification": "LOW"},
        ],
    }

    analysis = analyze_skill_gap(gap)
    feedback = generate_candidate_feedback(analysis)

    assert analysis["status"] == "GAP_FOUND"
    assert analysis["missing_skills"] == ["Rust"]
    assert analysis["gap_percentage"] == 33.33
    assert [item["skill"] for item in feedback["learning_suggestions"]] == ["Rust"]


def test_exact_match_fallback_when_semantic_results_are_absent():
    analysis = analyze_skill_gap({
        "matched_skills": ["Python"],
        "missing_skills": ["Rust"],
        "total_required": 2,
        "semantic_matches": [],
    })

    assert analysis["status"] == "GAP_FOUND"
    assert analysis["missing_skills"] == ["Rust"]
    assert analysis["gap_percentage"] == 50.0


def test_m04_public_match_counts_align_with_semantic_analysis(monkeypatch):
    from modules.M04_semantic_skill_matching import skill_matching

    monkeypatch.setattr(
        skill_matching,
        "calculate_semantic_skill_matches",
        lambda claimed, required, evidence=None: [
            {"required_skill": "Python", "classification": "HIGH", "matched_resume_skill": "Python"},
            {"required_skill": "REST APIs", "classification": "HIGH", "matched_resume_skill": "REST APIs"},
            {"required_skill": "Rust", "classification": "LOW", "matched_resume_skill": None},
        ],
    )
    gap = skill_matching.calculate_skill_gap(
        ["Python", "REST APIs"], ["Python", "REST APIs", "Rust"]
    )
    analysis = analyze_skill_gap(gap)

    assert gap["matched_skills"] == ["Python", "REST APIs"]
    assert gap["missing_skills"] == ["Rust"]
    assert gap["total_matched"] == 2
    assert gap["total_missing"] == 1
    assert gap["exact_missing_skills"] == ["Rust"]
    assert analysis["missing_skills"] == ["Rust"]
