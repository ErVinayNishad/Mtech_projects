"""HTTP layer: validates requests and orchestrates the five connected modules."""
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from modules.M01_input_sources.input_validation import resolve_jd_input
from modules.M02_document_processing.document_processing import extract_document_text
from modules.M03_nlp_information_extraction.resume_parser import extract_sections, extract_personal_details
from modules.M03_nlp_information_extraction.skill_evidence import extract_skill_evidence

router = APIRouter()

async def _read_upload(upload: UploadFile) -> bytes:
    try:
        return await upload.read()
    finally:
        await upload.close()

def _resume_payload(filename: str, content: bytes) -> dict:
    text = extract_document_text(filename, content)
    sections = extract_sections(text)
    personal = extract_personal_details(text)
    # Extract claims from the complete resume, not only the technical-skills
    # heading. Skills can also be explicitly claimed in projects, experience,
    # and certifications (e.g. REST APIs mentioned in work experience).
    from modules.M03_nlp_information_extraction.model_skill_extractor import get_claimed_skills_with_gliner
    skills = get_claimed_skills_with_gliner(text, section_name="resume")
    evidence = extract_skill_evidence(sections, skills)
    return {"filename": Path(filename).name, "file_type": Path(filename).suffix.lower()[1:], "text": text, "personal_details": personal, "sections": sections, "claimed_skills": skills, "skill_evidence": evidence}

@router.get("/")
def home(): return {"message": "Resume Skill Verification API is running", "modules": 5}

@router.get("/health")
def health(): return {"status": "healthy"}

@router.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    payload = _resume_payload(file.filename or "", await _read_upload(file))
    return {"filename": payload["filename"], "file_type": payload["file_type"], "text_length": len(payload["text"]), "extracted_text": payload["text"], "personal_details": payload["personal_details"], "sections": payload["sections"], "claimed_skills": payload["claimed_skills"], "skill_evidence": payload["skill_evidence"], "message": "Resume parsed successfully."}

@router.post("/api/job-description/analyze")
async def analyze_jd(job_description: str | None = Form(None), jd_file: UploadFile | None = File(None)):
    kind = resolve_jd_input(job_description, jd_file)
    if kind == "text": jd_text = job_description.strip()
    else: jd_text = extract_document_text(jd_file.filename or "", await _read_upload(jd_file))
    from modules.M03_nlp_information_extraction.jd_skill_extractor import extract_required_skills
    skills = extract_required_skills(jd_text)
    return {"input_type": kind, "required_skills": skills, "total_required_skills": len(skills), "job_description_length": len(jd_text), "message": "Job description analyzed successfully."}

@router.post("/api/skill-gap/analyze")
async def analyze_gap(file: UploadFile = File(...), job_description: str | None = Form(None), jd_file: UploadFile | None = File(None)):
    kind = resolve_jd_input(job_description, jd_file)
    jd_text = job_description.strip() if kind == "text" else extract_document_text(jd_file.filename or "", await _read_upload(jd_file))
    resume = _resume_payload(file.filename or "", await _read_upload(file))
    from modules.M03_nlp_information_extraction.jd_skill_extractor import extract_required_skills
    from modules.M04_semantic_skill_matching.skill_matching import calculate_skill_gap
    from modules.M05_initial_skill_gap.initial_analysis import analyze_skill_gap
    from modules.M05_initial_skill_gap.candidate_feedback import generate_candidate_feedback
    required = extract_required_skills(jd_text)
    gap = calculate_skill_gap(resume["claimed_skills"], required, resume["skill_evidence"])
    analysis = analyze_skill_gap(gap)
    feedback = generate_candidate_feedback(analysis)
    return {"filename": resume["filename"], "jd_input_type": kind, "required_skills": required, "claimed_skills": [x.get("skill", str(x)) if isinstance(x, dict) else str(x) for x in resume["claimed_skills"]], "skill_evidence": resume["skill_evidence"], "skill_gap": gap, "initial_analysis": analysis, "candidate_feedback": feedback, "message": "Initial skill gap analysis completed."}
