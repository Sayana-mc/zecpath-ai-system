
"""Unit tests for the Day 52 recommendation engine."""

import copy
import unittest
from pathlib import Path

from day52_final_recommendation_ai.src.decision_engine import (
    DecisionInputError,
    calculate_confidence,
    load_json,
    recommend_candidate,
)


ROOT = Path(__file__).resolve().parents[2]
DAY52 = ROOT / "day52_final_recommendation_ai"

RULES = load_json(DAY52 / "config" / "decision_rules.json")
SAMPLE = load_json(DAY52 / "data" / "candidate_assessment.json")


class TestDay52RecommendationAI(unittest.TestCase):

    def make_assessment(self):
        return copy.deepcopy(SAMPLE)

    def test_high_score_selects_when_complete(self):
        result = recommend_candidate(self.make_assessment(), RULES)
        self.assertEqual(result["decision"], "SELECTED")
        self.assertEqual(result["score"], 82.25)

    def test_medium_score_goes_to_review(self):
        assessment = self.make_assessment()
        assessment["unified_score"] = 70
        result = recommend_candidate(assessment, RULES)
        self.assertEqual(result["decision"], "HOLD_REVIEW")

    def test_low_score_rejected_when_evidence_complete(self):
        assessment = self.make_assessment()
        assessment["unified_score"] = 45
        result = recommend_candidate(assessment, RULES)
        self.assertEqual(result["decision"], "REJECTED")

    def test_integrity_flag_requires_review(self):
        assessment = self.make_assessment()
        assessment["risk_factors"]["integrity"] = {
            "flag": True,
            "evidence": ["Assessment log requires verification."],
            "source": "Assessment audit log"
        }
        result = recommend_candidate(assessment, RULES)
        self.assertEqual(result["decision"], "HOLD_REVIEW")

    def test_behavior_flag_requires_review(self):
        assessment = self.make_assessment()
        assessment["risk_factors"]["behavior"] = {
            "flag": True,
            "evidence": ["Documented job-related assessment concern."],
            "source": "Structured assessment record"
        }
        result = recommend_candidate(assessment, RULES)
        self.assertEqual(result["decision"], "HOLD_REVIEW")

    def test_missing_rounds_require_review(self):
        assessment = self.make_assessment()
        assessment["completed_rounds"] = 4
        assessment["assessment_status"] = "IN_PROGRESS"
        result = recommend_candidate(assessment, RULES)
        self.assertEqual(result["decision"], "HOLD_REVIEW")

    def test_low_confidence_requires_review(self):
        assessment = self.make_assessment()
        assessment["evidence_quality"] = 20
        assessment["data_consistency"] = 20
        result = recommend_candidate(assessment, RULES)
        self.assertEqual(result["decision"], "HOLD_REVIEW")

    def test_confidence_uses_coverage_quality_and_consistency(self):
        assessment = self.make_assessment()
        confidence = calculate_confidence(assessment)
        self.assertEqual(confidence, 97.0)

    def test_confidence_is_not_probability(self):
        result = recommend_candidate(self.make_assessment(), RULES)
        self.assertIn(
            "not a probability",
            result["confidence_interpretation"]
        )

    def test_flag_requires_evidence(self):
        assessment = self.make_assessment()
        assessment["risk_factors"]["integrity"] = {
            "flag": True,
            "evidence": [],
            "source": "Assessment audit log"
        }
        with self.assertRaises(DecisionInputError):
            recommend_candidate(assessment, RULES)

    def test_score_outside_range_is_rejected_as_invalid_input(self):
        assessment = self.make_assessment()
        assessment["unified_score"] = 120
        with self.assertRaises(DecisionInputError):
            recommend_candidate(assessment, RULES)

    def test_completed_rounds_cannot_exceed_expected(self):
        assessment = self.make_assessment()
        assessment["completed_rounds"] = 6
        with self.assertRaises(DecisionInputError):
            recommend_candidate(assessment, RULES)

    def test_output_explains_decision(self):
        result = recommend_candidate(self.make_assessment(), RULES)
        self.assertTrue(result["explanation"]["reasons"])
        self.assertTrue(result["audit"]["recommendation_only"])
        self.assertTrue(result["explanation"]["human_review_required"])

    def test_risk_flag_does_not_automatically_reject(self):
        assessment = self.make_assessment()
        assessment["unified_score"] = 45
        assessment["risk_factors"]["integrity"] = {
            "flag": True,
            "evidence": ["Needs human verification."],
            "source": "Assessment audit log"
        }
        result = recommend_candidate(assessment, RULES)
        self.assertEqual(result["decision"], "HOLD_REVIEW")


if __name__ == "__main__":
    unittest.main(verbosity=2)
