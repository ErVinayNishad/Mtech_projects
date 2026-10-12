
from pathlib import Path

from app.services.resume.resume_parser import (
    extract_text_from_docx,
    clean_text,
    extract_sections,
)

from app.services.resume.model_skill_extractor import (
    model,
    ENTITY_LABELS,
)


BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "uploads" / "resume1.docx"

THRESHOLD = 0.01

LABEL_EXPERIMENTS = {
    "Original labels": ENTITY_LABELS,

    "Framework + technical skill": [
        "framework",
        "technical skill",
    ],

    "Framework + technology": [
        "framework",
        "technology",
    ],

    "Web-related labels": [
        "framework",
        "technology",
        "technical skill",
        "web technology",
        "web development technology",
    ],

    "All original + additional labels": [
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
    ],
}


def get_technical_skills_text():
    if not FILE_PATH.is_file():
        raise FileNotFoundError(f"File not found: {FILE_PATH}")

    text = extract_text_from_docx(str(FILE_PATH))
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
        raise ValueError("Technical skills section not found.")

    return skills_text


def main():
    skills_text = get_technical_skills_text()

    print("Input text:")
    print(skills_text)

    print("\nReact confidence comparison")
    print(f"Diagnostic threshold: {THRESHOLD}")
    print("Production threshold remains unchanged.\n")

    results = []

    for experiment_name, labels in LABEL_EXPERIMENTS.items():
        entities = model.predict_entities(
            skills_text,
            labels,
            threshold=THRESHOLD,
        )

        react_entities = [
            entity for entity in entities
            if entity.get("text", "").strip().lower() == "react"
        ]

        print("=" * 65)
        print(experiment_name)
        print("Labels:", labels)

        if react_entities:
            for entity in react_entities:
                score = entity.get("score")
                print(
                    f"React detected | "
                    f"Label: {entity.get('label')} | "
                    f"Score: {score}"
                )

                results.append(
                    (experiment_name, score, entity.get("label"))
                )
        else:
            print("React was not detected.")

    print("\n" + "=" * 65)
    print("SUMMARY")

    if not results:
        print("React was not detected in any experiment.")
        return

    for name, score, label in results:
        print(f"{name}: score={score}, label={label}")

    best = max(results, key=lambda item: item[1])
    print(
        f"\nHighest observed React score: {best[1]} "
        f"({best[0]}, label={best[2]})"
    )


if __name__ == "__main__":
    main()
