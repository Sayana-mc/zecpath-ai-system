
import re


INTENT_PATTERNS = {
    "explain_score": [
        r"\bexplain\b.*\bscore\b",
        r"\bwhy\b.*\bscore\b",
        r"\bscore\b.*\bexplanation\b"
    ],
    "summarize_report": [
        r"\bsummar(?:y|ize|ise)\b.*\breport\b",
        r"\bcandidate report\b",
        r"\bevaluation summary\b"
    ],
    "show_missing_rounds": [
        r"\bmissing\b.*\brounds?\b",
        r"\bincomplete\b.*\brounds?\b",
        r"\bwhich\b.*\brounds?\b.*\bmissing\b"
    ],
    "explain_role_fit": [
        r"\brole fit\b",
        r"\bexplain\b.*\bsuitability\b",
        r"\bcandidate suitability\b"
    ],
    "show_evaluation_results": [
        r"\bevaluation results\b",
        r"\bshow\b.*\bassessment results\b",
        r"\bshow\b.*\bscores\b"
    ]
}


def detect_intent(text):
    """Return one supported intent or unknown; ambiguous matches are flagged."""

    if not isinstance(text, str) or not text.strip():
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "status": "NEEDS_CLARIFICATION",
            "matched_patterns": []
        }

    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    matches = []

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, normalized):
                matches.append(intent)
                break

    if len(matches) == 1:
        return {
            "intent": matches[0],
            "confidence": 1.0,
            "status": "MATCHED_RULE",
            "matched_patterns": matches
        }

    if len(matches) > 1:
        return {
            "intent": "ambiguous",
            "confidence": 0.0,
            "status": "NEEDS_CLARIFICATION",
            "matched_patterns": matches
        }

    return {
        "intent": "unknown",
        "confidence": 0.0,
        "status": "NEEDS_CLARIFICATION",
        "matched_patterns": []
    }
