import json
from datetime import datetime, timezone
from pathlib import Path
from .security_errors import ConsentRequired


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConsentRegistry:
    """
    Minimal consent ledger for a local demonstration.
    Store only the minimum required metadata; do not store unnecessary sensitive data.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.records: dict[str, dict] = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    record = json.loads(line)
                    self.records[record["candidate_id"]] = record

    def record(self, candidate_id: str, purpose: str, granted: bool, actor_id: str) -> dict:
        if not candidate_id.strip() or not purpose.strip() or not actor_id.strip():
            raise ValueError("candidate_id, purpose, and actor_id are required.")
        record = {
            "candidate_id": candidate_id,
            "purpose": purpose,
            "granted": bool(granted),
            "recorded_by": actor_id,
            "recorded_at": utc_now(),
            "version": "consent-v1"
        }
        # Append each event; in-memory view tracks the latest state for the candidate.
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        self.records[candidate_id] = record
        return record

    def is_granted(self, candidate_id: str, purpose: str) -> bool:
        record = self.records.get(candidate_id)
        return bool(
            record
            and record.get("granted") is True
            and record.get("purpose") == purpose
        )

    def require_granted(self, candidate_id: str, purpose: str) -> None:
        if not self.is_granted(candidate_id, purpose):
            raise ConsentRequired(
                f"Valid consent is required for candidate '{candidate_id}' "
                f"and purpose '{purpose}'."
            )
