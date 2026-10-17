
import json
import unittest
from pathlib import Path

from day54_optimization_refinement.src.accuracy_analyzer import (
    analyze_thresholds
)
from day54_optimization_refinement.src.intent_detector import (
    detect_intent
)
from day54_optimization_refinement.src.refined_scoring import (
    calculate_round_score,
    evaluate_candidate,
)


ROOT = Path(__file__).resolve().parents[1]


class Day54OptimizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "config" / "optimization_config.json").open(
            encoding="utf-8"
        ) as file:
            cls.config = json.load(file)

        with (ROOT / "data" / "labelled_evaluations.json").open(
            encoding="utf-8"
        ) as file:
            cls.examples = json.load(file)["examples"]

    def test_round_score_average(self):
        self.assertEqual(
            calculate_round_score([80, 90, 70]), 80.0
        )

    def test_missing_scores_return_none(self):
        self.assertIsNone(calculate_round_score([]))

    def test_invalid_score_rejected(self):
        with self.assertRaises(ValueError):
            calculate_round_score([80, 120])

    def test_boolean_score_rejected(self):
        with self.assertRaises(ValueError):
            calculate_round_score([True])

    def test_large_score_gap_requires_review(self):
        result = evaluate_candidate(
            score=82,
            round_scores=[40, 90, 75],
            completed_rounds=3,
            thresholds=self.config["thresholds"],
            consistency_config=self.config["consistency"],
            review_config=self.config["review"],
            intent="explain_role_fit"
        )
        self.assertEqual(
            result["status"], "HOLD_FOR_HUMAN_REVIEW"
        )
        self.assertIn(
            "LARGE_ROUND_SCORE_GAP", result["review_reasons"]
        )

    def test_incomplete_round_count_requires_review(self):
        result = evaluate_candidate(
            score=90,
            round_scores=[90, 91],
            completed_rounds=2,
            thresholds=self.config["thresholds"],
            consistency_config=self.config["consistency"],
            review_config=self.config["review"],
            intent="explain_role_fit"
        )
        self.assertEqual(
            result["status"], "HOLD_FOR_HUMAN_REVIEW"
        )

    def test_unknown_intent_requires_review(self):
        result = evaluate_candidate(
            score=90,
            round_scores=[90, 90, 90],
            completed_rounds=3,
            thresholds=self.config["thresholds"],
            consistency_config=self.config["consistency"],
            review_config=self.config["review"],
            intent="unknown"
        )
        self.assertIn("UNKNOWN_INTENT", result["review_reasons"])

    def test_intent_detected(self):
        result = detect_intent("Explain this candidate's role fit")
        self.assertEqual(result["intent"], "explain_role_fit")

    def test_ambiguous_intent_requests_clarification(self):
        result = detect_intent(
            "Explain this candidate's score and summarize the report"
        )
        self.assertEqual(result["status"], "NEEDS_CLARIFICATION")
        self.assertEqual(result["intent"], "ambiguous")

    def test_unknown_intent_requests_clarification(self):
        result = detect_intent("Open the blue dashboard")
        self.assertEqual(result["intent"], "unknown")
        self.assertEqual(result["status"], "NEEDS_CLARIFICATION")

    def test_threshold_analysis_returns_comparisons(self):
        result = analyze_thresholds(
            self.examples, self.config["tuning"]
        )
        self.assertGreater(len(result["threshold_comparisons"]), 0)
        self.assertIn("false_positive", result["configured_threshold_baseline"])
        self.assertFalse(result["threshold_change_approved"])

    def test_threshold_analysis_rejects_invalid_label(self):
        invalid = [dict(self.examples[0])]
        invalid[0]["ground_truth_suitable"] = "yes"

        with self.assertRaises(ValueError):
            analyze_thresholds(invalid, self.config["tuning"])

    def test_human_review_cannot_be_disabled(self):
        result = evaluate_candidate(
            score=95,
            round_scores=[95, 95, 95],
            completed_rounds=3,
            thresholds=self.config["thresholds"],
            consistency_config=self.config["consistency"],
            review_config=self.config["review"],
            intent="explain_role_fit"
        )
        self.assertTrue(result["human_review_required"])
        self.assertFalse(result["automatic_rejection_enabled"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
