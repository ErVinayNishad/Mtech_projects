import re

import pymupdf
from docx import Document


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file.
    Ensures the PDF document is closed even if extraction fails.
    """

    with pymupdf.open(file_path) as doc:
        text_parts = []

        for page in doc:
            page_text = page.get_text()

            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)
    """
    Extract text from a PDF file.
    """

    doc = pymupdf.open(file_path)

    text = ""

    for page in doc:
        page_text = page.get_text()

        if page_text:
            text += page_text + "\n"

    doc.close()

    return text


# ============================================================
# DOCX TEXT EXTRACTION
# ============================================================

def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX file.

    Extracts:
    - Normal paragraphs
    - Table contents
    """

    document = Document(file_path)

    text = ""

    # --------------------------------------------------------
    # Normal paragraphs
    # --------------------------------------------------------

    for paragraph in document.paragraphs:

        value = paragraph.text.strip()

        if value:
            text += value + "\n"

    # --------------------------------------------------------
    # Tables
    # --------------------------------------------------------

    for table in document.tables:

        for row in table.rows:

            row_text = []

            for cell in row.cells:

                value = cell.text.strip()

                if value:
                    row_text.append(value)

            if row_text:
                text += " | ".join(row_text) + "\n"

    return text


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):
    """
    Clean extracted resume text.

    - Replaces tabs with spaces
    - Removes extra spaces
    - Removes empty lines
    """

    lines = []

    for line in text.splitlines():

        # Replace tabs
        line = line.replace("\t", " ")

        # Normalize multiple spaces
        line = " ".join(line.split())

        if line:
            lines.append(line)

    return "\n".join(lines)


# ============================================================
# NORMALIZE SPACED HEADINGS
# ============================================================

def normalize_heading(text):
    """
    Normalize resume section headings.

    Handles headings such as:

    PROFESSIONAL SUMMARY
    P R O F E S S I O N A L   S U M M A R Y
    C O R E   C O M P E T E N C I E S
    """

    if not text:
        return ""

    text = text.strip()

    # --------------------------------------------------------
    # Remove common heading symbols
    # --------------------------------------------------------

    text = re.sub(
        r"^[•▪●○◦\-:|]+\s*",
        "",
        text
    )

    # --------------------------------------------------------
    # Lowercase
    # --------------------------------------------------------

    text = text.lower()

    # --------------------------------------------------------
    # Normalize spaces
    # --------------------------------------------------------

    text = " ".join(text.split())

    # --------------------------------------------------------
    # Handle fully spaced headings
    #
    # Example:
    # P R O F E S S I O N A L
    # --------------------------------------------------------

    tokens = text.split()

    if len(tokens) >= 3:

        if all(
            len(token) == 1 and token.isalpha()
            for token in tokens
        ):
            text = "".join(tokens)

    # --------------------------------------------------------
    # Handle partially spaced headings
    #
    # Example:
    # C O R E   C O M P E T E N C I E S
    # --------------------------------------------------------

    parts = re.split(r"\s{2,}", text)

    if len(parts) > 1:

        fixed_parts = []

        for part in parts:

            tokens = part.split()

            if (
                len(tokens) >= 3
                and all(
                    len(token) == 1 and token.isalpha()
                    for token in tokens
                )
            ):

                fixed_parts.append(
                    "".join(tokens)
                )

            else:

                fixed_parts.append(part)

        text = " ".join(fixed_parts)

    # --------------------------------------------------------
    # Final space normalization
    # --------------------------------------------------------

    text = " ".join(text.split())

    return text.strip()


# ============================================================
# SECTION NAME
# ============================================================

