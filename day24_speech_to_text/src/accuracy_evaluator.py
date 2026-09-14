import json
import re
from pathlib import Path

from stt_processor import SpeechToTextProcessor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"


def normalize_for_comparison(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def word_accuracy(expected, actual):

    expected_words = normalize_for_comparison(
        expected
    ).split()

    actual_words = normalize_for_comparison(
        actual
    ).split()

    if not expected_words:
        return 0.0

    correct = 0

    for expected_word, actual_word in zip(
        expected_words,
        actual_words
    ):
        if expected_word == actual_word:
            correct += 1

    accuracy = (
        correct / len(expected_words)
    ) * 100

    return round(accuracy, 2)


def evaluate():

    test_file = DATA_DIR / "stt_test_cases.json"

    with open(
        test_file,
        "r",
        encoding="utf-8"
    ) as f:
        test_cases = json.load(f)

    processor = SpeechToTextProcessor()

    results = []

    for test_case in test_cases:

        audio_path = (
            DATA_DIR
            / "audio"
            / "clean"
            / test_case["audio_file"]
        )

        if test_case["condition"] == "background_noise":
            audio_path = (
                DATA_DIR
                / "audio"
                / "noise"
                / test_case["audio_file"]
            )

        elif test_case["condition"].startswith(
            "accent_"
        ):
            audio_path = (
                DATA_DIR
                / "audio"
                / "accents"
                / test_case["audio_file"]
            )

        stt_result = processor.transcribe(
            audio_path
        )

        accuracy = word_accuracy(
            test_case["expected_text"],
            stt_result["text"]
        )

        results.append({
            "test_id": test_case["test_id"],
            "audio_file": test_case["audio_file"],
            "condition": test_case["condition"],
            "expected_text":
                test_case["expected_text"],
            "recognized_text":
                stt_result["text"],
            "accuracy_percent": accuracy
        })

    average_accuracy = 0.0

    if results:
        average_accuracy = round(
            sum(
                item["accuracy_percent"]
                for item in results
            ) / len(results),
            2
        )

    report = {
        "total_tests": len(results),
        "average_word_accuracy_percent":
            average_accuracy,
        "tests": results
    }

    OUTPUT_DIR.mkdir(exist_ok=True)

    output_file = (
        OUTPUT_DIR / "stt_accuracy_report.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            report,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("\nSTT Accuracy Test Completed")
    print(
        f"Total tests: {len(results)}"
    )
    print(
        f"Average accuracy: {average_accuracy}%"
    )
    print(
        f"Report: {output_file}"
    )


if __name__ == "__main__":
    evaluate()