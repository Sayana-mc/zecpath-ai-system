import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stt_processor import SpeechToTextProcessor
from transcript_normalizer import normalize_transcription


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = PROJECT_ROOT / "data" / "audio" / "clean"
OUTPUT_DIR = PROJECT_ROOT / "output"


def main():

    OUTPUT_DIR.mkdir(exist_ok=True)

    audio_files = list(AUDIO_DIR.glob("*.wav"))

    if not audio_files:
        print("No audio files found.")
        print(
            f"Add WAV files to: {AUDIO_DIR}"
        )
        return

    print("Starting Day 24 Speech-to-Text Processor...")

    processor = SpeechToTextProcessor()

    results = []

    for audio_file in audio_files:

        print(f"\nProcessing: {audio_file.name}")

        stt_result = processor.transcribe(audio_file)

        normalized = normalize_transcription(
            stt_result
        )

        result = {
            "audio_file": audio_file.name,
            "speech_to_text": stt_result,
            "normalized_transcript": normalized
        }

        results.append(result)

        print(
            "Raw transcript:",
            stt_result["text"]
        )

        print(
            "Clean transcript:",
            normalized["clean_text"]
        )

        print(
            "Partial answer:",
            normalized["partial_answer"]
        )

    output_file = (
        OUTPUT_DIR / "clean_transcripts.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            results,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("\nProcessing completed.")
    print(f"Processed audio files: {len(results)}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()