import json

from src.eligibility_engine import EligibilityDecisionEngine


def load_rules():

    with open(
        "config/eligibility_rules.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def test_eligible_candidate():

    engine = EligibilityDecisionEngine(load_rules())

    candidate = {
        "ats_score": 80,
        "skills": [
            "Python",
            "SQL"
        ],
        "experience_years": 2,
        "location": "Bengaluru"
    }

    result = engine.evaluate_candidate(
        candidate,
        "Data Analyst"
    )

    assert result["status"] == "ELIGIBLE"


def test_low_ats_score():

    engine = EligibilityDecisionEngine(load_rules())

    candidate = {
        "ats_score": 50,
        "skills": [
            "Python",
            "SQL"
        ],
        "experience_years": 2,
        "location": "Bengaluru"
    }

    result = engine.evaluate_candidate(
        candidate,
        "Data Analyst"
    )

    assert result["status"] == "REJECTED"


def test_missing_mandatory_skill():

    engine = EligibilityDecisionEngine(load_rules())

    candidate = {
        "ats_score": 80,
        "skills": [
            "Python"
        ],
        "experience_years": 2,
        "location": "Bengaluru"
    }

    result = engine.evaluate_candidate(
        candidate,
        "Data Analyst"
    )

    assert result["status"] == "REVIEW"


def test_location_mismatch():

    engine = EligibilityDecisionEngine(load_rules())

    candidate = {
        "ats_score": 80,
        "skills": [
            "Python",
            "SQL"
        ],
        "experience_years": 2,
        "location": "Kochi"
    }

    result = engine.evaluate_candidate(
        candidate,
        "Data Analyst"
    )

    assert result["status"] == "REVIEW"