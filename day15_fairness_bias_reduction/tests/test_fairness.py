import pytest

from src.normalization import (
    normalize_text,
    normalize_score,
    normalize_candidate,
)

from src.bias_reduction import (
    mask_personal_attributes,
    calculate_keyword_dependence,
    reduce_keyword_dependence,
)

from src.fairness_engine import (
    normalize_score_range,
    calculate_bias_indicators,
    process_candidates,
)


# ============================================================
# TEST 1 - SCORE NORMALIZATION
# ============================================================

def test_normalize_score():
    assert normalize_score(50) == 50.0
    assert normalize_score(150) == 100.0
    assert normalize_score(-20) == 0.0
    assert normalize_score("75") == 75.0
    assert normalize_score("invalid") == 0.0


# ============================================================
# TEST 2 - TEXT NORMALIZATION
# ============================================================

def test_normalize_text():

    text = "  Python   Developer\r\n\r\n\r\nSQL  "

    result = normalize_text(text)

    assert result == "Python Developer\n\nSQL"


# ============================================================
# TEST 3 - CANDIDATE NORMALIZATION
# ============================================================

def test_candidate_normalization():

    candidate = {
        "candidate_name": "  John   Doe  ",
        "job_id": " JOB001 ",
        "job_title": " Data Analyst ",
        "final_ats_score": "85",
    }

    result = normalize_candidate(candidate)

    assert result["candidate_name"] == "John Doe"
    assert result["job_id"] == "JOB001"
    assert result["job_title"] == "Data Analyst"
    assert result["final_ats_score"] == 85.0


# ============================================================
# TEST 4 - PERSONAL ATTRIBUTE MASKING
# ============================================================

def test_personal_attribute_masking():

    candidate = {
        "candidate_name": "John Doe",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "9876543210",
        "gender": "Male",
        "age": 25,
        "nationality": "Indian",
        "skills": ["Python", "SQL"],
        "fairness_score": 80.0,
    }

    result = mask_personal_attributes(candidate)

    assert result["candidate_name"] == "[MASKED]"
    assert result["name"] == "[MASKED]"
    assert result["email"] == "[MASKED]"
    assert result["phone"] == "[MASKED]"
    assert result["gender"] == "[MASKED]"
    assert result["age"] == "[MASKED]"
    assert result["nationality"] == "[MASKED]"

    # Job-relevant information must remain available.
    assert result["skills"] == ["Python", "SQL"]
    assert result["fairness_score"] == 80.0


# ============================================================
# TEST 5 - SCORE RANGE NORMALIZATION
# ============================================================

def test_score_normalization():

    scores = [10, 20, 30, 40, 50]

    result = normalize_score_range(
        scores,
        minimum=0,
        maximum=100,
    )

    assert result == [
        0.0,
        25.0,
        50.0,
        75.0,
        100.0,
    ]

    assert min(result) >= 0
    assert max(result) <= 100


# ============================================================
# TEST 6 - IDENTICAL SCORE NORMALIZATION
# ============================================================

def test_identical_score_normalization():

    scores = [50, 50, 50]

    result = normalize_score_range(
        scores,
        minimum=0,
        maximum=100,
    )

    assert result == [
        50.0,
        50.0,
        50.0,
    ]


# ============================================================
# TEST 7 - KEYWORD DEPENDENCE
# ============================================================

def test_keyword_dependence():

    breakdown = {
        "skill_match": 80,
        "experience_relevance": 70,
        "education_alignment": 60,
        "semantic_similarity": 90,
    }

    result = calculate_keyword_dependence(
        breakdown
    )

    assert result == 0.8


# ============================================================
# TEST 8 - KEYWORD DEPENDENCE REDUCTION
# ============================================================

def test_keyword_dependence_reduction():

    candidate = {
        "final_ats_score": 80.0,
        "breakdown": {
            "skill_match": 80.0,
            "experience_relevance": 70.0,
            "education_alignment": 60.0,
            "semantic_similarity": 90.0,
        },
    }

    result = reduce_keyword_dependence(
        candidate,
        keyword_limit=0.35,
    )

    assert result["keyword_dependence"] == 0.8

    # 80 * 0.95 = 76
    assert result["fairness_pre_adjusted_score"] == 76.0


