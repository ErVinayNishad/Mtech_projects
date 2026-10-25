from modules.M03_nlp_information_extraction import jd_skill_extractor as jd_extractor


def test_jd_extractor_preserves_new_open_vocabulary_skills(monkeypatch):
    monkeypatch.setattr(
        jd_extractor,
        "extract_skills_with_gliner",
        lambda text: ["PyTorch Lightning", "Rust", "PyTorch Lightning", "skills"],
    )

    assert jd_extractor.extract_required_skills(
        "We need PyTorch Lightning and Rust experience."
    ) == ["PyTorch Lightning", "Rust"]


def test_jd_extractor_fallback_finds_known_skill_missed_by_model(monkeypatch):
    monkeypatch.setattr(jd_extractor, "extract_skills_with_gliner", lambda text: [])

    assert "Kubernetes" in jd_extractor.extract_required_skills(
        "Experience deploying workloads on Kubernetes."
    )


def test_jd_extractor_keeps_react_when_both_react_and_react_native_are_required(monkeypatch):
    monkeypatch.setattr(jd_extractor, "extract_skills_with_gliner", lambda text: [])

    skills = jd_extractor.extract_required_skills(
        "Required: React Native for mobile apps and React for the web UI."
    )

    assert "React Native" in skills
    assert "React" in skills


def test_jd_extractor_does_not_count_react_native_as_react(monkeypatch):
    monkeypatch.setattr(jd_extractor, "extract_skills_with_gliner", lambda text: [])

    skills = jd_extractor.extract_required_skills(
        "Build mobile apps using React Native."
    )

    assert "React Native" in skills
    assert "React" not in skills


def test_jd_extractor_scopes_to_required_skills_section(monkeypatch):
    seen_text = []

    def fake_gliner(text):
        seen_text.append(text)
        return []

    monkeypatch.setattr(jd_extractor, "extract_skills_with_gliner", fake_gliner)
    jd_text = """Job Title: Python Backend Developer
Required Skills:
1. Python
2. Django
3. REST APIs
4. MySQL
5. Git
6. Docker
Responsibilities:
- Develop backend applications using Python and Django.
- Create and maintain REST APIs.
Qualifications:
- Basic understanding of backend development.
- Good problem-solving skills.
"""

    skills = jd_extractor.extract_required_skills(jd_text)

    assert skills == ["Django", "Docker", "Git", "MySQL", "Python", "REST APIs"]
    assert len(seen_text) == 1
    assert "Develop backend applications" not in seen_text[0]
    assert "Good problem-solving skills" not in seen_text[0]


def test_jd_extractor_preserves_unseen_skill_from_required_section(monkeypatch):
    seen_text = []

    def fake_gliner(text):
        seen_text.append(text)
        return ["LangGraph"]

    monkeypatch.setattr(jd_extractor, "extract_skills_with_gliner", fake_gliner)
    skills = jd_extractor.extract_required_skills(
        "Job Title: AI Engineer\nRequired Skills:\n- LangGraph\n- Python\n"
        "Responsibilities:\n- Develop AI applications."
    )

    assert "LangGraph" in skills
    assert "Python" in skills
    assert "Develop" not in skills
    assert "AI applications" not in skills
    assert "Develop AI applications" not in seen_text[0]
