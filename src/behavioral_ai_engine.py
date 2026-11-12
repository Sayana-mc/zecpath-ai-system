"""Day 48: Behavioral AI Research, Observation Engine, and Ethical Safeguards."""

import uuid
from typing import Any

try:
    from . import database
except ImportError:
    from src import database


DEFAULT_BEHAVIORAL_WEIGHTS: dict[str, float] = {
    "attention_consistency": 0.35,
    "engagement_level": 0.25,
    "composure_indicator": 0.20,
    "pacing_regularity": 0.20,
}

MANDATORY_BEHAVIORAL_DISCLAIMER: str = (
    "Behavioral signals reflect observable pacing, communicative responsiveness, and focus indicators during "
    "this session. They do NOT evaluate personality, honesty, cognitive capacity, or mental health. Candidates "
    "must never be penalized for neurodivergence, cultural variance, or equipment limitations. Observations remain "
    "strictly separate from technical competency scoring. This assistive evaluation is non-binding and advisory only."
)


class BehavioralAIEngine:
    """Processes consented behavioral observations with strict fairness safeguards."""

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or DEFAULT_BEHAVIORAL_WEIGHTS

    def analyze_behavioral_sample(
        self,
        candidate_id: str,
        session_id: str,
        consent_recorded: bool,
        metrics: dict[str, float] | None = None,
        observation_notes: str | None = None,
    ) -> dict[str, Any]:
        """Analyzes consented candidate observations and computes signal consistency index."""
        if not consent_recorded:
            return {
                "candidate_id": candidate_id,
                "session_id": session_id,
                "consent_recorded": False,
                "status": "OPTED_OUT_OR_DECLINED",
                "message": "Candidate declined or did not record consent for behavioral observation.",
                "disclaimer": MANDATORY_BEHAVIORAL_DISCLAIMER,
            }

        input_metrics = metrics or {
            "attention_consistency": 0.85,
            "engagement_level": 0.80,
            "composure_indicator": 0.85,
            "pacing_regularity": 0.80,
        }

        # Validate bounds [0.0, 1.0]
        validated: dict[str, float] = {}
        for k, weight in self.weights.items():
            val = input_metrics.get(k, 0.75)
            val = max(0.0, min(1.0, float(val)))
            validated[k] = val

        weighted_score = sum(validated[k] * self.weights[k] for k in self.weights) * 100.0
        consistency_index = round(weighted_score, 2)

        if consistency_index >= 75.0:
            description = "High behavioral and communicative consistency observed throughout the session."
        elif consistency_index >= 50.0:
            description = "Moderate variability in pacing and communication cues observed."
        else:
            description = "Noticeable variability in pacing and responsiveness observed."

        record_id = f"BEH_{uuid.uuid4().hex[:8].upper()}"
        record = {
            "record_id": record_id,
            "candidate_id": candidate_id,
            "session_id": session_id,
            "consent_recorded": 1,
            "signal_consistency_index": consistency_index,
            "signal_description": description,
            "metrics": validated,
            "disclaimer": MANDATORY_BEHAVIORAL_DISCLAIMER,
        }
        try:
            saved = database.save_candidate_behavioral_record(record)
            return saved
        except Exception:
            return record

    def evaluate_observations(
        self,
        observations: list[dict[str, Any]],
        has_consent: bool = True,
    ) -> dict[str, Any]:
        """Convenience method evaluating candidate observations and returning consistency index."""
        if not has_consent:
            return {
                "consistency_index": 0.0,
                "requires_human_review": True,
                "disclaimer": MANDATORY_BEHAVIORAL_DISCLAIMER,
                "status": "OPTED_OUT_OR_DECLINED",
            }
        neg_count = sum(1 for o in observations if o.get("impact") == "negative")
        pos_count = sum(1 for o in observations if o.get("impact") == "positive")
        total = max(1, len(observations))
        score = max(0.0, min(100.0, 100.0 - (neg_count / total * 50.0) + (pos_count / total * 10.0)))
        requires_review = score < 60.0 or neg_count >= 2
        return {
            "consistency_index": round(score, 2),
            "requires_human_review": requires_review,
            "disclaimer": MANDATORY_BEHAVIORAL_DISCLAIMER,
            "observations_count": len(observations),
        }


behavioral_ai_engine = BehavioralAIEngine()
