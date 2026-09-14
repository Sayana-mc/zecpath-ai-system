import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "day24_speech_to_text" / "src"

sys.path.insert(0, str(SRC_DIR))

from transcript_cleaner import (
    normalize_whitespace,
    remove_filler_words,
    remove_repeated_words,
    clean_transcript,
    detect_partial_answer
)


def test_normalize_whitespace():

    text = "Hello    Python\nSQL   Power BI"

    result = normalize_whitespace(text)

    assert result == "Hello Python SQL Power BI"


def test_remove_filler_words():

    text = "Um I have experience in Python and uh SQL"

    result = remove_filler_words(text)

    assert "Um" not in result
    assert "uh" not in result.lower()
    assert "Python" in result
    assert "SQL" in result


def test_remove_repeated_words():

    text = "I I I have have experience"

    result = remove_repeated_words(text)

    assert result == "I have experience"


def test_clean_transcript():

    text = "  um hello   my name is Sayana  "

    result = clean_transcript(text)

    assert result["clean_text"]
    assert result["clean_text"][0].isupper()


def test_partial_answer():

    text = "I have experience in Python and"

    segments = [
        {
            "start": 0.0,
            "end": 3.0,
            "text": text
        }
    ]

    result = detect_partial_answer(
        text,
        segments
    )

    assert result is True


def test_complete_answer():

    text = (
        "I have experience in Python "
        "and SQL."
    )

    segments = [
        {
            "start": 0.0,
            "end": 3.0,
            "text": text
        }
    ]

    result = detect_partial_answer(
        text,
        segments
    )

    assert result is False