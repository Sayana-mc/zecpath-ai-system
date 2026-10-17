
"""Unit tests for Day 53 Hiring Intelligence Report Generator."""

import copy
import tempfile
import unittest
from pathlib import Path

from day53_hiring_intelligence_report.src.report_generator import (
    ReportInputError,
    build_hiring_report,
    load_json,
    render_markdown,
    save_report,
)


ROOT = Path(__file__).resolve().parents[2]
DAY53 = ROOT / "day53_hiring_intelligence_report"

CONFIG = load_json(DAY53 / "config" / "report_config.json")
SAMPLE = load_json(DAY53 / "data" / "candidate_profile.json")


class TestHiringIntelligenceReport(unittest.TestCase):

    def setUp(self):
        self.assessment = copy.deepcopy(SAMPLE)

    def test_builds_candidate_profile(self):
        report = build_hiring_report(self.assessment, CONFIG)
        profile = report["candidate_profile"]

        self.assertEqual(profile["candidate_id"], "DEMO-C001")
        self.assertEqual(profile["target_role"], "Data Scientist")

    def test_includes_all_evaluation_areas(self):
        report = build_hiring_report(self.assessment, CONFIG)
        rounds = report["evaluation_summary"]["rounds"]

        for key in (
            "ats",
            "screening",
            "hr_interview",
            "technical_interview",
            "machine_test",
        ):
            self.assertIn(key, rounds)

    def test_includes_strengths_and_weaknesses(self):
        report = build_hiring_report(self.assessment, CONFIG)

        self.assertTrue(report["candidate_insights"]["strengths"])
        self.assertTrue(report["candidate_insights"]["weaknesses"])

    def test_preserves_day52_recommendation(self):
        report = build_hiring_report(self.assessment, CONFIG)

        self.assertEqual(
            report["final_recommendation"]["decision"],
            "SELECTED",
        )
        self.assertEqual(
            report["final_recommendation"]["score"],
            82.25,
        )

    def test_incomplete_round_requires_review(self):
        self.assessment["evaluation_rounds"]["machine_test"]["status"] = (
            "PENDING"
        )

        report = build_hiring_report(self.assessment, CONFIG)

        self.assertEqual(
            report["final_recommendation"]["decision"],
            "HOLD_REVIEW",
        )
        self.assertTrue(report["risk_indicators"])

    def test_behavior_flag_requires_review(self):
        self.assessment["behavioral_assessment"]["flags"] = [
            "A documented job-related assessment concern requires review."
        ]

        report = build_hiring_report(self.assessment, CONFIG)

        self.assertEqual(
            report["final_recommendation"]["decision"],
            "HOLD_REVIEW",
        )

    def test_invalid_round_score_is_rejected(self):
        self.assessment["evaluation_rounds"]["ats"]["score"] = 150

        with self.assertRaises(ReportInputError):
            build_hiring_report(self.assessment, CONFIG)

    def test_markdown_contains_required_sections(self):
        report = build_hiring_report(self.assessment, CONFIG)
        markdown = render_markdown(report)

        self.assertIn("Candidate Profile", markdown)
        self.assertIn("Evaluation Results", markdown)
        self.assertIn("Strengths", markdown)
        self.assertIn("Weaknesses and Development Areas", markdown)
        self.assertIn("Risk Indicators", markdown)
        self.assertIn("Final Recommendation", markdown)

    def test_saves_json_and_markdown(self):
        report = build_hiring_report(self.assessment, CONFIG)

        with tempfile.TemporaryDirectory() as temporary_dir:
            json_path, markdown_path = save_report(
                report, temporary_dir
            )

            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertGreater(json_path.stat().st_size, 0)
            self.assertGreater(markdown_path.stat().st_size, 0)

    def test_report_is_advisory(self):
        report = build_hiring_report(self.assessment, CONFIG)

        self.assertTrue(
            report["final_recommendation"]["recommendation_only"]
        )
        self.assertTrue(
            report["final_recommendation"]["human_review_required"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
