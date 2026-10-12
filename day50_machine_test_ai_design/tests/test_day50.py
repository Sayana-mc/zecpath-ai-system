
import json
import tempfile
import unittest
from pathlib import Path

from day50_machine_test_ai_design.src.evaluator import (
    calculate_correctness,
    calculate_time_management,
    evaluate_submission,
    load_json,
    validate_config,
)


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "scoring_rules.json"
DATA_PATH = BASE_DIR / "data" / "sample_submission.json"


class Day50EvaluationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = load_json(CONFIG_PATH)
        cls.sample = load_json(DATA_PATH)

    def test_scoring_weights_total_100(self):
        self.assertEqual(sum(self.config["weights"].values()), 100)
        validate_config(self.config)

    def test_correctness_uses_supplied_test_results(self):
        score, passed, total = calculate_correctness([
            {"test_id": "T1", "passed": True},
            {"test_id": "T2", "passed": False},
            {"test_id": "T3", "passed": True},
            {"test_id": "T4", "passed": True},
        ])
        self.assertEqual(score, 75.0)
        self.assertEqual(passed, 3)
        self.assertEqual(total, 4)

    def test_empty_results_return_zero_correctness(self):
        self.assertEqual(calculate_correctness([]), (0.0, 0, 0))

    def test_time_score_full_credit_under_threshold(self):
        result = calculate_time_management(
            {"allotted_seconds": 1000, "elapsed_seconds": 600},
            self.config,
        )
        self.assertEqual(result["time_management_score"], 100.0)

    def test_time_score_zero_after_deadline(self):
        result = calculate_time_management(
            {"allotted_seconds": 1000, "elapsed_seconds": 1100},
            self.config,
        )
        self.assertEqual(result["time_management_score"], 0.0)
        self.assertFalse(result["submitted_within_deadline"])

    def test_sample_report_has_required_safeguards(self):
        report = evaluate_submission(self.sample, self.config)
        self.assertEqual(report["final_score"], 80.25)
        self.assertEqual(report["test_results"]["passed"], 3)
        self.assertEqual(report["test_results"]["total"], 4)
        self.assertTrue(report["decision"]["human_review_required"])
        self.assertFalse(report["decision"]["automatic_rejection"])

    def test_unsupported_task_type_is_rejected(self):
        bad = json.loads(json.dumps(self.sample))
        bad["task"]["task_type"] = "unknown"
        with self.assertRaises(ValueError):
            evaluate_submission(bad, self.config)

    def test_invalid_metric_is_rejected(self):
        bad = json.loads(json.dumps(self.sample))
        bad["submission"]["metrics"]["efficiency"] = 120
        with self.assertRaises(ValueError):
            evaluate_submission(bad, self.config)

    def test_negative_elapsed_time_is_rejected(self):
        bad = json.loads(json.dumps(self.sample))
        bad["time"]["elapsed_seconds"] = -1
        with self.assertRaises(ValueError):
            evaluate_submission(bad, self.config)

    def test_duplicate_test_ids_are_rejected(self):
        bad = json.loads(json.dumps(self.sample))
        bad["submission"]["execution_results"].append(
            {"test_id": "T1", "passed": True}
        )
        with self.assertRaises(ValueError):
            evaluate_submission(bad, self.config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
