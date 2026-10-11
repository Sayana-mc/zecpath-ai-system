
import unittest

from day48_behavioral_ai_research_design.src.signal_analyzer import (
    analyze_signals,
    load_json
)

BASE = "day48_behavioral_ai_research_design"

CONFIG = load_json(f"{BASE}/config/signal_mapping.json")
SAMPLE = load_json(f"{BASE}/data/sample_behavior_signals.json")


class TestBehavioralAI(unittest.TestCase):

    def test_valid_sample(self):
        result = analyze_signals(SAMPLE, CONFIG)
        self.assertEqual(result["signal_consistency_index"], 75.75)

    def test_human_review_required(self):
        result = analyze_signals(SAMPLE, CONFIG)
        self.assertTrue(result["human_review_required"])

    def test_consent_required(self):
        sample = dict(SAMPLE)
        sample["consent_recorded"] = False

        with self.assertRaises(ValueError):
            analyze_signals(sample, CONFIG)

    def test_metric_out_of_range(self):
        sample = {
            **SAMPLE,
            "metrics": {**SAMPLE["metrics"], "gaze_stability": 1.5}
        }

        with self.assertRaises(ValueError):
            analyze_signals(sample, CONFIG)

    def test_weights_must_sum_to_one(self):
        config = {
            **CONFIG,
            "weights": {**CONFIG["weights"], "gaze_stability": 0.5}
        }

        with self.assertRaises(ValueError):
            analyze_signals(SAMPLE, config)

    def test_negative_event_count(self):
        sample = {
            **SAMPLE,
            "event_counts": {
                **SAMPLE["event_counts"],
                "gesture_events": -1
            }
        }

        with self.assertRaises(ValueError):
            analyze_signals(sample, CONFIG)


if __name__ == "__main__":
    unittest.main()
