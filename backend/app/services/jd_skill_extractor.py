# app/services/jd_skill_extractor.py


def extract_required_skills(text):
    skills_dictionary = [
        "Python",
        "Java",
        "C",
        "C++",
        "JavaScript",
        "HTML",
        "HTML5",
        "CSS",
        "CSS3",
        "React",
        "React.js",
        "Node.js",
        "PHP",
        "Django",
        "Spring",
        "Spring Boot",
        "SQL",
        "MySQL",
        "MongoDB",
        "DBMS",
        "Git",
        "GitHub",
        "Docker",
        "AWS",
        "Machine Learning",
        "Artificial Intelligence",
        "Natural Language Processing",
        "Computer Networks",
        "Data Structures",
        "Algorithms"
    ]

    text_lower = text.lower()

    required_skills = []

    for skill in skills_dictionary:
        if skill.lower() in text_lower:
            required_skills.append(skill)

    return required_skills