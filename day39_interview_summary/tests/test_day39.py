import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT /
    "day39_interview_summary_generator" /
    "src"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)


from interview_report_generator import (
    InterviewReportGenerator
)


def sample_responses():

    return {
        "communication_score": 85,
        "confidence_score": 80,
        "relevance_score": 90,
        "consistency_score": 88,
        "teamwork": "I enjoy working with a team.",
        "adaptability": "I am flexible and willing to learn.",
        "answers": [
            "I have experience with Python and SQL.",
            "I worked on data analysis projects."
        ]
    }


def test_strength_detection():

    generator = InterviewReportGenerator()

    result = generator.identify_strengths(
        sample_responses()
    )

    assert len(result) > 0


def test_weakness_detection():

    generator = InterviewReportGenerator()

    data = sample_responses()

    data["communication_score"] = 40

    result = generator.identify_weaknesses(data)

    assert "Communication needs improvement" in result


def test_cultural_fit():

    generator = InterviewReportGenerator()

    result = generator.identify_cultural_fit(
        sample_responses()
    )

    assert len(result) > 0


def test_risk_detection():

    generator = InterviewReportGenerator()

    data = sample_responses()

    data["answers"].append(
        "I am not sure about that."
    )

    result = generator.identify_risks(data)

    assert len(result) > 0


def test_overall_score():

    generator = InterviewReportGenerator()

    result = generator.calculate_overall_score(
        sample_responses()
    )

    assert result == 85.75


def test_report_generation():

    generator = InterviewReportGenerator()

    result = generator.generate_report(
        "C001",
        sample_responses()
    )

    assert result["candidate_id"] == "C001"
    assert "strengths" in result
    assert "weaknesses" in result
    assert "risk_flags" in result
    assert "summary" in result