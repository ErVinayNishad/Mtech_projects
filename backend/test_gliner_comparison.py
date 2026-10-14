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
    extract_skills_with_gliner,
)
from app.services.llm_skill_extractor import (
    extract_skills_with_model,
)


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "evaluation_dataset.json"
MEDIUM_THRESHOLDS = [0.30, 0.35, 0.45]


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


ALIASES = {
    "react.js": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "express": "express.js",
    "expressjs": "express.js",
    "html5": "html",
    "css3": "css",
}


def normalize_skills(skills):
    normalized = set()

    for skill in skills or []:
        if not isinstance(skill, str):
            continue

        skill = skill.strip()
        if not skill:
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
                normalized.add(ALIASES.get(item, item))

    return normalized


def evaluate_model(model_name, predicted_skills, expected_skills):
    predicted = normalize_skills(predicted_skills)
    expected = normalize_skills(expected_skills)

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
        "model": model_name,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "correct": correct,
        "false_positive": false_positive,
        "missed": missed,
    }


def load_skills_text(file_path, file_type):
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


def evaluate_file(relative_path, file_type, expected_skills):
    file_path = BASE_DIR / relative_path

    if not file_path.is_file():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    skills_text = load_skills_text(file_path, file_type)
    results = []

    for threshold in MEDIUM_THRESHOLDS:
        predicted = extract_skills_with_gliner(
            skills_text,
            threshold=threshold,
        )

        result = evaluate_model(
            f"Medium v2.1 | threshold={threshold}",
            predicted,
            expected_skills,
        )
        result["file"] = file_path.name
        result["threshold"] = threshold
        results.append(result)

    predicted_small = extract_skills_with_model(skills_text)

    result = evaluate_model(
        "Small v2.5 | default threshold",
        predicted_small,
        expected_skills,
    )
    result["file"] = file_path.name
    result["threshold"] = "default"
    results.append(result)

    return results


def print_evaluation_report(all_results):
    print("\n" + "=" * 90)
    print("GLiNER MODEL COMPARISON REPORT")
    print(f"Dataset: {DATASET.get('dataset_name', 'unnamed')}")
    print(f"Samples: {len(DATASET['samples'])}")
    print("=" * 90)

    for result in all_results:
        print(f"\nResume: {result['file']}")
        print(f"Model: {result['model']}")
        print(f"Precision: {result['precision']:.2%}")
        print(f"Recall:    {result['recall']:.2%}")
        print(f"F1 Score:  {result['f1']:.2%}")
        print(f"Correct skills: {sorted(result['correct'])}")
        print(f"False positives: {sorted(result['false_positive'])}")
        print(f"Missed skills: {sorted(result['missed'])}")

    print("\n" + "-" * 90)
    print("AVERAGE F1 BY MODEL / THRESHOLD")
    print("-" * 90)

    groups = {}

    for result in all_results:
        groups.setdefault(result["model"], []).append(result["f1"])

    for model_name, scores in groups.items():
        average_f1 = sum(scores) / len(scores)
        print(f"{model_name:<40} Average F1: {average_f1:.2%}")

    print("\nNote: Results are preliminary.")
    print("The current dataset contains only two resumes.")


@pytest.mark.parametrize(
    "relative_path,file_type,expected_skills",
    EXPECTED_FILES,
    ids=[sample["id"] for sample in DATASET["samples"]],
)
def test_model_comparison_returns_metrics(
    relative_path,
    file_type,
    expected_skills,
):
    results = evaluate_file(relative_path, file_type, expected_skills)

    assert len(results) == len(MEDIUM_THRESHOLDS) + 1

    for result in results:
        assert 0.0 <= result["precision"] <= 1.0
        assert 0.0 <= result["recall"] <= 1.0
        assert 0.0 <= result["f1"] <= 1.0
        assert isinstance(result["correct"], set)
        assert isinstance(result["false_positive"], set)
        assert isinstance(result["missed"], set)


@pytest.mark.parametrize(
    "predicted,expected,expected_f1",
    [
        (["Python", "Django"], ["Python", "Django"], 1.0),
        (["Python"], ["Python", "Django"], 2 / 3),
        ([], ["Python"], 0.0),
        (["Python"], [], 0.0),
    ],
)
def test_evaluate_model_f1(predicted, expected, expected_f1):
    result = evaluate_model("Test model", predicted, expected)
    assert result["f1"] == pytest.approx(expected_f1)


def test_normalize_skills_handles_aliases_and_duplicates():
    result = normalize_skills([
        "React.js",
        "react",
        "NodeJS",
        "Node.js",
        " HTML5 ",
        "",
        None,
    ])

    assert result == {"react", "node.js", "html"}


def test_load_skills_text_rejects_unsupported_file_type():
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_skills_text(Path("resume.txt"), "TXT")


if __name__ == "__main__":
    all_results = []

    for relative_path, file_type, expected_skills in EXPECTED_FILES:
        all_results.extend(
            evaluate_file(relative_path, file_type, expected_skills)
        )

    print_evaluation_report(all_results)
