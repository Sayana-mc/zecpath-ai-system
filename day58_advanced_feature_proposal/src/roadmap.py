"""Roadmap loading and basic schema validation."""


def validate_roadmap(data):
    if not isinstance(data, dict):
        raise ValueError("Roadmap must be a JSON object")
    if not isinstance(data.get("phases"), list) or not data["phases"]:
        raise ValueError("Roadmap must contain at least one phase")
    principles = data.get("principles")
    if not isinstance(principles, dict):
        raise ValueError("Roadmap principles must be an object")
    if principles.get("human_review_required") is not True:
        raise ValueError("Human review must remain required")
    if principles.get("automatic_rejection_enabled") is not False:
        raise ValueError("Automatic rejection must remain disabled")
    if principles.get("emotion_inference_for_hiring_enabled") is not False:
        raise ValueError("Emotion inference for hiring decisions must remain disabled")
    ids = set()
    for phase in data["phases"]:
        if not isinstance(phase, dict) or not phase.get("id") or not phase.get("name"):
            raise ValueError("Every roadmap phase needs an ID and name")
        if phase["id"] in ids:
            raise ValueError(f"Duplicate roadmap phase ID: {phase['id']}")
        ids.add(phase["id"])
        if not isinstance(phase.get("features"), list) or not isinstance(phase.get("exit_criteria"), list):
            raise ValueError("Every phase needs features and exit_criteria lists")
    return data
