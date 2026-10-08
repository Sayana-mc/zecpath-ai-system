from day46_technical_interview_system_design.src.interview_blueprint import (
    determine_experience_level,
    get_role_skills,
    build_interview_blueprint
)


def test_basic_experience_level():
    assert determine_experience_level(1) == "0-2"


def test_intermediate_experience_level():
    assert determine_experience_level(4) == "3-5"


def test_advanced_experience_level():
    assert determine_experience_level(7) == "5+"


def test_role_skill_mapping():
    skills = get_role_skills("MERN Developer")

    assert "React" in skills
    assert "Node.js" in skills
    assert "MongoDB" in skills


def test_ai_ml_role_mapping():
    skills = get_role_skills("AI/ML Engineer")

    assert "Python" in skills
    assert "Machine Learning" in skills


def test_blueprint_generation():
    candidate = {
        "candidate_id": "TEST001",
        "role": "Data Analyst",
        "experience_years": 2,
        "skills": [
            "Python",
            "SQL"
        ]
    }

    blueprint = build_interview_blueprint(candidate)

    assert blueprint["experience_level"] == "0-2"
    assert blueprint["difficulty"] == "basic"
    assert "SQL" in blueprint["skill_domains"]
    assert "introduction" in blueprint["question_types"]