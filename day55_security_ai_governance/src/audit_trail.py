import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from .security_errors import IntegrityError


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class AuditTrail:
    """
    Append-only JSONL event log with hash chaining.
    This detects many edits/deletions but is NOT tamper-proof if an attacker can rewrite
    both the log and head file. Production should export/sign logs to separate protected storage.
    """

    def __init__(self, log_path: str | Path, head_path: str | Path):
        self.log_path = Path(log_path)
        self.head_path = Path(head_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.head_path.parent.mkdir(parents=True, exist_ok=True)

    def _current_head(self) -> str:
        if not self.head_path.exists():
            return "GENESIS"
        try:
            return json.loads(self.head_path.read_text(encoding="utf-8"))["hash"]
        except (json.JSONDecodeError, KeyError) as exc:
            raise IntegrityError("Audit head file is malformed.") from exc

    def append(self, event_type: str, actor_id: str, subject_id: str, details: dict) -> dict:
        if not event_type or not actor_id or not subject_id:
            raise ValueError("event_type, actor_id, and subject_id are required.")
        previous_hash = self._current_head()
        event = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "actor_id": actor_id,
            "subject_id": subject_id,
            "details": details,
            "previous_hash": previous_hash
        }
        event_hash = hashlib.sha256(canonical_json(event).encode("utf-8")).hexdigest()
        stored = {**event, "event_hash": event_hash}
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(stored) + "\n")
        self.head_path.write_text(
            json.dumps({"hash": event_hash}, indent=2), encoding="utf-8"
        )
        return stored

    def log_score(self, actor_id: str, candidate_id: str, score: float,
                  model_version: str, evidence_ref: str = "not-recorded") -> dict:
        return self.append("SCORE_RECORDED", actor_id, candidate_id, {
            "score": score,
            "model_version": model_version,
            "evidence_ref": evidence_ref
        })

    def log_decision(self, actor_id: str, candidate_id: str, decision: str,
                     reason_codes: list[str], human_reviewed: bool) -> dict:
        return self.append("DECISION_RECORDED", actor_id, candidate_id, {
            "decision": decision,
            "reason_codes": reason_codes,
            "human_reviewed": human_reviewed,
            "automatic_rejection_enabled": False
        })

    def verify(self) -> dict:
        previous_hash = "GENESIS"
        count = 0
        if not self.log_path.exists():
            expected_head = self._current_head()
            if expected_head != "GENESIS":
                raise IntegrityError("Audit head exists but log is missing.")
            return {"valid": True, "events_checked": 0, "head_hash": "GENESIS"}

        for line_number, line in enumerate(self.log_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                stored = json.loads(line)
                event = {k: v for k, v in stored.items() if k != "event_hash"}
                actual_hash = hashlib.sha256(canonical_json(event).encode("utf-8")).hexdigest()
            except (json.JSONDecodeError, TypeError) as exc:
                raise IntegrityError(f"Malformed audit event at line {line_number}.") from exc

            if event.get("previous_hash") != previous_hash:
                raise IntegrityError(f"Broken hash chain at line {line_number}.")
            if stored.get("event_hash") != actual_hash:
                raise IntegrityError(f"Event hash mismatch at line {line_number}.")
            previous_hash = actual_hash
            count += 1

        if self._current_head() != previous_hash:
            raise IntegrityError("Audit head does not match the final event.")
        return {"valid": True, "events_checked": count, "head_hash": previous_hash}
