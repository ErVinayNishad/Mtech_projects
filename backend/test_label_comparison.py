
from pathlib import Path

from app.services.resume.resume_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    extract_sections,
)

from app.services.resume.model_skill_extractor import (
    model,
    normalize_skill,
    ENTITY_LABELS,
)


BASE_DIR = Path(__file__).resolve().parent
THRESHOLD = 0.35


# Original labels before expansion
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

# Expanded labels currently added to the model file
EXPANDED_LABELS = [
    "programming language",
    "framework",
    "library",
    "database",
    "cloud platform",
    "devops tool",
    "software tool",
    "technology",
    "technical skill",
    "web technology",
    "web development technology",
    "data processing framework",
    "API technology",
    "distributed systems technology",
]


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

    for skill in skills:
        if not isinstance(skill, str):
            continue

        # Handle a multiline entity such as "Kafka\nSpark".
        parts = skill.replace("\r\n", "\n").replace("\r", "\n")
        parts = parts.replace("\n", ",").split(",")

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
    else:
        text = extract_text_from_docx(str(file_path))

    text = clean_text(text)
    sections = extract_sections(text)
    section = sections.get("technical_skills", [])

    if isinstance(section, str):
        skills_text = section
    else:
        skills_text = "\n".join(str(item) for item in section if item)

    if not skills_text.strip():
        raise ValueError(
            f"No technical skills section found in {file_path.name}"
        )

    return skills_text


def print_result(label_name, result):
    print(f"\n--- {label_name} ---")
    print(f"Precision: {result['precision']:.2%}")
    print(f"Recall:    {result['recall']:.2%}")
    print(f"F1-score:  {result['f1']:.2%}")
    print("Correct:", sorted(result["correct"]))
    print("False positives:", sorted(result["false_positive"]))
    print("Missed:", sorted(result["missed"]))


def main():
    all_results = {}

    print(f"Threshold used: {THRESHOLD}")
    print(f"Original label count: {len(ORIGINAL_LABELS)}")
    print(f"Expanded label count: {len(EXPANDED_LABELS)}")

    for relative_path, file_type, expected in EXPECTED_FILES:
        print("\n" + "=" * 70)
        print(f"FILE: {relative_path}")
        print("=" * 70)

        try:
            skills_text = load_skills_text(relative_path, file_type)
        except (FileNotFoundError, ValueError) as error:
            print(f"ERROR: {error}")
            continue

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

        print_result("Original 9 labels", original_result)
        print_result("Expanded labels", expanded_result)

        all_results.setdefault("original", []).append(original_result)
        all_results.setdefault("expanded", []).append(expanded_result)

    print("\n" + "=" * 70)
    print("OVERALL COMPARISON")
    print("=" * 70)

    for label_set in ("original", "expanded"):
        results = all_results.get(label_set, [])

        if not results:
            print(f"{label_set}: no files evaluated")
            continue

        avg_f1 = sum(result["f1"] for result in results) / len(results)
        avg_precision = sum(
            result["precision"] for result in results
        ) / len(results)
        avg_recall = sum(
            result["recall"] for result in results
        ) / len(results)

        print(f"\n{label_set.upper()} LABELS")
        print(f"Average precision: {avg_precision:.2%}")
        print(f"Average recall:    {avg_recall:.2%}")
        print(f"Average F1-score:  {avg_f1:.2%}")


if __name__ == "__main__":
    main()
