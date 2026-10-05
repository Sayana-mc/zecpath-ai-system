from datetime import datetime, timedelta
from typing import Dict


class RetentionManager:

    def __init__(self, config: Dict):
        self.config = config["retention"]

    def calculate_expiry(self, created_at: str) -> Dict:

        created = datetime.fromisoformat(created_at)

        retention_days = self.config["default_retention_days"]

        expiry = created + timedelta(days=retention_days)

        return {
            "created_at": created.isoformat(),
            "retention_days": retention_days,
            "expiry_date": expiry.isoformat(),
            "deletion_after_expiry": self.config["delete_after_expiry"],
            "candidate_deletion_request_supported":
                self.config["candidate_deletion_request_supported"]
        }