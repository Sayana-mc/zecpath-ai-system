import json
from pathlib import Path

from confidence_analyzer import ConfidenceAnalyzer
from sentiment_engine import SentimentEngine
from behavioral_signals import BehavioralSignalAnalyzer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def main():

    print("=" * 60)
    print("DAY 36 - CONFIDENCE & STRESS INDICATORS")
    print("=" * 60)

    responses = [
        {
            "answer_id": "ANS001",
            "question": "Tell me about your strengths.",
            "answer": (
                "I am confident in Python and SQL. "
                "I successfully completed several projects."
            ),
            "previous_information": {}
        },
        {
            "answer_id": "ANS002",
            "question": "Tell me about a difficult situation.",
            "answer": (
                "Um... I think maybe it was difficult "
                "and I was worried about the problem."
            ),
            "previous_information": {}
        },
        {
            "answer_id": "ANS003",
            "question": "Tell me about your experience.",
            "answer": (
                "I have 2 years of experience "
                "working in data analysis."
            ),
            "previous_information": {
                "experience_years": 1
            }
        }
    ]

    confidence_analyzer = ConfidenceAnalyzer()
    sentiment_engine = SentimentEngine()
    behavioral_analyzer = BehavioralSignalAnalyzer()

    results = []

    for item in responses:

        answer = item["answer"]

        confidence_result = confidence_analyzer.analyze(
            answer
        )

        sentiment_result = sentiment_engine.analyze(
            answer
        )

        behavioral_result = behavioral_analyzer.analyze(
            answer,
            confidence_result["hesitation"],
            confidence_result["uncertainty"],
            confidence_result["repeated_words"],
            sentiment_result,
            item["previous_information"]
        )

        result = {
            "answer_id": item["answer_id"],
            "question": item["question"],
            "answer": answer,
            "confidence_analysis": confidence_result,
            "sentiment_analysis": sentiment_result,
            "behavioral_signals": behavioral_result
        }

        results.append(result)

        print()
        print("Answer ID:", item["answer_id"])
        print(
            "Confidence Score:",
            confidence_result["confidence_score"]
        )
        print(
            "Sentiment:",
            sentiment_result["sentiment"]
        )
        print(
            "Sentiment Score:",
            sentiment_result["score"]
        )
        print(
            "Stress Score:",
            behavioral_result["stress_score"]
        )
        print(
            "Contradiction:",
            behavioral_result["contradiction"]["contradiction"]
        )

    output = {
        "total_answers": len(results),
        "results": results
    }

    output_file = (
        OUTPUT_DIR /
        "behavioral_signal_report.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=4
        )

    print()
    print("=" * 60)
    print("BEHAVIORAL SIGNAL ANALYSIS COMPLETED")
    print("Total answers:", len(results))
    print("Output:", output_file)
    print("=" * 60)


if __name__ == "__main__":
    main()