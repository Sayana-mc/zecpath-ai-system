
import copy
import unittest
from pathlib import Path

from day51_cross_round_aggregation_engine.src.aggregation_engine import (
    aggregate_candidate,
    load_json,
    normalize_score,
    validate_config,
)


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG = load_json(BASE_DIR / "config" / "role_weights.json")
SAMPLE = load_json(BASE_DIR / "data" / "candidate_evaluations.json")


class Day51AggregationTests(unittest.TestCase):

    def test_role_weights_total_100(self):
        for weights in CONFIG["roles"].values():
            self.assertEqual(sum(weights.values()), 100)
        validate_config(CONFIG)

    def test_raw_score_normalization(self):
        self.assertEqual(normalize_score(42, 50), 84.0)

    def test_full_candidate_score(self):
        report = aggregate_candidate(copy.deepcopy(SAMPLE), CONFIG)
        self.assertEqual(report["hiring_fit_score_percent"], 82.25)
        self.assertEqual(report["score_status"], "COMPLETE")
        self.assertEqual(report["fit_band"], "STRONG_FIT")

    def test_all_five_rounds_are_present(self):
        report = aggregate_candidate(copy.deepcopy(SAMPLE), CONFIG)
        self.assertEqual(len(report["round_scores"]), 5)
        self.assertEqual(report["missing_rounds"], [])

    def test_partial_candidate_is_renormalized(self):
        candidate = copy.deepcopy(SAMPLE)
        del candidate["evaluations"]["machine_test"]

        report = aggregate_candidate(candidate, CONFIG)

        self.assertEqual(report["score_status"], "PARTIAL")
        self.assertEqual(report["missing_rounds"], ["machine_test"])
        self.assertAlmostEqual(
            report["hiring_fit_score_percent"], 83.461538, places=4
        )
        self.assertAlmostEqual(
            sum(report["effective_weights_percent"].values()), 100.0
        )

    def test_pending_round_is_not_treated_as_zero(self):
        candidate = copy.deepcopy(SAMPLE)
        candidate["evaluations"]["machine_test"] = {
            "status": "pending"
        }

        report = aggregate_candidate(candidate, CONFIG)

        self.assertIsNone(
            report["round_scores"]["machine_test"]["normalized_score"]
        )
        self.assertIn("machine_test", report["missing_rounds"])
        self.assertEqual(report["score_status"], "PARTIAL")

    def test_not_applicable_round_is_excluded(self):
        candidate = copy.deepcopy(SAMPLE)
        candidate["evaluations"]["machine_test"] = {
            "status": "not_applicable"
        }

        report = aggregate_candidate(candidate, CONFIG)

        self.assertIn("machine_test", report["not_applicable_rounds"])
        self.assertEqual(report["score_status"], "PARTIAL")

    def test_no_completed_rounds_has_no_fit_score(self):
        candidate = copy.deepcopy(SAMPLE)
        candidate["evaluations"] = {
            "ats": {"status": "pending"},
            "screening": {"status": "pending"},
            "hr_interview": {"status": "pending"},
            "technical_interview": {"status": "pending"},
            "machine_test": {"status": "pending"}
        }

        report = aggregate_candidate(candidate, CONFIG)

        self.assertIsNone(report["hiring_fit_score_percent"])
        self.assertEqual(report["fit_band"], "NOT_EVALUATED")
        self.assertEqual(report["score_status"], "NOT_EVALUATED")

    def test_unknown_role_is_rejected(self):
        candidate = copy.deepcopy(SAMPLE)
        candidate["role"] = "unknown_role"

        with self.assertRaises(ValueError):
            aggregate_candidate(candidate, CONFIG)

    def test_out_of_range_score_is_rejected(self):
        candidate = copy.deepcopy(SAMPLE)
        candidate["evaluations"]["ats"]["score"] = 110

        with self.assertRaises(ValueError):
            aggregate_candidate(candidate, CONFIG)

    def test_automatic_rejection_must_be_disabled(self):
        config = copy.deepcopy(CONFIG)
        config["safeguards"]["automatic_rejection"] = True

        with self.assertRaises(ValueError):
            aggregate_candidate(copy.deepcopy(SAMPLE), config)

    def test_bad_weights_are_rejected(self):
        config = copy.deepcopy(CONFIG)
        config["roles"]["data_scientist"]["ats"] = 50

        with self.assertRaises(ValueError):
            aggregate_candidate(copy.deepcopy(SAMPLE), config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
