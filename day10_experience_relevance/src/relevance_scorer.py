import re


ROLE_KEYWORDS = {
    "python developer": {
        "python",
        "developer",
        "software",
        "api",
        "backend",
        "programming",
    },
    "data analyst": {
        "data",
        "analyst",
        "sql",
        "python",
        "excel",
        "power bi",
        "tableau",
        "analytics",
    },
    "data scientist": {
        "data",
        "scientist",
        "python",
        "machine learning",
        "statistics",
        "analytics",
    },
    "ai/ml engineer": {
        "ai",
        "ml",
        "machine learning",
        "deep learning",
        "python",
        "tensorflow",
        "pytorch",
    },
    "software engineer": {
        "software",
        "engineer",
        "developer",
        "programming",
        "api",
        "database",
    },
    "hr executive": {
        "hr",
        "human resources",
        "recruitment",
        "recruiter",
        "employee",
        "talent",
    },
    "graphic designer": {
        "graphic",
        "designer",
        "design",
        "figma",
        "photoshop",
        "illustrator",
        "branding",
    },
    "marketing manager": {
        "marketing",
        "manager",
        "digital",
        "campaign",
        "sales",
        "branding",
    },
    "financial analyst": {
        "financial",
        "finance",
        "analyst",
        "accounting",
        "excel",
        "investment",
    },
    "sales manager": {
        "sales",
        "manager",
        "business",
        "customer",
        "revenue",
        "marketing",
    },
}


def normalize_role(role):
    """Normalize a role title."""

    if not role:
        return ""

    role = role.lower().strip()

    role = re.sub(
        r"[^a-z0-9\s/+-]",
        " ",
        role,
    )

    role = re.sub(
        r"\s+",
        " ",
        role,
    )

    return role


def tokenize_role(role):
    """Generate useful role tokens."""

    normalized = normalize_role(role)

    tokens = set(
        normalized.split()
    )

    for keyword_set in ROLE_KEYWORDS.values():

        for phrase in keyword_set:

            if " " in phrase and phrase in normalized:
                tokens.add(phrase)

    return tokens


def calculate_role_similarity(
    candidate_role,
    target_role,
):
    """Calculate role-to-role similarity."""

    candidate_tokens = tokenize_role(
        candidate_role
    )

    target_tokens = tokenize_role(
        target_role
    )

    if not candidate_tokens or not target_tokens:
        return 0.0

    intersection = (
        candidate_tokens
        & target_tokens
    )

    union = (
        candidate_tokens
        | target_tokens
    )

    score = len(intersection) / len(union)

    return round(score * 100, 2)


def calculate_relevance_score(
    experiences,
    target_role,
):
    """Calculate overall experience relevance."""

    if not experiences:
        return {
            "target_role": target_role,
            "relevance_score": 0.0,
            "relevant_roles": [],
        }

    scored_roles = []

    for experience in experiences:

        role = experience.get(
            "job_title",
            "",
        )

        similarity = calculate_role_similarity(
            role,
            target_role,
        )

        scored_roles.append(
            {
                "job_title": role,
                "company": experience.get(
                    "company"
                ),
                "similarity_score": similarity,
            }
        )

    relevant_roles = [
        role
        for role in scored_roles
        if role["similarity_score"] >= 30
    ]

    if scored_roles:

        overall_score = max(
            role["similarity_score"]
            for role in scored_roles
        )

    else:

        overall_score = 0.0

    return {
        "target_role": target_role,
        "relevance_score": round(
            overall_score,
            2,
        ),
        "relevant_roles": relevant_roles,
    }