
import unittest

from day49_malpractice_integrity_detection.src.integrity_detector import (
    analyze_integrity,
    load_json
)

BASE = "day49_malpractice_integrity_detection"

CONFIG = load_json(f"{BASE}/config/integrity_rules.json")
SAMPLE = load_json(f"{BASE}/data/sample_interview_events.json")


class TestIntegrityDetection(unittest.TestCase):

    def test_sample_generates_review_flags(self):
        result = analyze_integrity(SAMPLE, CONFIG)
        self.assertEqual(result["risk_score"], 50)
        self.assertEqual(result["risk_level"], "HIGH")
        self.assertEqual(result["status"], "REVIEW_REQUIRED")

    def test_automatic_rejection_is_disabled(self):
        result = analyze_integrity(SAMPLE, CONFIG)
        self.assertFalse(result["automatic_rejection"])

    def test_consent_is_required(self):
        sample = {**SAMPLE, "consent_recorded": False}
        with self.assertRaises(ValueError):
            analyze_integrity(sample, CONFIG)

    def test_negative_event_count_is_rejected(self):
        sample = {
            **SAMPLE,
            "events": {
                **SAMPLE["events"],
                "tab_switch_count": -1
            }
        }
        with self.assertRaises(ValueError):
            analyze_integrity(sample, CONFIG)

    def test_no_threshold_exceeded(self):
        sample = {
            **SAMPLE,
            "events": {
                "tab_switch_count": 0,
                "focus_loss_count": 0,
                "external_voice_events": 0,
                "repeated_looking_away_events": 0
            }
        }
        result = analyze_integrity(sample, CONFIG)
        self.assertEqual(result["risk_score"], 0)
        self.assertEqual(result["status"], "NO_THRESHOLD_EXCEEDED")
        self.assertEqual(len(result["flags"]), 0)

    def test_behavior_context_does_not_change_risk(self):
        result1 = analyze_integrity(SAMPLE, CONFIG)
        sample2 = {
            **SAMPLE,
            "behavioral_context": {
                "source": "day48",
                "signal_consistency_index": 10
            }
        }
        result2 = analyze_integrity(sample2, CONFIG)
        self.assertEqual(result1["risk_score"], result2["risk_score"])
        self.assertFalse(
            result2["behavioral_context"]["used_in_risk_score"]
        )


if __name__ == "__main__":
    unittest.main()
