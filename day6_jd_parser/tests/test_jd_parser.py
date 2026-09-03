import sys
from pathlib import Path

import pytest


SRC_DIR = Path(__file__).resolve().parents[1] / "src"

sys.path.insert(
    0,
    str(SRC_DIR)
)

from jd_cleaner import (
    clean_jd_text,
    normalize_experience
)

from skill_normalizer import (
    normalize_skill,
    normalize_skills,
    normalize_role
)

from jd_parser import create_ai_jd_profile


def test_text_cleaning():

    text = "Python   Developer\n\nKochi"

    result = clean_jd_text(text)

    assert result == "Python Developer\nKochi"


def test_skill_normalization():

    assert normalize_skill("powerbi") == "Power BI"

    assert normalize_skill(
        "structured query language"
    ) == "SQL"

    assert normalize_skill(
        "fast api"
    ) == "FastAPI"


def test_skill_list_normalization():

    skills = [
        "Python",
        "python programming",
        "SQL",
        "powerbi"
    ]

    result = normalize_skills(skills)

    assert "Python" in result
    assert "SQL" in result
    assert "Power BI" in result

    assert result.count("Python") == 1


def test_role_normalization():

    assert normalize_role(
        "machine learning engineer"
    ) == "AI/ML Engineer"

    assert normalize_role(
        "math teacher"
    ) == "Mathematics Teacher"


def test_experience_normalization():

    assert normalize_experience(
        "0-2 years"
    ) == "0-2"


def test_jd_profile_creation():

    jd = {

        "job_id": "TEST001",

        "job_title": "Python Developer",

        "department": "Engineering",

        "domain": "Software Development",

        "job_type": "Technical",

        "experience_required_years": "0-2",

        "location": "Kochi, Kerala",

        "employment_type": "Full-time",

        "education": [
            "B.Tech / B.E in Computer Science"
        ],

        "required_skills": [
            "Python",
            "SQL",
            "powerbi"
        ],

        "preferred_skills": [
            "Docker"
        ],

        "responsibilities": [
            "Develop applications"
        ],

        "soft_skills": [
            "Communication"
        ]
    }

    result = create_ai_jd_profile(jd)

    assert result["job_id"] == "TEST001"

    assert (
        result["role"]["title"]
        == "Python Developer"
    )

    assert "Python" in result["skills"]["required"]

    assert "SQL" in result["skills"]["required"]

    assert "Power BI" in result["skills"]["required"]

    assert (
        result["experience"]["required_years"]
        == "0-2"
    )