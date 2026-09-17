import json
from pathlib import Path

from confidence_analyzer import ConfidenceAnalyzer
from sentiment_analyzer import SentimentAnalyzer
from behavioral_analyzer import BehavioralAnalyzer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_FILE = (
    PROJECT_ROOT
    / "day27_confidence_sentiment_analysis"
    / "config"
    / "analysis_config.json"
)

DATA_FILE = (
    PROJECT_ROOT
    / "day27_confidence_sentiment_analysis"
    / "data"
    / "sample_transcripts.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "day27_confidence_sentiment_analysis"
    / "output"
    / "behavioral_indicators_report.json"
)


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def main():

    print(
        "Starting Day 27 Confidence & Sentiment Analysis..."
    )

    config = load_json(CONFIG_FILE)

    transcripts = load_json(DATA_FILE)

    confidence_analyzer = ConfidenceAnalyzer(
        config
    )

    sentiment_analyzer = SentimentAnalyzer(
        config
    )

    behavioral_analyzer = BehavioralAnalyzer(
        confidence_analyzer,
        sentiment_analyzer
    )

    results = []

    for transcript in transcripts:

        result = behavioral_analyzer.analyze(
            transcript
        )

        results.append(result)

        confidence_score = result[
            "confidence_analysis"
        ]["confidence_score"]

        sentiment = result[
            "sentiment_analysis"
        ]["sentiment"]

        strength = result[
            "communication_strength"
        ]

        print()
        print(
            f"Answer ID: {result['answer_id']}"
        )
        print(
            f"Confidence Signal Score: {confidence_score}"
        )
        print(
            f"Sentiment: {sentiment}"
        )
        print(
            f"Communication Indicator: {strength}"
        )

    output = {
        "total_answers": len(results),
        "behavioral_indicators": results
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4
        )

    print()
    print(
        "Day 27 analysis completed."
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()