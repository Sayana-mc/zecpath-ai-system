from src.noisy_resume_handler import (
    normalize_noisy_text,
    normalize_skill_text,
)

from src.entity_optimizer import (
    detect_skills,
    detect_years_of_experience,
)


def test_empty_resume():

    result = normalize_noisy_text("")

    assert result == ""


def test_noisy_text():

    text = "Pyth0n!!!     SQL!!!"

    result = normalize_skill_text(text)

    assert "Python" in result
    assert "SQL" in result


def test_skill_detection():

    text = "Python SQL Power BI"

    skills = detect_skills(text)

    assert "python" in skills
    assert "sql" in skills
    assert "power bi" in skills


def test_experience_detection():

    text = "Data Analyst with 3 years of experience."

    years = detect_years_of_experience(text)

    assert years == 3


def test_missing_experience():

    text = "Fresh graduate with Python skills."

    years = detect_years_of_experience(text)

    assert years == 0