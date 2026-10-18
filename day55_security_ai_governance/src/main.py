import json
from pathlib import Path
from .access_control import AccessController, Principal
from .audit_trail import AuditTrail
from .consent import ConsentRegistry
from .governance import build_governance_report, governance_markdown
from .secure_storage import load_or_create_key, SecureFileStore
from .retention import retention_policy
from .security_errors import AccessDenied, ConsentRequired

ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict:
    return json.loads((ROOT / "config" / "governance_config.json").read_text(encoding="utf-8"))


def main() -> None:
    config = load_config()
    for directory in ("data/audit", "data/consent", "data/secure_storage", "output"):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)

    audit = AuditTrail(
        ROOT / config["audit"]["log_file"],
        ROOT / config["audit"]["integrity_file"]
    )
    access = AccessController(config["access"]["roles"])
    consent = ConsentRegistry(ROOT / "data/consent/consent_events.jsonl")

    # Synthetic demo identities. Replace with authenticated application identities.
    reviewer = Principal("demo-reviewer-01", "reviewer")
    auditor = Principal("demo-auditor-01", "auditor")

    # Record consent for synthetic candidate data only.
    consent.record("DEMO-C055", "hiring_evaluation", True, actor_id="demo-candidate-portal")
    consent.require_granted("DEMO-C055", "hiring_evaluation")
    audit.append("CONSENT_VERIFIED", "demo-reviewer-01", "DEMO-C055",
                 {"purpose": "hiring_evaluation", "consent_version": "consent-v1"})

    access.require(reviewer, "score:read")
    score_event = audit.log_score(
        actor_id=reviewer.user_id,
        candidate_id="DEMO-C055",
        score=82.25,
        model_version="day52-final-recommendation-v1",
        evidence_ref="synthetic-demo-evidence"
    )
    decision_event = audit.log_decision(
        actor_id=reviewer.user_id,
        candidate_id="DEMO-C055",
        decision="HOLD_FOR_HUMAN_REVIEW",
        reason_codes=["HUMAN_REVIEW_REQUIRED"],
        human_reviewed=False
    )

    # Encrypted storage demo: synthetic report/transcript only.
    key = load_or_create_key(config["storage"]["key_environment_variable"])
    store = SecureFileStore(ROOT / config["storage"]["directory"], key)
    store.put("DEMO-C055-report", "report", json.dumps({
        "candidate_id": "DEMO-C055",
        "score": 82.25,
        "recommendation": "ADVISORY_ONLY",
        "human_review_required": True,
        "automatic_rejection_enabled": False
    }))
    # Demonstrate a transcript category without saving raw candidate data.
    store.put("DEMO-C055-transcript-note", "transcript_summary",
              "Synthetic demo summary only; raw transcript not stored.")

    verification = audit.verify()
    access.require(auditor, "audit:read")
    report = build_governance_report(config)
    report["audit_verification"] = verification
    report["sample_events"] = {
        "score_event_hash": score_event["event_hash"],
        "decision_event_hash": decision_event["event_hash"]
    }
    report["retention_policy"] = retention_policy(config)

    output = ROOT / "output"
    (output / "governance_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    (output / "governance_report.md").write_text(
        governance_markdown(report), encoding="utf-8"
    )
    (output / "audit_verification.json").write_text(
        json.dumps(verification, indent=2), encoding="utf-8"
    )
    print("DAY 55 — SECURITY & AI GOVERNANCE")
    print(f"Audit chain valid: {verification['valid']}")
    print(f"Events checked: {verification['events_checked']}")
    print("Human review required: True")
    print("Automatic rejection enabled: False")
    print(f"Reports written to: {output}")
    print("Note: Demo uses synthetic data and a process-local key unless you configure a secret externally.")


if __name__ == "__main__":
    main()
