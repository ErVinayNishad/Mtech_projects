
from pathlib import Path

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

MEDIUM_THRESHOLDS = [0.30, 0.35, 0.45]


EXPECTED_FILES = [
    (
        "uploads/resume1.pdf",
        "PDF",
        {
            "python", "java", "javascript", "c++",
            "html", "css", "react", "bootstrap",
            "node.js", "express.js", "django",
            "mysql", "mongodb", "sql", "git",
            "github", "docker", "aws",
        },
    ),
    (
        "uploads/resume1.docx",
        "DOCX",
        {
            "grpc", "spring boot", "django", "react",
            "kafka", "spark", "gcp", "aws",
            "kubernetes", "terraform", "datadog",
        },
    ),
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
        if precision + recall else 0.0
    )

    result = {
        "model": model_name,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "correct": correct,
        "false_positive": false_positive,
        "missed": missed,
    }

    print(f"\n--- {model_name} ---")
    print("Predicted:", sorted(predicted))
    print("Correct:", sorted(correct))
    print("False positives:", sorted(false_positive))
    print("Missed:", sorted(missed))
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1-score:  {f1:.2%}")

    return result


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

    print("\n" + "=" * 70)
    print(f"FILE: {file_path.name} | TYPE: {file_type}")
    print("=" * 70)

    if not file_path.is_file():
        print(f"ERROR: File not found: {file_path}")
        return []

    try:
        skills_text = load_skills_text(file_path, file_type)
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}")
        return []

    print("\nTechnical skills text:")
    print(skills_text)

    results = []

    # Medium model: threshold comparison
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

    # Small model: existing default threshold
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


def print_summary(results):
    print("\n" + "=" * 90)
    print("FINAL COMPARISON SUMMARY")
    print("=" * 90)

    if not results:
        print("No results available.")
        return

    print(
        f"{'File':<18}{'Model':<32}"
        f"{'Precision':>12}{'Recall':>10}{'F1':>10}"
    )
    print("-" * 82)

    for result in results:
        print(
            f"{result['file']:<18}"
            f"{result['model']:<32}"
            f"{result['precision']:>11.2%} "
            f"{result['recall']:>9.2%} "
            f"{result['f1']:>9.2%}"
        )

    print("\nMEDIUM MODEL AVERAGE F1")

    for threshold in MEDIUM_THRESHOLDS:
        matching = [
            item for item in results
            if item["model"] == f"Medium v2.1 | threshold={threshold}"
        ]

        if matching:
            average_f1 = sum(item["f1"] for item in matching) / len(matching)
            print(
                f"Threshold {threshold}: {average_f1:.2%} "
                f"({len(matching)} file(s))"
            )


if __name__ == "__main__":
    all_results = []

    for relative_path, file_type, expected in EXPECTED_FILES:
        all_results.extend(
            evaluate_file(relative_path, file_type, expected)
        )

    print_summary(all_results)
