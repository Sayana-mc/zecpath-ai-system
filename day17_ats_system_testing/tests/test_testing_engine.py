from pathlib import Path

from src.testing_engine import (
    calculate_metrics,
    find_mismatches,
    merge_ai_and_manual_results,
)


def test_metrics_perfect_match():

    records = [
        {
            "ai_decision": "SHORTLISTED",
            "manual_decision": "SHORTLISTED",
        },
        {
            "ai_decision": "REJECTED",
            "manual_decision": "REJECTED",
        },
    ]

    result = calculate_metrics(records)

    assert result["accuracy"] == 1.0
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0


def test_false_positive():

    records = [
        {
            "ai_decision": "SHORTLISTED",
            "manual_decision": "REJECTED",
        }
    ]

    result = calculate_metrics(records)

    assert result["false_positive"] == 1


def test_false_negative():

    records = [
        {
            "ai_decision": "REJECTED",
            "manual_decision": "SHORTLISTED",
        }
    ]

    result = calculate_metrics(records)

    assert result["false_negative"] == 1


def test_mismatch_detection():

    records = [
        {
            "job_id": "JOB001",
            "job_title": "Data Analyst",
            "candidate_name": "Candidate A",
            "ai_score": 75,
            "ai_decision": "SHORTLISTED",
            "manual_decision": "REJECTED",
            "profile_category": "tech",
            "review_notes": "Skill mismatch",
        }
    ]

    mismatches = find_mismatches(records)

    assert len(mismatches) == 1
    assert (
        mismatches[0]["candidate_name"]
        == "Candidate A"
    )


def test_matching_decisions_have_no_mismatch():

    records = [
        {
            "job_id": "JOB001",
            "job_title": "Data Analyst",
            "candidate_name": "Candidate A",
            "ai_score": 75,
            "ai_decision": "SHORTLISTED",
            "manual_decision": "SHORTLISTED",
            "profile_category": "tech",
            "review_notes": "",
        }
    ]

    mismatches = find_mismatches(records)

    assert mismatches == []