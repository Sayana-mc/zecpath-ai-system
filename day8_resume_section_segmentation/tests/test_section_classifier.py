from src.section_classifier import (
    classify_heading,
    detect_section_heading,
    normalize_heading,
)

from src.segmentation_engine import (
    segment_resume,
)


def test_heading_normalization():

    result = normalize_heading(
        "Technical Skills:"
    )

    assert result == "technical skills"


def test_skill_heading():

    result = classify_heading(
        "Technical Skills"
    )

    assert result == "SKILLS"


def test_experience_heading():

    result = classify_heading(
        "Professional Experience"
    )

    assert result == "WORK EXPERIENCE"


def test_education_heading():

    result = classify_heading(
        "Education"
    )

    assert result == "EDUCATION"


def test_certification_heading():

    result = classify_heading(
        "Certifications"
    )

    assert result == "CERTIFICATIONS"


def test_project_heading():

    result = classify_heading(
        "Academic Projects"
    )

    assert result == "PROJECTS"


def test_section_segmentation():

    text = """
    John Mathew

    EDUCATION
    M.Sc Data Science
    B.Sc Mathematics

    SKILLS
    Python
    SQL
    Power BI

    PROJECTS
    Resume Screening System
    """

    result = segment_resume(text)

    assert (
        "M.Sc Data Science"
        in result["sections"]["EDUCATION"]
    )

    assert (
        "Python"
        in result["sections"]["SKILLS"]
    )

    assert (
        "Resume Screening System"
        in result["sections"]["PROJECTS"]
    )