def get_section_name(line):
    """
    Identify the normalized section name of a resume heading.
    """

    normalized = normalize_heading(line)

    section_headings = {

        # ----------------------------------------------------
        # Career / Summary
        # ----------------------------------------------------

        "career objective": "career_objective",
        "objective": "career_objective",
        "summary": "career_objective",
        "professional summary": "career_objective",
        "profile": "career_objective",
        "professional profile": "career_objective",

        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        "technical skills": "technical_skills",
        "technical skill": "technical_skills",
        "skills": "technical_skills",
        "skill": "technical_skills",
        "core skills": "technical_skills",
        "core competencies": "technical_skills",
        "competencies": "technical_skills",
        "core competency": "technical_skills",
        "technologies": "technical_skills",
        "technology": "technical_skills",
        "technical competencies": "technical_skills",

        # ----------------------------------------------------
        # Skill Categories
        # ----------------------------------------------------

        "programming languages": "technical_skills",
        "programming language": "technical_skills",
        "frameworks": "technical_skills",
        "framework": "technical_skills",
        "platforms": "technical_skills",
        "tools": "technical_skills",
        "tools and platforms": "technical_skills",
        "tools & platforms": "technical_skills",
        "web technologies": "technical_skills",
        "web technology": "technical_skills",
        "databases": "technical_skills",
        "database": "technical_skills",

        # ----------------------------------------------------
        # Education
        # ----------------------------------------------------

        "education": "education",
        "academic background": "education",
        "academic qualification": "education",
        "academic qualifications": "education",
        "qualifications": "education",
        "qualification": "education",
        "educational background": "education",
        "educational qualifications": "education",

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        "experience": "work_experience",
        "work experience": "work_experience",
        "professional experience": "work_experience",
        "work history": "work_experience",
        "employment history": "work_experience",
        "professional background": "work_experience",
        "web development experience": "work_experience",
        "career history": "work_experience",

        # ----------------------------------------------------
        # Projects
        # ----------------------------------------------------

        "projects": "projects",
        "project": "projects",
        "academic projects": "projects",
        "personal projects": "projects",
        "technical projects": "projects",
        "academic project": "projects",
        "personal project": "projects",

        "m tech project": "mtech_project",
        "m.tech project": "mtech_project",
        "mtech project": "mtech_project",

        # ----------------------------------------------------
        # Certifications
        # ----------------------------------------------------

        "certifications": "certifications",
        "certification": "certifications",
        "certs": "certifications",
        "professional development": "certifications",
        "professional development courses": "certifications",
        "courses": "certifications",
        "training": "certifications",
        "trainings": "certifications",

        # ----------------------------------------------------
        # Achievements
        # ----------------------------------------------------

        "achievements": "achievements",
        "achievement": "achievements",
        "awards": "achievements",
        "award": "achievements",
        "honors": "achievements",
        "honours": "achievements",

        # ----------------------------------------------------
        # Activities
        # ----------------------------------------------------

        "activities": "activities",
        "activity": "activities",
        "extracurricular activities": "activities",
        "extracurricular activity": "activities",
        "extra curricular activities": "activities",
        "extra curricular activity": "activities",

        # ----------------------------------------------------
        # Combined Certifications / Achievements
        # ----------------------------------------------------

        "certifications & achievements":
            "certifications_achievements",

        "certifications and achievements":
            "certifications_achievements",

        "certification & achievements":
            "certifications_achievements",

        "certification and achievements":
            "certifications_achievements",

        # ----------------------------------------------------
        # Areas of Interest
        # ----------------------------------------------------

        "areas of interest": "areas_of_interest",
        "areas of interests": "areas_of_interest",
        "interests": "areas_of_interest",
        "professional interests": "areas_of_interest",

        # ----------------------------------------------------
        # Hobbies
        # ----------------------------------------------------

        "hobbies": "hobbies_interests",
        "hobbies & interests": "hobbies_interests",
        "hobbies and interests": "hobbies_interests",

        # ----------------------------------------------------
        # Languages
        # ----------------------------------------------------

        "language": "languages",
        "languages": "languages",
        "spoken languages": "languages",

        # ----------------------------------------------------
        # Personal Details
        # ----------------------------------------------------

        "personal details": "personal_details",
        "personal information": "personal_details",
        "contact": "personal_details",
        "contact information": "personal_details",
        "contact details": "personal_details",
    }

    return section_headings.get(normalized)


# ============================================================
# EXTRACT RESUME SECTIONS
# ============================================================

def extract_sections(text):
    """
    Extract resume sections based on recognized headings.
    """

    sections = {}

    current_section = None

    lines = text.splitlines()

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        section_name = get_section_name(line)

        # ----------------------------------------------------
        # New section detected
        # ----------------------------------------------------

        if section_name:

            current_section = section_name

            if current_section not in sections:
                sections[current_section] = []

            continue

        # ----------------------------------------------------
        # Add content to current section
        # ----------------------------------------------------

        if current_section:
            sections[current_section].append(line)

    return sections


# ============================================================
# PERSONAL DETAILS
# ============================================================

