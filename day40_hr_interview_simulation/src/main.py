import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day40_hr_interview_simulation"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))

from simulation_engine import HRInterviewSimulator
from evaluator import HREvaluator


OUTPUT_DIR = (
    PROJECT_ROOT
    / "day40_hr_interview_simulation"
    / "output"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def manual_scores(candidate_type):
    """
    Reference scores representing manual evaluation.
    These are used only for comparison with AI scores.
    """

    return {
        "confident": 92,
        "hesitant": 68,
        "inexperienced": 62,
        "overqualified": 88
    }.get(candidate_type, 0)


def main():

    print("=" * 60)
    print("DAY 40 - HR INTERVIEW SIMULATION")
    print("=" * 60)

    simulator = HRInterviewSimulator()
    evaluator = HREvaluator()

    sessions = simulator.simulate_all()

    report = []

    for candidate_type, session in sessions.items():

        evaluation = evaluator.evaluate_session(
            session
        )

        ai_score = evaluation["overall_ai_score"]
        manual_score = manual_scores(
            candidate_type
        )

        difference = round(
            abs(ai_score - manual_score),
            2
        )

        evaluation["manual_score"] = manual_score
        evaluation["score_difference"] = difference

        report.append(evaluation)

        print()
        print(
            f"Candidate Type: {candidate_type}"
        )
        print(
            f"Candidate ID: {session['candidate_id']}"
        )
        print(
            f"AI Score: {ai_score}"
        )
        print(
            f"Manual Score: {manual_score}"
        )
        print(
            f"Difference: {difference}"
        )

    overall_accuracy = round(
        sum(
            100 - item["score_difference"]
            for item in report
        ) / len(report),
        2
    )

    final_report = {
        "day": 40,
        "title": "HR Interview Simulation",
        "total_sessions": len(report),
        "candidate_types_tested": [
            "confident",
            "hesitant",
            "inexperienced",
            "overqualified"
        ],
        "sessions": report,
        "average_ai_manual_accuracy": overall_accuracy
    }

    output_file = (
        OUTPUT_DIR
        / "hr_interview_test_report.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            final_report,
            file,
            indent=4
        )

    accuracy_file = (
        OUTPUT_DIR
        / "accuracy_evaluation.json"
    )

    accuracy_data = {
        "metric": "AI vs Manual Evaluation",
        "accuracy": overall_accuracy,
        "interpretation": (
            "Higher value indicates closer agreement "
            "between AI and manual scores."
        )
    }

    with open(
        accuracy_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            accuracy_data,
            file,
            indent=4
        )

    print()
    print("=" * 60)
    print("HR INTERVIEW SIMULATION COMPLETED")
    print("=" * 60)
    print(
        f"Average AI/Manual accuracy: "
        f"{overall_accuracy}"
    )
    print(
        f"Test Report: {output_file}"
    )
    print(
        f"Accuracy Report: {accuracy_file}"
    )


if __name__ == "__main__":
    main()