"""
Skill normalization utilities.
"""

import re

from .skill_dictionary import (
    SKILL_DICTIONARY,
    SKILL_STACKS
)


def normalize_text(text):
    """
    Normalize text for matching.
    """

    if not text:
        return ""

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_skill_name(skill):
    """
    Return canonical skill name.
    """

    if not skill:
        return None

    normalized = normalize_text(skill)

    for category, skills in SKILL_DICTIONARY.items():

        for canonical, aliases in skills.items():

            if normalized == normalize_text(canonical):
                return canonical

            for alias in aliases:

                if normalized == normalize_text(alias):
                    return canonical

    for stack_name in SKILL_STACKS:

        if normalized == normalize_text(stack_name):
            return stack_name

    return None


def get_skill_category(skill):
    """
    Return category of a canonical skill.
    """

    canonical = normalize_skill_name(skill)

    if canonical in SKILL_STACKS:
        return "technical"

    for category, skills in SKILL_DICTIONARY.items():

        if canonical in skills:
            return category

    return "unknown"