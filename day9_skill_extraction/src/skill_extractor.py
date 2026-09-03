"""
Day 9 Skill Extraction Engine.

Extracts technical, business, creative and soft skills
from structured resume sections.
"""

import re

from .skill_dictionary import (
    SKILL_DICTIONARY,
    SKILL_STACKS
)

from .skill_normalizer import (
    normalize_text,
    normalize_skill_name,
    get_skill_category
)


def calculate_confidence(
    skill,
    source,
    exact_match=False,
    alias_match=False,
    stack_match=False
):
    """
    Calculate confidence score for an extracted skill.
    """

    score = 0.50

    if source == "SKILLS":
        score += 0.20

    elif source == "WORK EXPERIENCE":
        score += 0.15

    elif source == "PROJECTS":
        score += 0.15

    elif source == "CERTIFICATIONS":
        score += 0.10

    if exact_match:
        score += 0.20

    elif alias_match:
        score += 0.15

    if stack_match:
        score += 0.10

    return min(round(score, 2), 1.0)


def find_skill_matches(text):
    """
    Find direct and alias skill matches.
    """

    normalized_text = normalize_text(text)

    matches = []

    for category, skills in SKILL_DICTIONARY.items():

        for canonical, aliases in skills.items():

            canonical_pattern = (
                r"(?<!\w)"
                + re.escape(normalize_text(canonical))
                + r"(?!\w)"
            )

            if re.search(
                canonical_pattern,
                normalized_text
            ):
                matches.append({
                    "skill": canonical,
                    "category": category,
                    "match_type": "exact"
                })

                continue

            for alias in aliases:

                alias_pattern = (
                    r"(?<!\w)"
                    + re.escape(normalize_text(alias))
                    + r"(?!\w)"
                )

                if re.search(
                    alias_pattern,
                    normalized_text
                ):

                    matches.append({
                        "skill": canonical,
                        "category": category,
                        "match_type": "alias"
                    })

                    break

    return matches


def expand_skill_stacks(text):
    """
    Detect stacks such as MERN and MEAN and expand
    them into their component skills.
    """

    normalized_text = normalize_text(text)

    matches = []

    for stack_name, components in SKILL_STACKS.items():

        pattern = (
            r"(?<!\w)"
            + re.escape(normalize_text(stack_name))
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            normalized_text
        ):

            matches.append({
                "stack": stack_name,
                "components": components
            })

    return matches


def deduplicate_skills(skills):
    """
    Remove duplicate skills while preserving
    the highest confidence record.
    """

    unique = {}

    for item in skills:

        skill = item["skill"]

        if skill not in unique:

            unique[skill] = item

        else:

            if item["confidence"] > unique[skill]["confidence"]:

                unique[skill] = item

    return list(unique.values())


def extract_skills_from_text(
    text,
    source="OTHER"
):
    """
    Extract skills from a single text block.
    """

    if not text:
        return []

    results = []

    matches = find_skill_matches(text)

    for match in matches:

        confidence = calculate_confidence(
            skill=match["skill"],
            source=source,
            exact_match=(
                match["match_type"] == "exact"
            ),
            alias_match=(
                match["match_type"] == "alias"
            )
        )

        results.append({
            "skill": match["skill"],
            "category": match["category"],
            "source": source,
            "match_type": match["match_type"],
            "confidence": confidence
        })

    stack_matches = expand_skill_stacks(text)

    for stack in stack_matches:

        results.append({
            "skill": stack["stack"],
            "category": "technical",
            "source": source,
            "match_type": "skill_stack",
            "confidence": calculate_confidence(
                skill=stack["stack"],
                source=source,
                stack_match=True
            )
        })

        for component in stack["components"]:

            category = get_skill_category(component)

            results.append({
                "skill": component,
                "category": category,
                "source": source,
                "match_type": "stack_component",
                "confidence": 0.90
            })

    return deduplicate_skills(results)


def extract_skills_from_sections(sections):
    """
    Extract skills from multiple resume sections.
    """

    all_skills = []

    priority_sections = [
        "SKILLS",
        "WORK EXPERIENCE",
        "PROJECTS",
        "CERTIFICATIONS"
    ]

    for section in priority_sections:

        text = sections.get(
            section,
            ""
        )

        extracted = extract_skills_from_text(
            text,
            source=section
        )

        all_skills.extend(extracted)

    return deduplicate_skills(all_skills)