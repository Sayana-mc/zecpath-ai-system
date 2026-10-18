from datetime import datetime, timedelta, timezone
from pathlib import Path
import json


def is_expired(iso_timestamp: str, retention_days: int, now=None) -> bool:
    if retention_days < 0:
        raise ValueError("retention_days cannot be negative.")
    timestamp = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    return now >= timestamp + timedelta(days=retention_days)


def apply_file_retention(directory: str | Path, retention_days: int, now=None) -> list[str]:
    """
    Demo file-retention helper. Deletes files based on mtime.
    Do not run against production data until legal holds, backups, and approval rules exist.
    """
    if retention_days < 0:
        raise ValueError("retention_days cannot be negative.")
    root = Path(directory)
    if not root.exists():
        return []
    now = now or datetime.now(timezone.utc)
    deleted = []
    cutoff = now.timestamp() - retention_days * 86400
    for path in root.iterdir():
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink()
            deleted.append(path.name)
    return deleted


def retention_policy(config: dict) -> dict:
    return {
        category: {
            "retention_days": days,
            "action": "delete_or_anonymize_after_expiry",
            "exception": "legal_hold_or_documented_business_requirement"
        }
        for category, days in config["retention_days"].items()
    }
