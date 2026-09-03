from __future__ import annotations


IMPORTANT_SECTIONS = {
    "summary",
    "skills",
    "experience",
    "education",
    "projects",
    "certifications",
}


def optimize_resume_for_model(
    sections: dict[str, str],
) -> str:

    selected = []

    for section_name, content in sections.items():

        normalized_name = (
            section_name
            .strip()
            .lower()
        )

        if normalized_name not in IMPORTANT_SECTIONS:
            continue

        if not content:
            continue

        selected.append(
            f"{section_name.upper()}:\n{content.strip()}"
        )

    return "\n\n".join(selected)


def limit_text(
    text: str,
    max_characters: int = 12000,
) -> str:

    if len(text) <= max_characters:
        return text

    return text[:max_characters]


if __name__ == "__main__":

    print("=" * 65)
    print("LLM PROMPT OPTIMIZATION")
    print("=" * 65)

    print("\nOptimization techniques:")
    print("- Send relevant resume sections only")
    print("- Remove unnecessary content")
    print("- Limit excessive text")
    print("- Reduce prompt size")

    print("\nPrompt optimizer ready.")

    print("=" * 65)