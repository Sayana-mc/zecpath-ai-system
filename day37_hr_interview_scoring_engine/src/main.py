import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = (
    PROJECT_ROOT
    / "day37_hr_interview_scoring_engine"
    / "config"
)

SRC_DIR = (
    PROJECT_ROOT
    / "day37_hr_interview_scoring_engine"
    / "src"
)

sys.path.insert(0, str(CONFIG_DIR))
sys.path.insert(0, str(SRC_DIR))


from scoring_config import load_config
from hr_scoring_engine import HRInterviewScoringEngine


def main():

    print("=" * 60)
    print("DAY 37 - HR INTERVIEW SCORING ENGINE")
    print("=" * 60)

    config = load_config()

    engine = HRInterviewScoringEngine(config)

    candidate_id = "C001"

    responses = [
        {
            "question_id": "HR001",
            "question": "Tell me about yourself.",
            "answer_relevance": 5,
            "communication": 5,
            "confidence": 4,
            "consistency": 5
        },
        {
            "question_id": "HR002",
            "question": "What are your strengths?",
            "answer_relevance": 5,
            "communication": 4,
            "confidence": 4,
            "consistency": 5
        },
        {
            "question_id": "HR003",
            "question": "Where do you see yourself in five years?",
            "answer_relevance": 4,
            "communication": 4,
            "confidence": 4,
            "consistency": 4
        },
        {
            "question_id": "HR004",
            "question": "Why should we hire you?",
            "answer_relevance": 5,
            "communication": 4,
            "confidence": 5,
            "consistency": 4
        }
    ]

    total_scores = {
        "answer_relevance": 0,
        "communication": 0,
        "confidence": 0,
        "consistency": 0
    }

    for response in responses:

        for parameter in total_scores:
            total_scores[parameter] += response[parameter]

    count = len(responses)

    average_scores = {
        parameter: round(
            total / count,
            2
        )
        for parameter, total
        in total_scores.items()
    }

    result = engine.calculate_candidate_score(
        responses=count,
        relevance=average_scores["answer_relevance"],
        communication=average_scores["communication"],
        confidence=average_scores["confidence"],
        consistency=average_scores["consistency"]
    )

    report = {
        "candidate_id": candidate_id,
        "interview_type": "HR Interview",
        "questions_evaluated": count,
        "average_parameter_scores": average_scores,
        "score": result
    }

    output_dir = (
        PROJECT_ROOT
        / "day37_hr_interview_scoring_engine"
        / "output"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir
        / "candidate_hr_score_report.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print()
    print("Candidate ID:", candidate_id)
    print("Questions evaluated:", count)

    print()
    print("Average Scores:")

    for parameter, score in average_scores.items():
        print(
            f"{parameter}: {score}/5"
        )

    print()
    print(
        "Weighted Score:",
        result["weighted_score"]
    )

    print(
        "Normalized HR Score:",
        result["normalized_score"]
    )

    print()
    print("Explainable Breakdown:")

    for parameter, details in result[
        "explainable_breakdown"
    ].items():

        print(
            parameter,
            "->",
            details
        )

    print()
    print("HR interview scoring completed.")
    print("Output:", output_file)
    print("=" * 60)


if __name__ == "__main__":
    main()