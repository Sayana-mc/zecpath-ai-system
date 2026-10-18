from datetime import datetime, timezone


def build_governance_report(config: dict) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": config["project_name"],
        "version": config["version"],
        "controls": {
            "human_review_required": config["governance"]["human_review_required"],
            "automatic_rejection_enabled": config["governance"]["automatic_rejection_enabled"],
            "consent_required_for_processing": config["governance"]["consent_required_for_processing"],
            "raw_transcripts_stored_by_default": config["governance"]["store_raw_transcripts_by_default"],
            "encryption_at_rest": "Fernet encryption in local reference implementation",
            "role_based_access_control": True,
            "score_and_decision_audit_logs": True,
            "hash_chained_audit_log": True
        },
        "retention_days": config["retention_days"],
        "limitations": [
            "Local reference implementation; not production certification.",
            "Authentication and session management must be supplied by the host application.",
            "Hash chaining detects tampering but is not tamper-proof if log and head are both rewritten.",
            "Consent wording, lawful basis, and retention schedules require legal/privacy review.",
            "Use a managed key vault, encrypted backups, monitoring, and access reviews in production."
        ]
    }


def governance_markdown(report: dict) -> str:
    lines = [
        "# Day 55 — AI Security & Governance Report",
        "",
        f"- Project: {report['project']}",
        f"- Version: {report['version']}",
        f"- Generated: {report['generated_at']}",
        "",
        "## Security and governance controls",
    ]
    for key, value in report["controls"].items():
        lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    lines += ["", "## Data retention"]
    for category, days in report["retention_days"].items():
        lines.append(f"- **{category.replace('_', ' ').title()}**: {days} days")
    lines += ["", "## Limitations and production actions"]
    lines += [f"- {item}" for item in report["limitations"]]
    lines += [
        "",
        "## Human oversight",
        "AI scores and recommendations are advisory. Human review is required. Automatic rejection is disabled.",
        "",
        "## Consent and minimization",
        "Process candidate data only for the recorded purpose after consent is verified. Avoid storing raw transcripts unless necessary.",
        "",
        "## Incident response",
        "Restrict access, preserve relevant audit evidence, notify the designated security/privacy owner, investigate scope, rotate compromised keys, and follow applicable notification obligations."
    ]
    return "\n".join(lines) + "\n"
