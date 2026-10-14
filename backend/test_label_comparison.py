import json
from pathlib import Path

import pytest

from app.services.resume.resume_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    extract_sections,
)
from app.services.resume.model_skill_extractor import (
    model,
    normalize_skill,
)


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "evaluation_dataset.json"
THRESHOLD = 0.35

ORIGINAL_LABELS = [
    "programming language",
    "framework",
    "library",
    "database",
    "cloud platform",
    "devops tool",
    "software tool",
    "technology",
    "technical skill",
]

EXPANDED_LABELS = [
    *ORIGINAL_LABELS,
    "web technology",
    "web development technology",
    "data processing framework",
    "API technology",
    "distributed systems technology",
]


def load_evaluation_dataset():
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    samples = dataset.get("samples", [])

    if not isinstance(samples, list) or not samples:
        raise ValueError("Evaluation dataset must contain samples.")

    for sample in samples:
        required_fields = {
            "id", "file", "file_type", "expected_skills"
        }

        if not required_fields.issubset(sample):
            raise ValueError(
                f"Invalid dataset sample: {sample.get('id', 'unknown')}"
            )

        if not isinstance(sample["expected_skills"], list):
            raise ValueError(
                f"expected_skills must be a list: {sample['id']}"
            )

    return dataset


DATASET = load_evaluation_dataset()
EXPECTED_FILES = [
    (
        sample["file"],
        sample["file_type"],
        set(sample["expected_skills"]),
    )
    for sample in DATASET["samples"]
]


def normalize_for_evaluation(skills):
    normalized = set()

    aliases = {
        "react.js": "react",
        "reactjs": "react",
        "node": "node.js",
        "nodejs": "node.js",
        "express": "express.js",
        "expressjs": "express.js",
        "html5": "html",
        "css3": "css",
    }

    for skill in skills or []:
        if not isinstance(skill, str):
            continue

        parts = (
            skill.replace("\r\n", "\n")
            .replace("\r", "\n")
            .replace("\n", ",")
            .split(",")
        )

        for part in parts:
            item = part.strip().lower()
            if item:
                normalized.add(aliases.get(item, item))

    return normalized


def extract_with_labels(text, labels):
    entities = model.predict_entities(
        text,
        labels,
        threshold=THRESHOLD,
    )

    skills = []

    for entity in entities:
        skill = normalize_skill(entity.get("text", ""))

        if skill and skill not in skills:
            skills.append(skill)

    return skills


def evaluate(predicted, expected):
    predicted = normalize_for_evaluation(predicted)
    expected = normalize_for_evaluation(expected)

    correct = predicted & expected
    false_positive = predicted - expected
    missed = expected - predicted

    precision = len(correct) / len(predicted) if predicted else 0.0
    recall = len(correct) / len(expected) if expected else 0.0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "correct": correct,
        "false_positive": false_positive,
        "missed": missed,
    }


def load_skills_text(relative_path, file_type):
    file_path = BASE_DIR / relative_path

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_type == "PDF":
        text = extract_text_from_pdf(str(file_path))
    elif file_type == "DOCX":
        text = extract_text_from_docx(str(file_path))
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    text = clean_text(text)
    sections = extract_sections(text)
    section = sections.get("technical_skills", [])

    if isinstance(section, str):
        skills_text = section
    else:
        skills_text = "\n".join(
            str(item) for item in section if item
        )

    if not skills_text.strip():
        raise ValueError(
            f"No technical skills section found in {file_path.name}"
        )

    return skills_text


def print_result(label_name, result):
    print(f"\n{label_name}")
    print(f"Precision: {result['precision']:.2%}")
    print(f"Recall:    {result['recall']:.2%}")
    print(f"F1 Score:  {result['f1']:.2%}")
    print(f"Correct skills: {sorted(result['correct'])}")
    print(f"False positives: {sorted(result['false_positive'])}")
    print(f"Missed skills: {sorted(result['missed'])}")


def run_label_comparison(relative_path, file_type, expected):
    skills_text = load_skills_text(relative_path, file_type)

    original_predictions = extract_with_labels(
        skills_text,
        ORIGINAL_LABELS,
    )
    expanded_predictions = extract_with_labels(
        skills_text,
        EXPANDED_LABELS,
    )

    original_result = evaluate(original_predictions, expected)
    expanded_result = evaluate(expanded_predictions, expected)

    print("\n" + "=" * 75)
    print(f"Resume: {relative_path}")
    print(f"Threshold: {THRESHOLD}")
    print(f"Dataset: {DATASET.get('dataset_name', 'unnamed')}")
    print("=" * 75)

    print_result(
        f"Original labels ({len(ORIGINAL_LABELS)})",
        original_result,
    )
    print_result(
        f"Expanded labels ({len(EXPANDED_LABELS)})",
        expanded_result,
    )

    difference = expanded_result["f1"] - original_result["f1"]
    print(f"\nF1 difference (expanded - original): {difference:+.2%}")

    return original_result, expanded_result


@pytest.mark.parametrize(
    "relative_path,file_type,expected",
    EXPECTED_FILES,
    ids=[sample["id"] for sample in DATASET["samples"]],
)
def test_original_and_expanded_label_comparison(
    relative_path,
    file_type,
    expected,
):
    original_result, expanded_result = run_label_comparison(
        relative_path,
        file_type,
        expected,
    )

    for result in (original_result, expanded_result):
        assert 0.0 <= result["precision"] <= 1.0
        assert 0.0 <= result["recall"] <= 1.0
        assert 0.0 <= result["f1"] <= 1.0


@pytest.mark.parametrize(
    "predicted,expected,expected_f1",
    [
        (["Python", "Django"], ["Python", "Django"], 1.0),
        (["Python"], ["Python", "Django"], 2 / 3),
        ([], ["Python"], 0.0),
        (["Python"], [], 0.0),
    ],
)
def test_evaluation_f1_calculation(predicted, expected, expected_f1):
    result = evaluate(predicted, expected)
    assert result["f1"] == pytest.approx(expected_f1)


def test_normalization_handles_aliases_and_duplicates():
    result = normalize_for_evaluation([
        "React.js",
        "react",
        "NodeJS",
        "Node.js",
        "HTML5",
        "",
        None,
    ])

    assert result == {"react", "node.js", "html"}


def test_label_sets_have_expected_sizes():
    assert len(ORIGINAL_LABELS) == 9
    assert len(EXPANDED_LABELS) == 14
    assert len(set(EXPANDED_LABELS)) == 14
    assert set(ORIGINAL_LABELS).issubset(set(EXPANDED_LABELS))


if __name__ == "__main__":
    for relative_path, file_type, expected in EXPECTED_FILES:
        run_label_comparison(relative_path, file_type, expected)
