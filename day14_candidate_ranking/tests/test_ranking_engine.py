from src.ranking_engine import (
    normalize_score,
    rank_candidates,
)
from src.shortlisting_engine import (
    get_decision,
)


def test_normalize_score():
    assert normalize_score(80) == 80.0
    assert normalize_score(150) == 100.0
    assert normalize_score(-10) == 0.0


def test_candidate_sorting():
    candidates = [
        {"candidate_name": "Candidate A", "final_ats_score": 40},
        {"candidate_name": "Candidate B", "final_ats_score": 80},
        {"candidate_name": "Candidate C", "final_ats_score": 60},
    ]

    ranked = rank_candidates(candidates)

    assert ranked[0]["candidate_name"] == "Candidate B"
    assert ranked[1]["candidate_name"] == "Candidate C"
    assert ranked[2]["candidate_name"] == "Candidate A"


def test_rank_numbers():
    candidates = [
        {"candidate_name": "Candidate A", "final_ats_score": 90},
        {"candidate_name": "Candidate B", "final_ats_score": 80},
    ]

    ranked = rank_candidates(candidates)

    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2


def test_shortlisted_threshold():
    assert get_decision(65, 65, 40) == "SHORTLISTED"
    assert get_decision(90, 65, 40) == "SHORTLISTED"


def test_review_threshold():
    assert get_decision(40, 65, 40) == "REVIEW"
    assert get_decision(50, 65, 40) == "REVIEW"


def test_rejected_threshold():
    assert get_decision(39.99, 65, 40) == "REJECTED"
    assert get_decision(10, 65, 40) == "REJECTED"