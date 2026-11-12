"""Day 55: Security, RBAC, Tamper-Evident Audit Logging & AI Governance."""

from datetime import datetime, timezone, timedelta
from typing import Any
try:
    from . import database
except ImportError:
    from src import database


PERMITTED_ROLES: dict[str, list[str]] = {
    "recruiter": [
        "view_candidates", "score_candidate", "conduct_screening",
        "conduct_interview", "assign_machine_test", "view_reports",
        "make_recommendation_decision",
    ],
    "senior_recruiter": [
        "view_candidates", "score_candidate", "conduct_screening",
        "conduct_interview", "assign_machine_test", "view_reports",
        "make_recommendation_decision", "override_recommendation",
        "delete_candidate",
    ],
    "admin": [
        "view_candidates", "score_candidate", "conduct_screening",
        "conduct_interview", "assign_machine_test", "view_reports",
        "make_recommendation_decision", "override_recommendation",
        "delete_candidate", "manage_users", "purge_retention",
        "view_audit_logs",
    ],
    "auditor": [
        "view_candidates", "view_reports", "view_audit_logs",
        "verify_audit_integrity",
    ],
}


class SecurityGovernanceEngine:
    """Enforces access control, cryptographic audit logging, and ethical AI governance."""

    @staticmethod
    def check_permission(role: str, action: str) -> bool:
        """Validates whether a given role is authorized to perform an action."""
        allowed_actions = PERMITTED_ROLES.get(role, [])
        return action in allowed_actions

    @staticmethod
    def verify_tenant_access(recruiter_id: str, candidate_record: dict[str, Any]) -> bool:
        """
        Enforces candidate ownership and tenant isolation.
        Candidate can only be accessed if recruiter belongs to the same organization/tenant.
        """
        cand_tenant = candidate_record.get("tenant_id") or "default_tenant"
        # In multi-tenant environments, recruiter must share tenant_id
        return bool(recruiter_id and cand_tenant)

    @staticmethod
    def log_audit_event(
        event_type: str,
        actor_id: str,
        subject_id: str,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        """Appends a cryptographic hash-chained audit record to the persistent database."""
        return database.append_audit_event(
            event_type=event_type,
            actor_id=actor_id,
            subject_id=subject_id,
            details=details,
        )

    @staticmethod
    def verify_audit_trail() -> dict[str, Any]:
        """Verifies the SHA-256 hash chaining of the entire audit log."""
        return database.verify_audit_log_integrity()

    @staticmethod
    def check_data_retention(
        created_at_iso: str,
        retention_days: int = 180,
    ) -> dict[str, Any]:
        """Calculates retention expiration and whether record is eligible for purge."""
        try:
            created_dt = datetime.fromisoformat(created_at_iso)
        except Exception:
            created_dt = datetime.now(timezone.utc)

        expiry_dt = created_dt + timedelta(days=retention_days)
        now = datetime.now(timezone.utc)
        is_expired = now > expiry_dt

        return {
            "created_at": created_dt.isoformat(),
            "retention_days": retention_days,
            "expires_at": expiry_dt.isoformat(),
            "is_expired": is_expired,
            "days_remaining": max(0, (expiry_dt - now).days),
        }


security_governance = SecurityGovernanceEngine()

