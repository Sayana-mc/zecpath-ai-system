import json
import sys
from pathlib import Path

# Ensure local and root directories are available for import
_LOCAL_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _p in [str(_LOCAL_DIR), str(_PROJECT_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from .screening_pipeline import ScreeningPipeline
except (ImportError, ValueError):
    try:
        from day32_screening_system_finalization.src.screening_pipeline import (
            ScreeningPipeline,
        )
    except ImportError:
        from screening_pipeline import ScreeningPipeline


def main():
    print("=" * 70)
    print("DAY 32 - FINAL AI SCREENING SYSTEM: LIVE DEMONSTRATION")
    print("=" * 70)

    pipeline: ScreeningPipeline = ScreeningPipeline()

    # Demonstration input values matching Day 32 specification:
    # Candidate ID: C001
    # Technical Skills: Python, SQL, Excel, Power BI
    # Experience: 1 year
    # Availability: Immediate
    # Expected Salary: 4 LPA
    candidate_answers = {
        "Q001": "I have experience with Python, SQL, Excel and Power BI.",
        "Q002": "I have completed data analyst and data science internships with 1 year of experience.",
        "Q003": "I am available to join immediately.",
        "Q004": "My expected salary is around 4 LPA."
    }

    result = pipeline.process_candidate(
        candidate_id="C001",
        answers=candidate_answers
    )

    print()
    print("SCREENING SESSION OVERVIEW")
    print("-" * 70)
    print(f"Candidate ID       : {result['candidate_id']}")
    print(f"Screening ID       : {result['screening_id']}")
    print(f"Timestamp          : {result['timestamp']}")
    print(f"Session Status     : {result['status'].upper()}")
    print(f"Total Questions    : {result['total_questions']}")
    print(f"Aggregate Score    : {result['aggregate_score']} / 100")
    print(f"Dominant Sentiment : {result['behavioral_summary']['dominant_sentiment'].upper()}")
    print(f"Communication Eval : {result['behavioral_summary']['communication_rating']}")

    print()
    print("EVALUATED SCREENING RESPONSES")
    print("-" * 70)

    for answer in result["answers"]:
        qid = answer["question_id"]
        status = answer["status"]
        q_text = answer["question"]
        ans_text = answer["answer"]
        intent = answer.get("intent", "unknown")
        confidence = answer.get("intent_confidence", 1.0)
        extracted = answer.get("extracted_information", {})
        scoring = answer.get("scoring", {})
        norm_score = answer.get("score", 0.0)
        behavioral = answer.get("behavioral", {})

        print(f"[{qid}] Category: {answer.get('category', '').upper()} | Status: {status.upper()}")
        print(f"  Question   : {q_text}")
        print(f"  Answer     : {ans_text}")
        print(f"  Intent     : {intent} (Confidence: {confidence * 100:.1f}%)")
        print(f"  Extracted  : {json.dumps(extracted, ensure_ascii=False)}")
        print(f"  Score      : {norm_score} / 100")
        if scoring.get("parameter_scores"):
            p_scores = scoring["parameter_scores"]
            print(f"  Breakdown  : Clarity={p_scores.get('clarity')}/5, Relevance={p_scores.get('relevance')}/5, Completeness={p_scores.get('completeness')}/5, Consistency={p_scores.get('consistency')}/5")
        if behavioral:
            print(f"  Behavioral : Sentiment={behavioral.get('sentiment', 'N/A').upper()}, Confidence Score={behavioral.get('confidence_score', 'N/A')}")
        print()

    output_path = (
        Path(__file__).resolve().parents[1]
        / "output"
        / "final_screening_demo.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            result,
            file,
            indent=4
        )

    print("=" * 70)
    print("END-TO-END SCREENING DEMO COMPLETED SUCCESSFULLY")
    print(f"Saved Output: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
