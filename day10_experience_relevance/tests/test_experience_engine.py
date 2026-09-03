from datetime import date

from src.experience_parser import (
    parse_month_year,
    calculate_months,
    calculate_total_experience,
    detect_gaps,
    detect_overlaps,
)

from src.relevance_scorer import (
    calculate_role_similarity,
    calculate_relevance_score,
)


def test_month_year_parsing():

    result = parse_month_year(
        "January 2023"
    )

    assert result == date(
        2023,
        1,
        1,
    )


def test_month_calculation():

    start = date(
        2023,
        1,
        1,
    )

    end = date(
        2023,
        12,
        1,
    )

    assert calculate_months(
        start,
        end,
    ) == 12


def test_total_experience():

    experiences = [
        {
            "duration_months": 12
        },
        {
            "duration_months": 24
        },
    ]

    assert calculate_total_experience(
        experiences
    ) == 3.0


def test_gap_detection():

    experiences = [
        {
            "job_title": "Developer",
            "start_date": "2020-01-01",
            "end_date": "2020-12-01",
        },
        {
            "job_title": "Analyst",
            "start_date": "2022-01-01",
            "end_date": "2022-12-01",
        },
    ]

    gaps = detect_gaps(
        experiences
    )

    assert len(gaps) == 1


def test_overlap_detection():

    experiences = [
        {
            "job_title": "Developer",
            "start_date": "2020-01-01",
            "end_date": "2021-06-01",
        },
        {
            "job_title": "Consultant",
            "start_date": "2021-01-01",
            "end_date": "2021-12-01",
        },
    ]

    overlaps = detect_overlaps(
        experiences
    )

    assert len(overlaps) == 1


def test_role_similarity():

    score = calculate_role_similarity(
        "Data Analyst",
        "Data Analyst",
    )

    assert score > 0


def test_relevance_score():

    experiences = [
        {
            "job_title": "Data Analyst",
            "company": "ABC Company",
            "duration_months": 24,
        }
    ]

    result = calculate_relevance_score(
        experiences,
        "Data Analyst",
    )

    assert result[
        "relevance_score"
    ] > 0