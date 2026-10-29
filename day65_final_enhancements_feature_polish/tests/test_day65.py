import json
import unittest
from pathlib import Path

from src.main import (
    DATA, CONFIG, OUTPUT, DataValidationError, find_skills,
    load_json, run, score_candidate, validate_inputs
)


class Day65Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = load_json(DATA / "jobs.json")
        cls.candidates = load_json(DATA / "candidates.json")
        cls.config = load_json(CONFIG)

    def test_input_data_counts(self):
        self.assertEqual(len(self.jobs), 2)
        self.assertEqual(len(self.candidates), 6)

    def test_skill_matching_uses_word_boundaries(self):
        self.assertEqual(find_skills("Python and SQL; not pythonic", ["Python", "SQL"]), ["Python", "SQL"])

    def test_weights_are_consistent(self):
        validate_inputs(self.jobs, self.candidates, self.config)
        broken = dict(self.config)
        broken["preferred_skill_weight"] = 0.4
        with self.assertRaises(DataValidationError):
            validate_inputs(self.jobs, self.candidates, broken)

    def test_unknown_job_is_rejected(self):
        candidates = [dict(self.candidates[0], job_id="UNKNOWN")]
        with self.assertRaises(DataValidationError):
            validate_inputs(self.jobs, candidates, self.config)

    def test_human_review_is_always_required(self):
        results = run()
        self.assertEqual(len(results), 6)
        self.assertTrue(all(r["human_review_required"] for r in results))
        self.assertTrue(all(not r["automated_rejection"] for r in results))

    def test_reports_exist_and_are_readable(self):
        run()
        summary = json.loads((OUTPUT / "recruiter_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["candidate_count"], 6)
        self.assertEqual(summary["job_count"], 2)
        self.assertTrue((OUTPUT / "recruiter_summary.csv").exists())
        self.assertTrue((OUTPUT / "run_report.txt").exists())


if __name__ == "__main__":
    unittest.main()
