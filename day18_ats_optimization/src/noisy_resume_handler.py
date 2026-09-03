from __future__ import annotations

import re


def normalize_noisy_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace(
        "\x00",
        " ",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    text = re.sub(
        r"[^\x20-\x7E\n]",
        " ",
        text,
    )

    text = re.sub(
        r"[!]{2,}",
        "!",
        text,
    )

    text = re.sub(
        r"[\?]{2,}",
        "?",
        text,
    )

    return text.strip()


def normalize_skill_text(text: str) -> str:

    text = normalize_noisy_text(text)

    replacements = {
        "Pyth0n": "Python",
        "JAVASCR1PT": "JavaScript",
        "P0WER BI": "Power BI",
        "SQL!!!": "SQL",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new,
        )

    return text


if __name__ == "__main__":

    noisy_resume = """
    Pyth0n     Developer!!!
    Skilled in SQL!!!
    P0WER BI
    """

    print("=" * 65)
    print("NOISY RESUME HANDLING")
    print("=" * 65)

    print("\nOriginal:")
    print(noisy_resume)

    print("\nNormalized:")
    print(
        normalize_skill_text(
            noisy_resume
        )
    )

    print("\nNoisy resume handling completed.")

    print("=" * 65)