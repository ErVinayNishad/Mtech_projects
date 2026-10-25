
import pytest

from modules.M03_nlp_information_extraction import model_skill_extractor as extractor


@pytest.mark.parametrize(
    ("skill", "expected"),
    [
        ("Python", "Python"),
        ("react.js", "React"),
        ("PyTorch Lightning", "PyTorch Lightning"),
        ("framework", None),
        ("frameworks", None),
        ("", None),
        ("   ", None),
        (None, None),
        (123, None),
    ],
)
def test_normalize_skill(skill, expected):
    assert extractor.normalize_skill(skill) == expected


class FakeGLiNER:
    def __init__(self, entities):
        self.entities = entities
        self.calls = []

    def predict_entities(self, text, labels, threshold):
        self.calls.append((text, labels, threshold))
        return self.entities


def test_extract_preserves_unknown_skill(monkeypatch):
    fake_model = FakeGLiNER(
        [{"text": "PyTorch Lightning"}]
    )
    monkeypatch.setattr(extractor, "get_model", lambda: fake_model)

    result = extractor.extract_skills_with_gliner(
        "PyTorch Lightning",
    )

    assert result == ["PyTorch Lightning"]


def test_extract_normalizes_known_alias(monkeypatch):
    fake_model = FakeGLiNER(
        [{"text": "react.js"}]
    )
    monkeypatch.setattr(extractor, "get_model", lambda: fake_model)

    result = extractor.extract_skills_with_gliner("react.js")

    assert result == ["React"]


def test_extract_removes_duplicates(monkeypatch):
    fake_model = FakeGLiNER(
        [{"text": "Python"}, {"text": "Python"}]
    )
    monkeypatch.setattr(extractor, "get_model", lambda: fake_model)

    result = extractor.extract_skills_with_gliner("Python")

    assert result == ["Python"]


def test_extract_filters_generic_terms(monkeypatch):
    fake_model = FakeGLiNER(
        [{"text": "framework"}, {"text": "frameworks"}]
    )
    monkeypatch.setattr(extractor, "get_model", lambda: fake_model)

    result = extractor.extract_skills_with_gliner("Technical skills")

    assert result == []

@pytest.mark.parametrize(
    "threshold",
    [0.0, 1.0, 0.30, 0.45],
)
def test_validate_threshold_accepts_valid_values(threshold):
    extractor.validate_threshold(threshold)


@pytest.mark.parametrize(
    "threshold",
    [-0.1, 1.1, float("nan"), float("inf"), True, "0.3", None],
)
def test_validate_threshold_rejects_invalid_values(threshold):
    with pytest.raises(ValueError):
        extractor.validate_threshold(threshold)


@pytest.mark.parametrize("text", ["", "   ", None, 123])
def test_empty_or_invalid_text_does_not_load_model(monkeypatch, text):
    def fail_if_model_loaded():
        pytest.fail("Model should not load for empty or invalid input")

    monkeypatch.setattr(extractor, "get_model", fail_if_model_loaded)

    assert extractor.extract_skills_with_gliner(text) == []

def test_normalize_skill_collapses_internal_whitespace_for_new_skills():
    assert extractor.normalize_skill("  PyTorch   Lightning  ") == "PyTorch Lightning"


@pytest.mark.parametrize(
    "generic_label",
    ["library", "cloud platforms", "devops tools", "software tools"],
)
def test_normalize_skill_filters_generic_entity_labels(generic_label):
    assert extractor.normalize_skill(generic_label) is None


def test_claimed_skill_extraction_falls_back_to_known_skill_mentions(monkeypatch):
    monkeypatch.setattr(extractor, "extract_skills_with_gliner", lambda text, threshold=0.30: ["Python"])

    claims = extractor.get_claimed_skills_with_gliner(
        "Technical Skills: Python\nWork Experience: Worked with REST APIs and Git."
    )
    skills = {item["skill"] for item in claims}

    assert {"Python", "REST APIs", "Git"}.issubset(skills)
    assert next(item for item in claims if item["skill"] == "REST APIs")["extraction_method"] == "GLiNER+known-skill fallback"


def test_known_skill_fallback_uses_boundaries_for_c_and_cplusplus():
    skills = extractor._extract_known_skill_mentions(
        "Used C++ in one project; learned SQL."
    )
    assert "C++" in skills
    assert "SQL" in skills
    assert "C" not in skills


def test_known_skill_fallback_avoids_ambiguous_go_and_c_prose():
    skills = extractor._extract_known_skill_mentions(
        "Please go to the office; this candidate received Grade C."
    )
    assert "Go" not in skills
    assert "C" not in skills
