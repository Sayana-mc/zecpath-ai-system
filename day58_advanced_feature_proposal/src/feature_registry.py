"""Structured registry of proposed features and their guardrails."""

FEATURES = [
    {
        "id": "F01",
        "name": "Consent-based video interview review",
        "category": "video_analysis",
        "priority": "MEDIUM",
        "status": "PROPOSED",
        "description": "Optional recording review, timestamps, and transcript alignment for interviewers.",
        "guardrails": ["explicit consent", "withdrawal option", "limited retention", "human review", "no emotion/personality inference"],
        "acceptance_criteria": ["recording is off by default", "access is role-restricted", "candidate can request deletion"]
    },
    {
        "id": "F02",
        "name": "Emotion detection",
        "category": "emotion_detection",
        "priority": "NOT_RECOMMENDED",
        "status": "EXCLUDED_FROM_HIRING_DECISIONS",
        "description": "Do not infer emotions, honesty, confidence, or personality from facial expressions or voice for hiring decisions.",
        "guardrails": ["not used for ranking", "not used for rejection", "no proxy personality scoring"],
        "acceptance_criteria": ["no emotion score is generated or stored"]
    },
    {
        "id": "F03",
        "name": "Real-time interview feedback",
        "category": "real_time_feedback",
        "priority": "HIGH",
        "status": "PROPOSED",
        "description": "Optional practice-mode feedback on answer structure, relevance to a rubric, and technical concepts.",
        "guardrails": ["practice mode only by default", "transparent rubric", "candidate can opt out", "no hidden scoring"],
        "acceptance_criteria": ["feedback references observable answer content", "candidate sees why feedback was provided"]
    },
    {
        "id": "F04",
        "name": "AI coaching system",
        "category": "candidate_coaching",
        "priority": "HIGH",
        "status": "PROPOSED",
        "description": "Creates practice plans, sample questions, and learning activities from job-related skill gaps.",
        "guardrails": ["recommendations are advisory", "candidate controls participation", "coaching usage is not a hiring score"],
        "acceptance_criteria": ["every suggestion maps to a role skill", "no unsupported claims about candidate ability"]
    },
    {
        "id": "F05",
        "name": "Candidate improvement suggestions",
        "category": "candidate_improvement",
        "priority": "HIGH",
        "status": "PROTOTYPE_AVAILABLE",
        "description": "Identifies missing target skills and suggests practical learning actions.",
        "guardrails": ["based only on supplied skills and role requirements", "candidate can correct inputs"],
        "acceptance_criteria": ["each missing skill has a concrete next step"]
    },
    {
        "id": "F06",
        "name": "Interview analytics dashboard",
        "category": "interview_analytics",
        "priority": "MEDIUM",
        "status": "PROPOSED",
        "description": "Shows stage completion, rubric coverage, review latency, and reviewer disagreement at aggregate level.",
        "guardrails": ["role-based access", "small-group privacy protections", "no emotion/personality metrics"],
        "acceptance_criteria": ["metric definitions are documented", "dashboard data can be audited"]
    }
]


def list_features():
    """Return a defensive copy of feature definitions."""
    return [dict(feature, guardrails=list(feature["guardrails"]), acceptance_criteria=list(feature["acceptance_criteria"])) for feature in FEATURES]


def get_feature(feature_id):
    """Return one feature by ID or raise KeyError."""
    for feature in FEATURES:
        if feature["id"] == feature_id:
            return dict(feature, guardrails=list(feature["guardrails"]), acceptance_criteria=list(feature["acceptance_criteria"]))
    raise KeyError(f"Unknown feature ID: {feature_id}")
