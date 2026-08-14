from ats_engine.ats_scorer import calculate_ats_score


def test_calculate_ats_score():
    candidate_skills = [
        "Python",
        "SQL",
        "Power BI"
    ]

    required_skills = [
        "Python",
        "SQL",
        "Excel",
        "Power BI"
    ]

    score = calculate_ats_score(
        candidate_skills,
        required_skills
    )

    assert score == 75.0