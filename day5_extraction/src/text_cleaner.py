import re


def fix_encoding_issues(text):
    """
    Fix common mojibake/encoding sequences produced during PDF extraction.
    """

    replacements = {
        "\u00e2\u20ac\u00a2": "•",   # â€¢
        "\u00e2\u20ac\u0093": "–",   # â€“
        "\u00e2\u20ac\u0094": "—",   # â€”
        "\u00e2\u20ac\u02dc": "‘",   # â€˜
        "\u00e2\u20ac\u2122": "’",   # â€™
        "\u00e2\u20ac\u0153": "“",   # â€œ
        "\u00e2\u20ac\u009d": "”",   # â€
        "\u00e2\u20ac\u00a6": "...", # â€¦
        "\u00c2\u00a0": " ",
        "\u00c2": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)
    # Normalize Unicode dashes to standard hyphen
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    return text


def normalize_whitespace(text):
    """
    Normalize spaces and blank lines.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = []

    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def normalize_bullets(text):
    """
    Convert different bullet symbols into a standard hyphen.
    """

    bullet_symbols = [
        "•",
        "●",
        "▪",
        "◦",
        "‣",
    ]

    for symbol in bullet_symbols:
        text = text.replace(symbol, "-")

    return text


def remove_noise(text):
    """
    Remove unwanted control characters and excessive blank lines.
    """

    text = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
        "",
        text
    )

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def clean_text(text):
    """
    Complete resume text-cleaning pipeline.
    """

    text = fix_encoding_issues(text)
    text = remove_noise(text)
    text = normalize_bullets(text)
    text = normalize_whitespace(text)

    return text