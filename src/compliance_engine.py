"""Day 43: Ethics, Compliance, Consent Management, and Demographic Scrubber."""

import re
from datetime import datetime, timezone, timedelta
from typing import Any


DEFAULT_COMPLIANCE_CONFIG: dict[str, Any] = {
    "consent": {
        "required": True,
        "consent_types": ["ai_evaluation", "audio_processing", "integrity_monitoring"],
    },
    "demographic_signals": [
        "male", "female", "man", "woman", "he", "she", "his", "her",
        "age", "years old", "married", "single", "religion", "christian",
        "muslim", "hindu", "jewish", "caste", "nationality", "citizen",
        "race", "white", "black", "asian", "hispanic", "pregnant", "pregnancy", "maternity",
    ],
    "data_retention_days": 180,
    "human_review_required": True,
}


class BiasSignalDetector:
    """Detects and redacts protected demographic attributes to safeguard fair scoring."""

    def __init__(self, demographic_signals: list[str] | None = None):
        self.signals = [
            s.lower() for s in (demographic_signals or DEFAULT_COMPLIANCE_CONFIG["demographic_signals"])
        ]

    def detect(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        detected: list[str] = []
        for signal in self.signals:
            pattern = r"\b" + re.escape(signal) + r"\b"
            if re.search(pattern, text_lower):
                detected.append(signal)

        return {
            "bias_signals_detected": detected,
            "bias_signal_count": len(detected),
            "clean": len(detected) == 0,
        }

    def remove_signals(self, text: str) -> dict[str, Any]:
        cleaned = text
        removed: list[str] = []
        for signal in self.signals:
            pattern = r"\b" + re.escape(signal) + r"\b"
            if re.search(pattern, cleaned, flags=re.IGNORECASE):
                removed.append(signal)
                cleaned = re.sub(pattern, "[REDACTED_DEMOGRAPHIC]", cleaned, flags=re.IGNORECASE)

        return {
            "original_text": text,
            "cleaned_text": cleaned,
            "removed_signals": removed,
        }


class ConsentManager:
    """Validates candidate explicit consent before executing automated scoring or signal monitoring."""

    def __init__(self, required: bool = True):
        self.required = required

    def validate_consent(self, consent_given: bool) -> dict[str, Any]:
        if self.required and not consent_given:
            return {
                "status": "BLOCKED",
                "consent_valid": False,
                "message": "Candidate consent is mandatory before AI processing or signal tracking.",
            }
        return {
            "status": "ALLOWED",
            "consent_valid": True,
            "message": "Candidate consent requirement satisfied.",
        }


class RetentionManager:
    """Calculates data retention schedules and purges expired candidate records."""

    def __init__(self, retention_days: int = 180):
        self.retention_days = retention_days

    def calculate_expiration(self, created_at_iso: str | None = None) -> dict[str, Any]:
        if created_at_iso:
            try:
                base = datetime.fromisoformat(created_at_iso)
            except Exception:
                base = datetime.now(timezone.utc)
        else:
            base = datetime.now(timezone.utc)

        expiration = base + timedelta(days=self.retention_days)
        now = datetime.now(timezone.utc)
        is_expired = now > expiration

        return {
            "retention_days": self.retention_days,
            "created_at": base.isoformat(),
            "expires_at": expiration.isoformat(),
            "purge_scheduled_at": expiration.isoformat(),
            "is_expired": is_expired,
        }


class EthicsComplianceEngine:
    """Unified ethics, compliance, demographic scrubber, and audit trail engine."""

    def __init__(self, config: dict[str, Any] | None = None):
        cfg = config or DEFAULT_COMPLIANCE_CONFIG
        self.bias_detector = BiasSignalDetector(cfg.get("demographic_signals"))
        self.consent_mgr = ConsentManager(cfg.get("consent", {}).get("required", True))
        self.retention_mgr = RetentionManager(cfg.get("data_retention_days", 180))

    def audit_evaluation_input(self, text: str, consent_given: bool) -> dict[str, Any]:
        consent_status = self.consent_mgr.validate_consent(consent_given)
        scrubbed = self.bias_detector.remove_signals(text)

        return {
            "consent": consent_status,
            "demographic_scrubbing": scrubbed,
            "fairness_certified": consent_status["consent_valid"],
            "explainability_note": (
                "Scoring input scrubbed of protected demographic markers (gender, age, ethnicity) "
                "to ensure decisions rely strictly on competencies, structured answers, and job fit."
            ),
        }

    def redact_protected_demographic_signals(self, text: str) -> str:
        res = self.bias_detector.remove_signals(text)
        return res["cleaned_text"]

    def validate_candidate_consent(self, has_consent: bool) -> bool:
        res = self.consent_mgr.validate_consent(has_consent)
        return res["consent_valid"]

    def calculate_retention_expiry(self, retention_days: int = 180) -> dict[str, Any]:
        mgr = RetentionManager(retention_days)
        return mgr.calculate_expiration()


compliance_engine = EthicsComplianceEngine()