def extract_personal_details(text):
    """
    Extract basic personal information:

    - Name
    - Email
    - Phone
    - Location
    """

    personal_details = {
        "name": None,
        "email": None,
        "phone": None,
        "location": None
    }

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # ========================================================
    # EMAIL
    # ========================================================

    email_pattern = (
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}"
    )

    for line in lines:

        match = re.search(
            email_pattern,
            line
        )

        if match:

            personal_details["email"] = match.group(0)

            break

    # ========================================================
    # PHONE
    # ========================================================

    phone_patterns = [

        # Indian phone
        r"(?:\+91[\s-]?)?[6-9]\d{9}",

        # US phone
        r"\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}",

        # Generic phone
        r"\+?\d[\d\s().-]{8,}\d"
    ]

    # --------------------------------------------------------
    # First search labelled phone
    # --------------------------------------------------------

    for line in lines:

        lower_line = line.lower()

        if (
            "phone" in lower_line
            or "mobile" in lower_line
            or "contact" in lower_line
        ):

            for pattern in phone_patterns:

                match = re.search(
                    pattern,
                    line
                )

                if match:

                    personal_details["phone"] = (
                        match.group(0).strip()
                    )

                    break

            if personal_details["phone"]:
                break

    # --------------------------------------------------------
    # Search anywhere if not found
    # --------------------------------------------------------

    if personal_details["phone"] is None:

        for line in lines:

            for pattern in phone_patterns:

                match = re.search(
                    pattern,
                    line
                )

                if match:

                    personal_details["phone"] = (
                        match.group(0).strip()
                    )

                    break

            if personal_details["phone"]:
                break

    # ========================================================
    # NAME
    # ========================================================

    ignored_words = [
        "resume",
        "curriculum vitae",
        "cv",
        "email",
        "phone",
        "mobile",
        "contact",
        "address",
        "linkedin",
        "github",
        "software engineer",
        "senior software engineer",
        "developer",
        "engineer",
        "professional",
        "summary",
        "profile"
    ]

    # --------------------------------------------------------
    # Usually name appears near beginning
    # --------------------------------------------------------

    for line in lines[:15]:

        lower_line = line.lower()

        # Email
        if "@" in line:
            continue

        # Phone
        if personal_details["phone"]:

            if personal_details["phone"] in line:
                continue

        # URLs
        if (
            "http://" in lower_line
            or "https://" in lower_line
            or "github.com" in lower_line
            or "linkedin.com" in lower_line
        ):
            continue

        # Ignore obvious labels
        if any(
            word in lower_line
            for word in ignored_words
        ):
            continue

        words = line.split()

        if 1 <= len(words) <= 5 and len(line) <= 60:

            # Avoid sentence-like lines
            if any(
                char in line
                for char in [".", ":", "|", "—"]
            ):
                continue

            # Avoid lines with many digits
            digit_count = sum(
                char.isdigit()
                for char in line
            )

            if digit_count > 3:
                continue

            personal_details["name"] = line

            break

    # ========================================================
    # LOCATION
    # ========================================================

    # --------------------------------------------------------
    # Explicit location/address labels
    # --------------------------------------------------------

    location_patterns = [

        r"(?:location|address)\s*[:\-]\s*(.+)",

        r"(?:based in|located in)\s+(.+)"
    ]

    for line in lines:

        for pattern in location_patterns:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE
            )

            if not match:
                continue

            location = match.group(1).strip()

            # Remove leading symbols / bullets
            location = re.sub(
                r"^[^\w]+",
                "",
                location
            ).strip()

            placeholder_words = [
                "complete street address",
                "street address, city",
                "city, state zip",
                "city, state zip code",
                "complete address",
                "your address"
            ]

            if any(
                word in location.lower()
                for word in placeholder_words
            ):
                continue

            if location:

                personal_details["location"] = location

                break

        if personal_details["location"]:
            break

    # --------------------------------------------------------
    # Common location format
    #
    # Example:
    # Indore, Madhya Pradesh, India
    # San Jose, CA 95101
    # --------------------------------------------------------

    if personal_details["location"] is None:

        for line in lines[:20]:

            lower_line = line.lower()

            # Ignore email
            if "@" in line:
                continue

            # Ignore phone
            if personal_details["phone"]:

                if personal_details["phone"] in line:
                    continue

            # Ignore URLs
            if (
                "github" in lower_line
                or "linkedin" in lower_line
                or "http://" in lower_line
                or "https://" in lower_line
            ):
                continue

            # Ignore education/company-related lines
            excluded = [
                "university",
                "college",
                "school",
                "institute",
                "education",
                "google",
                "linkedin",
                "github"
            ]

            if any(
                word in lower_line
                for word in excluded
            ):
                continue

            # Ignore placeholders
            if (
                "complete street address" in lower_line
                or "city, state zip code" in lower_line
            ):
                continue

            # ------------------------------------------------
            # Strong location indicators
            # ------------------------------------------------

            location_indicators = [
                "street",
                "st.",
                "road",
                "rd.",
                "avenue",
                "ave.",
                "boulevard",
                "blvd.",
                "lane",
                "ln.",
                "drive",
                "dr.",
                "california",
                "texas",
                "florida",
                "madhya pradesh",
                "uttar pradesh",
                "maharashtra",
                "karnataka",
                "tamil nadu",
                "india",
                "usa"
            ]

            if any(
                indicator in lower_line
                for indicator in location_indicators
            ):

                if len(line) <= 100:

                    personal_details["location"] = line

                    break

            # ------------------------------------------------
            # City + State + ZIP pattern
            #
            # Example:
            # San Jose, CA 95101
            # ------------------------------------------------

            city_state_zip = re.match(
                r"^[A-Za-z .'-]+,\s*"
                r"[A-Za-z .'-]{2,25}"
                r"(?:\s+\d{5}(?:-\d{4})?)?$",
                line
            )

            if city_state_zip:

                personal_details["location"] = line

                break

            # ------------------------------------------------
            # Indian style
            #
            # Example:
            # Indore, Madhya Pradesh, India
            # ------------------------------------------------

            indian_location = re.match(
                r"^[A-Za-z .'-]+,\s*"
                r"[A-Za-z .'-]+,\s*"
                r"(?:India|USA|UK)$",
                line,
                re.IGNORECASE
            )

            if indian_location:

                personal_details["location"] = line

                break

    return personal_details