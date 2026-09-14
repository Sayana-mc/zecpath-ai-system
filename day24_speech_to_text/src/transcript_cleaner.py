import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def load_cleaning_rules():
    with open(
        CONFIG_DIR / "cleaning_rules.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def normalize_whitespace(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_filler_words(text):
    rules = load_cleaning_rules()

    if not rules["remove_filler_words"]:
        return text

    fillers = rules["filler_words"]

    for filler in fillers:
        pattern = r"\b" + re.escape(filler) + r"\b"
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return normalize_whitespace(text)


def remove_repeated_words(text):
    words = text.split()

    if not words:
        return text

    result = [words[0]]

    for word in words[1:]:
        if word.lower() != result[-1].lower():
            result.append(word)

    return " ".join(result)


def normalize_case(text):
    text = text.strip()

    if not text:
        return text

    return text[0].upper() + text[1:]


def correct_punctuation(text):
    text = normalize_whitespace(text)

    if not text:
        return text

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.!?])", r"\1", text)

    # Avoid repeated punctuation
    text = re.sub(r"[.!?]{2,}", ".", text)

    # Add final punctuation when missing
    if text[-1] not in ".!?":
        text += "."

    return text


def clean_transcript(text):
    original_text = text

    text = normalize_whitespace(text)
    text = remove_filler_words(text)
    text = remove_repeated_words(text)
    text = normalize_whitespace(text)
    text = correct_punctuation(text)
    text = normalize_case(text)

    return {
        "raw_text": original_text,
        "clean_text": text
    }


def detect_partial_answer(text, segments):
    words = text.strip().split()

    if len(words) < 3:
        return True

    if not segments:
        return True

    last_segment = segments[-1]

    # If the transcript appears to end abruptly
    ending_words = {
        "and",
        "but",
        "because",
        "so",
        "if",
        "when",
        "which",
        "that",
        "to",
        "with"
    }

    last_word = words[-1].lower().strip(".,!?")

    if last_word in ending_words:
        return True

    return False