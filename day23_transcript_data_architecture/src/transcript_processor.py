import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "sample_transcript.json"
NORMALIZED_OUTPUT = BASE_DIR / "output" / "normalized_transcript.json"
AI_OUTPUT = BASE_DIR / "output" / "ai_screening_data.json"


def load_transcript():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_text(text):
    if not isinstance(text, str):
        return ""

    # Normalize line breaks
    text = text.replace("\n", " ")

    # Normalize repeated whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def validate_confidence(confidence):
    return isinstance(confidence, (int, float)) and 0.0 <= confidence <= 1.0


def process_transcript(transcript):
    interactions = transcript.get("interactions", [])

    valid_interactions = []
    validation_errors = []

    for interaction in interactions:
        required_fields = [
            "interaction_id",
            "question_id",
            "speaker",
            "timestamp",
            "raw_text",
            "confidence_level"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in interaction
        ]

        if missing_fields:
            validation_errors.append({
                "interaction_id": interaction.get("interaction_id"),
                "error": f"Missing fields: {missing_fields}"
            })
            continue

        if not validate_confidence(interaction["confidence_level"]):
            validation_errors.append({
                "interaction_id": interaction.get("interaction_id"),
                "error": "Confidence level must be between 0 and 1"
            })
            continue

        interaction["normalized_text"] = normalize_text(
            interaction["raw_text"]
        )

        valid_interactions.append(interaction)

    normalized_transcript = {
        "transcript_id": transcript.get("transcript_id"),
        "candidate_id": transcript.get("candidate_id"),
        "job_id": transcript.get("job_id"),
        "session_id": transcript.get("session_id"),
        "language": transcript.get("language"),
        "created_at": transcript.get("created_at"),
        "interactions": valid_interactions
    }

    ai_screening_data = {
        "candidate_id": transcript.get("candidate_id"),
        "job_id": transcript.get("job_id"),
        "session_id": transcript.get("session_id"),
        "screening_interactions": []
    }

    for interaction in valid_interactions:
        ai_screening_data["screening_interactions"].append({
            "interaction_id": interaction["interaction_id"],
            "question_id": interaction["question_id"],
            "speaker": interaction["speaker"],
            "timestamp": interaction["timestamp"],
            "answer": interaction["normalized_text"],
            "confidence_level": interaction["confidence_level"]
        })

    normalized_transcript["validation_errors"] = validation_errors

    return normalized_transcript, ai_screening_data


def save_json(data, output_file):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def main():
    print("Starting Transcript Data Processor...")

    transcript = load_transcript()

    normalized_transcript, ai_screening_data = process_transcript(
        transcript
    )

    save_json(normalized_transcript, NORMALIZED_OUTPUT)
    save_json(ai_screening_data, AI_OUTPUT)

    total_interactions = len(transcript.get("interactions", []))
    valid_interactions = len(normalized_transcript["interactions"])
    invalid_interactions = len(
        normalized_transcript["validation_errors"]
    )

    print("Transcript processing completed.")
    print(f"Total interactions: {total_interactions}")
    print(f"Valid interactions: {valid_interactions}")
    print(f"Invalid interactions: {invalid_interactions}")
    print(f"Normalized output: {NORMALIZED_OUTPUT}")
    print(f"AI screening output: {AI_OUTPUT}")


if __name__ == "__main__":
    main()