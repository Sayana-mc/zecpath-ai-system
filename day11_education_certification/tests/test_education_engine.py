from src.education_parser import (
    detect_degree_type,
    extract_year,
    normalize_field,
    parse_education_section,
)

from src.certification_parser import (
    normalize_certification_name,
    classify_certification,
    extract_certifications,
)

from src.education_relevance import (
    calculate_education_relevance,
)


def test_degree_detection():
    assert (
        detect_degree_type(
            "M.Sc Data Science"
        )
        == "MASTER"
    )


def test_bachelor_detection():
    assert (
        detect_degree_type(
            "B.Sc Mathematics"
        )
        == "BACHELOR"
    )


def test_year_extraction():
    assert (
        extract_year(
            "M.Sc Data Science 2024"
        )
        == 2024
    )


def test_field_normalization():
    assert (
        normalize_field(
            "data science and analytics"
        )
        == "Data Science"
    )


def test_education_parsing():
    result = parse_education_section(
        "M.Sc Data Science from Jain University 2024"
    )

    assert len(result) == 1
    assert result[0]["degree_type"] == "MASTER"
    assert result[0]["graduation_year"] == 2024


def test_certification_normalization():
    assert (
        normalize_certification_name(
            "aws certified"
        )
        == "AWS Certified"
    )


def test_certification_category():
    assert (
        classify_certification(
            "AWS Certified Solutions Architect"
        )
        == "TECHNICAL"
    )


def test_certification_extraction():
    result = extract_certifications(
        "AWS Certified Solutions Architect 2024"
    )

    assert len(result) == 1
    assert result[0]["category"] == "TECHNICAL"


def test_education_relevance():
    education = [
        {
            "degree_type": "MASTER",
            "degree_name": "M.Sc Data Science",
            "field_of_study": "Data Science",
            "institution": "Example University",
            "graduation_year": 2024,
        }
    ]

    result = calculate_education_relevance(
        education,
        "data analyst",
    )

    assert result["score"] == 1.0
    assert result["relevance"] == "HIGH"