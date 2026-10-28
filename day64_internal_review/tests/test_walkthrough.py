import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from day64_internal_review.src.walkthrough import run_walkthrough


class Day64WalkthroughTests(unittest.TestCase):
    def test_runs_connected_synthetic_pipeline_with_human_gate(self):
        with TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "walkthrough.json"
            report = run_walkthrough(output_json=output_path)

            self.assertEqual(
                report["stage_order"],
                [
                    "ats",
                    "screening",
                    "hr_interview",
                    "technical_interview",
                    "machine_test",
                    "aggregation",
                    "decision",
                ],
            )
            self.assertEqual(
                report["stages"]["aggregation"]["score_status"],
                "COMPLETE",
            )
            self.assertTrue(output_path.is_file())
            self.assertTrue(output_path.with_suffix(".md").is_file())
            self.assertEqual(report["human_review"]["disposition"], "PENDING")
            self.assertFalse(
                report["human_review"]["automatic_employment_action"]
            )

    def test_rejects_missing_required_screening_answer(self):
        from day64_internal_review.src.walkthrough import CASE_FILE, DATASET
        import json

        dataset = json.loads(DATASET.read_text(encoding="utf-8"))
        case = json.loads(CASE_FILE.read_text(encoding="utf-8"))
        case["screening_answers"] = case["screening_answers"][:-1]

        with TemporaryDirectory() as temporary_directory:
            temporary_directory = Path(temporary_directory)
            dataset_path = temporary_directory / "dataset.json"
            case_path = temporary_directory / "case.json"
            dataset_path.write_text(json.dumps(dataset), encoding="utf-8")
            case_path.write_text(json.dumps(case), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Screening is incomplete"):
                run_walkthrough(
                    dataset_path=dataset_path,
                    case_path=case_path,
                    output_json=None,
                )


if __name__ == "__main__":
    unittest.main()