# ============================================================
# TEST 9 - NO KEYWORD REDUCTION WHEN BELOW LIMIT
# ============================================================

def test_keyword_dependence_below_limit():

    candidate = {
        "final_ats_score": 80.0,
        "breakdown": {
            "skill_match": 20.0,
            "experience_relevance": 70.0,
        },
    }

    result = reduce_keyword_dependence(
        candidate,
        keyword_limit=0.35,
    )

    assert result["keyword_dependence"] == 0.2
    assert result["fairness_pre_adjusted_score"] == 80.0


# ============================================================
# TEST 10 - BIAS INDICATORS
# ============================================================

def test_bias_indicators():

    candidates = [
        {"fairness_score": 90},
        {"fairness_score": 70},
        {"fairness_score": 50},
    ]

    result = calculate_bias_indicators(
        candidates,
        warning_threshold=0.20,
    )

    assert result["candidate_count"] == 3
    assert result["minimum_score"] == 50.0
    assert result["maximum_score"] == 90.0
    assert result["average_score"] == 70.0
    assert result["score_gap"] == 0.4
    assert result["bias_warning"] is True


# ============================================================
# TEST 11 - NO BIAS WARNING FOR SMALL GAP
# ============================================================

def test_no_bias_warning_for_small_gap():

    candidates = [
        {"fairness_score": 80},
        {"fairness_score": 75},
        {"fairness_score": 70},
    ]

    result = calculate_bias_indicators(
        candidates,
        warning_threshold=0.20,
    )

    assert result["score_gap"] == 0.1
    assert result["bias_warning"] is False


# ============================================================
# TEST 12 - COMPLETE FAIRNESS PIPELINE
# ============================================================

def test_complete_fairness_pipeline():

    candidates = [
        {
            "candidate_name": "John Doe",
            "email": "john@example.com",
            "gender": "Male",
            "job_id": "JOB001",
            "job_title": "Data Analyst",
            "final_ats_score": 80,
            "breakdown": {
                "skill_match": 80,
                "experience_relevance": 70,
                "education_alignment": 60,
                "semantic_similarity": 90,
            },
        },
        {
            "candidate_name": "Jane Doe",
            "email": "jane@example.com",
            "gender": "Female",
            "job_id": "JOB001",
            "job_title": "Data Analyst",
            "final_ats_score": 40,
            "breakdown": {
                "skill_match": 20,
                "experience_relevance": 60,
                "education_alignment": 70,
                "semantic_similarity": 80,
            },
        },
    ]

    config = {
        "score_min": 0,
        "score_max": 100,
        "keyword_weight_limit": 0.35,
        "semantic_weight": 0.65,
        "bias_gap_warning": 0.20,
        "mask_personal_attributes": True,
        "personal_attributes": [
            "candidate_name",
            "email",
            "gender",
        ],
    }

    result = process_candidates(
        candidates,
        config,
    )

    assert len(result) == 2

    # Scores must be normalized.
    scores = [
        candidate["fairness_score"]
        for candidate in result
    ]

    assert min(scores) >= 0
    assert max(scores) <= 100

    # Personal attributes must be masked.
    assert result[0]["candidate_name"] == "[MASKED]"
    assert result[0]["email"] == "[MASKED]"
    assert result[0]["gender"] == "[MASKED]"

    assert result[1]["candidate_name"] == "[MASKED]"
    assert result[1]["email"] == "[MASKED]"
    assert result[1]["gender"] == "[MASKED]"

    # Fairness status must be assigned.
    assert result[0]["fairness_status"] == "FAIRNESS_CHECKED"
    assert result[1]["fairness_status"] == "FAIRNESS_CHECKED"

    # Keyword dependence should be calculated.
    assert "keyword_dependence" in result[0]
    assert "keyword_dependence" in result[1]