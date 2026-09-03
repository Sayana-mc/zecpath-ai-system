"""
Skill and role normalization utilities.

This module maps common aliases and variations
to canonical AI-readable terms.
"""


SKILL_SYNONYMS = {

    "python programming": "Python",
    "python development": "Python",

    "structured query language": "SQL",
    "sql queries": "SQL",

    "powerbi": "Power BI",
    "power-bi": "Power BI",

    "ms excel": "Excel",
    "microsoft excel": "Excel",
    "advanced excel": "Advanced Excel",

    "machine learning": "Machine Learning",
    "ml": "Machine Learning",

    "deep learning": "Deep Learning",
    "dl": "Deep Learning",

    "scikit learn": "Scikit-learn",
    "scikit learn library": "Scikit-learn",

    "tensorflow framework": "TensorFlow",

    "pytorch framework": "PyTorch",

    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",

    "version control": "Git",
    "git version control": "Git",

    "amazon web services": "AWS",

    "postgres": "PostgreSQL",

    "mongo": "MongoDB",

    "natural language processing": "NLP",
    "large language models": "LLMs",

    "generative ai": "Generative AI",
    "gen ai": "Generative AI",

    "fast api": "FastAPI",

    "human resources": "HR",
    "human resource": "HR",

    "customer service": "Customer Support",

    "customer support": "Customer Support",

    "relationship management": "CRM",

    "adobe photoshop": "Adobe Photoshop",

    "adobe illustrator": "Adobe Illustrator",

    "computer aided design": "AutoCAD",
}


ROLE_SYNONYMS = {

    "python developer": "Python Developer",
    "python programmer": "Python Developer",

    "software developer": "Software Developer",
    "software engineer": "Software Engineer",

    "data analyst": "Data Analyst",
    "data analytics": "Data Analyst",

    "ai/ml engineer": "AI/ML Engineer",
    "ai ml engineer": "AI/ML Engineer",
    "machine learning engineer": "AI/ML Engineer",

    "financial analyst": "Financial Analyst",

    "hr executive": "HR Executive",
    "human resources executive": "HR Executive",

    "graphic designer": "Graphic Designer",

    "mechanical engineer": "Mechanical Engineer",

    "customer support executive": "Customer Support Executive",
    "customer service executive": "Customer Support Executive",

    "mathematics teacher": "Mathematics Teacher",
    "math teacher": "Mathematics Teacher",

    "sales manager": "Sales Manager",
}


def normalize_skill(skill):
    """
    Convert a skill to its canonical representation.
    """

    if not skill:
        return ""

    original = str(skill).strip()
    key = original.lower()

    return SKILL_SYNONYMS.get(key, original)


def normalize_skills(skills):
    """
    Normalize a list of skills and remove duplicates.
    """

    normalized = []

    for skill in skills or []:

        canonical = normalize_skill(skill)

        if canonical and canonical not in normalized:
            normalized.append(canonical)

    return normalized


def normalize_role(role):
    """
    Convert job title variations to canonical role names.
    """

    if not role:
        return ""

    original = str(role).strip()
    key = original.lower()

    return ROLE_SYNONYMS.get(key, original)