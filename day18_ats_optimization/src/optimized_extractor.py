from __future__ import annotations

import re
from pathlib import Path


WHITESPACE_RE = re.compile(r"\s+")
BULLET_RE = re.compile(r"^[\u2022\u2023\u25E6\u2043\u2219•▪◦]\s*")


def clean_text(text: str) -> str:
    """
    Efficient resume text normalization.
    """

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line = BULLET_RE.sub("- ", line)

        line = WHITESPACE_RE.sub(
            " ",
            line,
        )

        lines.append(line)

    return "\n".join(lines)


def extract_text_from_txt(file_path: str | Path) -> str:
    """
    Fast text extraction for TXT files.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Resume not found: {file_path}"
        )

    text = file_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    return clean_text(text)


if __name__ == "__main__":

    print("=" * 65)
    print("OPTIMIZED TEXT EXTRACTION ENGINE")
    print("=" * 65)

    print("\nFeatures:")
    print("- Single-pass text normalization")
    print("- Whitespace normalization")
    print("- Bullet normalization")
    print("- UTF-8 error tolerance")
    print("- Reduced unnecessary processing")

    print("\nOptimized extractor ready.")

    print("=" * 65)