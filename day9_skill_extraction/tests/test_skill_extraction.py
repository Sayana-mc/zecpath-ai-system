from src.skill_normalizer import (
    normalize_skill_name,
    get_skill_category
)

from src.skill_extractor import (
    extract_skills_from_text,
    deduplicate_skills
)


def test_python_normalization():

    assert normalize_skill_name(
        "python3"
    ) == "Python"


def test_javascript_normalization():

    assert normalize_skill_name(
        "JS"
    ) == "JavaScript"


def test_sql_normalization():

    assert normalize_skill_name(
        "structured query language"
    ) == "SQL"


def test_skill_category():

    assert get_skill_category(
        "Python"
    ) == "technical"


def test_skill_extraction():

    text = """
    Python developer with SQL,
    Pandas and FastAPI experience.
    """

    skills = extract_skills_from_text(
        text,
        source="SKILLS"
    )

    names = [
        item["skill"]
        for item in skills
    ]

    assert "Python" in names
    assert "SQL" in names
    assert "Pandas" in names
    assert "FastAPI" in names


def test_skill_stack():

    text = """
    Full stack developer with MERN experience.
    """

    skills = extract_skills_from_text(
        text,
        source="SKILLS"
    )

    names = [
        item["skill"]
        for item in skills
    ]

    assert "MERN" in names
    assert "MongoDB" in names
    assert "React" in names
    assert "Node.js" in names


def test_deduplication():

    skills = [

        {
            "skill": "Python",
            "category": "technical",
            "source": "SKILLS",
            "match_type": "exact",
            "confidence": 0.90
        },

        {
            "skill": "Python",
            "category": "technical",
            "source": "PROJECTS",
            "match_type": "exact",
            "confidence": 0.75
        }
    ]

    result = deduplicate_skills(
        skills
    )

    assert len(result) == 1
    assert result[0]["confidence"] == 0.90


def test_confidence_score():

    text = "Python SQL"

    skills = extract_skills_from_text(
        text,
        source="SKILLS"
    )

    for skill in skills:

        assert 0.0 <= skill["confidence"] <= 1.0