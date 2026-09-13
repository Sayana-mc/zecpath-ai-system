import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "day23_transcript_data_architecture" / "src"

sys.path.insert(0, str(SRC_DIR))

from transcript_processor import (
    load_transcript,
    normalize_text,
    process_transcript,
    validate_confidence
)


def test_transcript_is_not_empty():
    transcript = load_transcript()

    assert transcript
    assert len(transcript["interactions"]) > 0


def test_required_metadata_exists():
    transcript = load_transcript()

    assert "candidate_id" in transcript
    assert "job_id" in transcript
    assert "session_id" in transcript


def test_question_id_exists():
    transcript = load_transcript()

    for interaction in transcript["interactions"]:
        assert "question_id" in interaction


def test_timestamp_exists():
    transcript = load_transcript()

    for interaction in transcript["interactions"]:
        assert "timestamp" in interaction


def test_confidence_level_is_valid():
    transcript = load_transcript()

    for interaction in transcript["interactions"]:
        assert validate_confidence(
            interaction["confidence_level"]
        )


def test_text_normalization():
    text = "  Python    SQL\nPower BI  "

    result = normalize_text(text)

    assert result == "Python SQL Power BI"


def test_processing():
    transcript = load_transcript()

    normalized, ai_data = process_transcript(transcript)

    assert len(normalized["interactions"]) == 4
    assert len(ai_data["screening_interactions"]) == 4