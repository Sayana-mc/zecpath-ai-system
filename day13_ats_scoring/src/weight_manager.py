DEFAULT_WEIGHTS = {
    "skill_match": 0.35,
    "experience_relevance": 0.20,
    "education_alignment": 0.15,
    "semantic_similarity": 0.30,
}


ROLE_WEIGHTS = {
    "data analyst": {
        "skill_match": 0.35,
        "experience_relevance": 0.20,
        "education_alignment": 0.15,
        "semantic_similarity": 0.30,
    },

    "python developer": {
        "skill_match": 0.40,
        "experience_relevance": 0.20,
        "education_alignment": 0.10,
        "semantic_similarity": 0.30,
    },

    "machine learning engineer": {
        "skill_match": 0.35,
        "experience_relevance": 0.25,
        "education_alignment": 0.15,
        "semantic_similarity": 0.25,
    },

    "graphic designer": {
        "skill_match": 0.40,
        "experience_relevance": 0.20,
        "education_alignment": 0.10,
        "semantic_similarity": 0.30,
    },

    "hr executive": {
        "skill_match": 0.30,
        "experience_relevance": 0.30,
        "education_alignment": 0.15,
        "semantic_similarity": 0.25,
    },
}


def validate_weights(weights):
    required_keys = {
        "skill_match",
        "experience_relevance",
        "education_alignment",
        "semantic_similarity",
    }

    if set(weights.keys()) != required_keys:
        raise ValueError("Invalid weight keys.")

    total = sum(weights.values())

    if abs(total - 1.0) > 0.0001:
        raise ValueError(
            f"Weights must sum to 1.0. Current total: {total}"
        )

    return True


def load_role_weights(role):
    """
    Load role-specific ATS weights.
    Falls back to default weights if the role is unknown.
    """

    role_key = str(role).strip().lower()

    weights = ROLE_WEIGHTS.get(
        role_key,
        DEFAULT_WEIGHTS
    ).copy()

    validate_weights(weights)

    return weights