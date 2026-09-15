import json
from pathlib import Path

from answer_understanding_engine import AnswerUnderstandingEngine


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "sample_answers.json"
OUTPUT_FILE = BASE_DIR / "output" / "structured_answers.json"


def main():

    print("Starting Day 25 Answer Understanding Engine...")
    print()

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        answers = json.load(file)

    engine = AnswerUnderstandingEngine()

    structured_answers = []

    for item in answers:

        answer_id = item["answer_id"]
        question_id = item["question_id"]
        question = item["question"]
        answer = item["answer"]

        expected_intent = item.get("question_intent")

        result = engine.understand(
            answer,
            expected_intent=expected_intent
        )

        print(f"Answer ID: {answer_id}")
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['intent_confidence']}")
        print(f"Status: {result['answer_status']}")
        print(f"Validation: {result['validation']}")
        print(f"Extracted: {result['extracted_information']}")
        print()

        structured_answers.append(
            {
                "answer_id": answer_id,
                "question_id": question_id,
                "question": question,
                "raw_answer": answer,
                "understanding": result
            }
        )

    output = {
        "total_answers": len(structured_answers),
        "structured_answers": structured_answers
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
            indent=4,
            ensure_ascii=False
        )

    print("Answer understanding completed.")
    print(f"Total answers processed: {len(structured_answers)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()