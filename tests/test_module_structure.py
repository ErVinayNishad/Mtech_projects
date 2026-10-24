from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_five_modules_exist():
    expected = ["M01_input_sources", "M02_document_processing", "M03_nlp_information_extraction", "M04_semantic_skill_matching", "M05_initial_skill_gap"]
    assert all((ROOT / "modules" / name / "__init__.py").exists() for name in expected)

def test_api_layer_does_not_contain_document_parsing_implementation():
    source = (ROOT / "app" / "api" / "routes.py").read_text(encoding="utf-8")
    assert "pymupdf.open" not in source and "Document(BytesIO" not in source
