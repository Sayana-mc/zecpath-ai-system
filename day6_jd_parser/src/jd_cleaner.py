import re


def clean_jd_text(text):
    """
    Clean and normalize job description text.
    """

    if not text:
        return ""

    # Normalize common encoding artifacts
    replacements = {
        "\u00e2\u0080\u0093": "-",
        "\u00e2\u0080\u0094": "-",
        "\u00e2\u0080\u00a2": "-",
        "\u00e2\u0080\u0099": "'",
        "\u00e2\u0080\u009c": '"',
        "\u00e2\u0080\u009d": '"',
        "\u2022": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize line breaks
    text = re.sub(r"\n\s*\n+", "\n", text)

    # Remove unnecessary spaces
    text = "\n".join(line.strip() for line in text.splitlines())

    return text.strip()


def normalize_title(title):
    """
    Normalize job title formatting.
    """

    if not title:
        return ""

    title = clean_jd_text(title)

    return " ".join(word.capitalize() for word in title.split())


def normalize_experience(experience):
    """
    Normalize experience range.
    """

    if not experience:
        return ""

    experience = str(experience).strip()

    experience = experience.replace("years", "")
    experience = experience.replace("year", "")
    experience = experience.strip()

    return experience