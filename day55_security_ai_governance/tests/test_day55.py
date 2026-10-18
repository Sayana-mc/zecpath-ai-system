import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet

from day55_security_ai_governance.src.access_control import AccessController, Principal
from day55_security_ai_governance.src.audit_trail import AuditTrail
from day55_security_ai_governance.src.consent import ConsentRegistry
from day55_security_ai_governance.src.retention import is_expired
from day55_security_ai_governance.src.secure_storage import SecureFileStore
from day55_security_ai_governance.src.security_errors import AccessDenied, ConsentRequired, IntegrityError, StorageKeyError


class Day55Tests(unittest.TestCase):
    def test_rbac_allows_permitted_role(self):
        acl = AccessController({"reviewer": ["score:read"]})
        self.assertTrue(acl.is_allowed(Principal("u1", "reviewer"), "score:read"))

    def test_rbac_denies_unpermitted_role(self):
        acl = AccessController({"candidate": ["consent:read"]})
        with self.assertRaises(AccessDenied):
            acl.require(Principal("u2", "candidate"), "score:read")

    def test_consent_required_until_granted(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = ConsentRegistry(Path(tmp) / "consent.jsonl")
            with self.assertRaises(ConsentRequired):
                registry.require_granted("C1", "hiring_evaluation")
            registry.record("C1", "hiring_evaluation", True, "candidate-portal")
            registry.require_granted("C1", "hiring_evaluation")

    def test_revoked_consent_is_not_granted(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = ConsentRegistry(Path(tmp) / "consent.jsonl")
            registry.record("C1", "hiring_evaluation", True, "candidate-portal")
            registry.record("C1", "hiring_evaluation", False, "candidate-portal")
            self.assertFalse(registry.is_granted("C1", "hiring_evaluation"))

    def test_audit_chain_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = AuditTrail(Path(tmp) / "events.jsonl", Path(tmp) / "head.json")
            audit.log_score("reviewer", "C1", 80, "model-v1")
            audit.log_decision("reviewer", "C1", "HOLD_FOR_HUMAN_REVIEW", ["human-review"], False)
            result = audit.verify()
            self.assertTrue(result["valid"])
            self.assertEqual(result["events_checked"], 2)

    def test_audit_tampering_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "events.jsonl"
            audit = AuditTrail(log, Path(tmp) / "head.json")
            audit.log_score("reviewer", "C1", 80, "model-v1")
            event = json.loads(log.read_text(encoding="utf-8"))
            event["details"]["score"] = 99
            log.write_text(json.dumps(event) + "\n", encoding="utf-8")
            with self.assertRaises(IntegrityError):
                audit.verify()

    def test_secure_storage_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = SecureFileStore(tmp, Fernet.generate_key())
            store.put("C1-report", "report", "synthetic secret")
            self.assertEqual(store.get("C1-report"), "synthetic secret")
            encrypted = (Path(tmp) / "C1-report.enc").read_text(encoding="ascii")
            self.assertNotIn("synthetic secret", encrypted)

    def test_wrong_key_fails_to_decrypt(self):
        with tempfile.TemporaryDirectory() as tmp:
            store1 = SecureFileStore(tmp, Fernet.generate_key())
            store1.put("C1-report", "report", "secret")
            store2 = SecureFileStore(tmp, Fernet.generate_key())
            with self.assertRaises(StorageKeyError):
                store2.get("C1-report")

    def test_retention_expiry(self):
        old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        self.assertTrue(is_expired(old, 7))

    def test_retention_not_expired(self):
        recent = datetime.now(timezone.utc).isoformat()
        self.assertFalse(is_expired(recent, 7))


if __name__ == "__main__":
    unittest.main()
