"""Day 49: Malpractice & Interview Integrity Detection with Fair Review Safeguards."""

import uuid
from typing import Any

try:
    from . import database
except ImportError:
    from src import database


DEFAULT_INTEGRITY_THRESHOLDS: dict[str, dict[str, Any]] = {
    "tab_switch_count": {
        "warning_at": 3,
        "risk_points": 15,
        "tag": "TAB_SWITCH_ACTIVITY",
    },
    "focus_loss_count": {
        "warning_at": 3,
        "risk_points": 15,
        "tag": "REPEATED_FOCUS_LOSS",
    },
    "external_voice_events": {
        "warning_at": 2,
        "risk_points": 20,
        "tag": "POSSIBLE_EXTERNAL_AUDIO",
    },
    "repeated_looking_away_events": {
        "warning_at": 5,
        "risk_points": 10,
        "tag": "REPEATED_LOOK_AWAY",
    },
}


class IntegrityDetectionEngine:
    """Monitors consented session integrity events and provides non-punitive audit reviews."""

    def __init__(self, thresholds: dict[str, dict[str, Any]] | None = None):
        self.thresholds = thresholds or DEFAULT_INTEGRITY_THRESHOLDS

    @staticmethod
    def get_risk_level(risk_score: int) -> str:
        if risk_score <= 24:
            return "LOW"
        if risk_score <= 49:
            return "MODERATE"
        return "HIGH"

    def evaluate_events(
        self,
        events: list[dict[str, Any]],
        has_consent: bool = True,
    ) -> dict[str, Any]:
        """Convenience method evaluating event lists and returning risk classification."""
        if not has_consent:
            return {
                "total_risk_points": 0,
                "risk_level": "LOW",
                "requires_human_review": True,
                "automatic_rejection": False,
                "review_flags": ["Candidate did not consent to integrity monitoring"],
            }
        risk_points = 0
        review_flags = []
        for e in events:
            etype = e.get("event_type", "")
            duration = e.get("duration_seconds", 0)
            if duration >= 10:
                risk_points += 25
                review_flags.append(f"Extended {etype} event ({duration}s)")
            elif duration > 0:
                risk_points += 5
        risk_level = self.get_risk_level(risk_points)
        requires_review = risk_level in ("MODERATE", "HIGH")
        return {
            "total_risk_points": risk_points,
            "risk_level": risk_level,
            "requires_human_review": requires_review,
            "automatic_rejection": False,
            "review_flags": review_flags,
        }

    def analyze_integrity_session(
        self,
        candidate_id: str,
        session_id: str,
        consent_recorded: bool,
        events: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """Analyzes session events, calculates risk score, and generates human review alerts."""
        if not consent_recorded:
            return {
                "candidate_id": candidate_id,
                "session_id": session_id,
                "consent_recorded": False,
                "status": "CONSENT_NOT_RECORDED",
                "message": "Candidate did not record consent for environment/browser integrity monitoring.",
            }

        input_events = events or {
            "tab_switch_count": 0,
            "focus_loss_count": 0,
            "external_voice_events": 0,
            "repeated_looking_away_events": 0,
        }

        flags: list[dict[str, Any]] = []
        risk_score = 0
        flagged_categories = 0

        for name, rule in self.thresholds.items():
            count = max(0, int(input_events.get(name, 0)))
            if count >= rule["warning_at"]:
                flagged_categories += 1
                risk_score += rule["risk_points"]
                flags.append({
                    "event": name,
                    "count": count,
                    "tag": rule["tag"],
                    "warning_threshold": rule["warning_at"],
                    "risk_points": rule["risk_points"],
                    "evidence": f"Candidate triggered {name} {count} times (warning threshold: {rule['warning_at']}).",
                })

        if flagged_categories >= 3:
            risk_score += 10

        risk_level = self.get_risk_level(risk_score)

        audit_trail = {
            "evaluated_events": input_events,
            "safeguards": {
                "automatic_rejection_disabled": True,
                "human_review_required": risk_level in ["MODERATE", "HIGH"],
                "single_event_proves_malpractice": False,
            },
        }

        record_id = f"INTG_{uuid.uuid4().hex[:8].upper()}"
        record = {
            "record_id": record_id,
            "candidate_id": candidate_id,
            "session_id": session_id,
            "consent_recorded": 1,
            "tab_switch_count": input_events.get("tab_switch_count", 0),
            "focus_loss_count": input_events.get("focus_loss_count", 0),
            "external_voice_events": input_events.get("external_voice_events", 0),
            "repeated_looking_away_events": input_events.get("repeated_looking_away_events", 0),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "review_flags": flags,
            "audit_trail": audit_trail,
        }
        saved = database.save_candidate_integrity_record(record)
        return saved


integrity_engine = IntegrityDetectionEngine()
IntegrityMonitor = IntegrityDetectionEngine
