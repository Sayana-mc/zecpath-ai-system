import json
import tempfile
import unittest
from pathlib import Path

from day58_advanced_feature_proposal.src.coaching import build_coaching_plan
from day58_advanced_feature_proposal.src.feature_registry import get_feature, list_features
from day58_advanced_feature_proposal.src.reporting import atomic_write_json, build_proposal_report
from day58_advanced_feature_proposal.src.roadmap import validate_roadmap

ROOT = Path(__file__).resolve().parents[1]


class Day58Tests(unittest.TestCase):
    def setUp(self):
        self.roadmap = json.loads((ROOT / "config" / "roadmap_config.json").read_text(encoding="utf-8"))
        self.candidate = json.loads((ROOT / "data" / "sample_candidate.json").read_text(encoding="utf-8"))

    def test_roadmap_validates(self):
        self.assertEqual(len(validate_roadmap(self.roadmap)["phases"]), 5)

    def test_human_review_required(self):
        bad = json.loads(json.dumps(self.roadmap))
        bad["principles"]["human_review_required"] = False
        with self.assertRaises(ValueError):
            validate_roadmap(bad)

    def test_automatic_rejection_must_be_disabled(self):
        bad = json.loads(json.dumps(self.roadmap))
        bad["principles"]["automatic_rejection_enabled"] = True
        with self.assertRaises(ValueError):
            validate_roadmap(bad)

    def test_emotion_inference_must_be_disabled(self):
        bad = json.loads(json.dumps(self.roadmap))
        bad["principles"]["emotion_inference_for_hiring_enabled"] = True
        with self.assertRaises(ValueError):
            validate_roadmap(bad)

    def test_duplicate_phase_ids_rejected(self):
        bad = json.loads(json.dumps(self.roadmap))
        bad["phases"][1]["id"] = bad["phases"][0]["id"]
        with self.assertRaises(ValueError):
            validate_roadmap(bad)

    def test_coaching_identifies_missing_skills(self):
        plan = build_coaching_plan(self.candidate)
        self.assertEqual([x["skill"] for x in plan["skills_to_practice"]], ["sql", "data visualization"])

    def test_coaching_does_not_make_hiring_decision(self):
        plan = build_coaching_plan(self.candidate)
        self.assertIsNone(plan["hiring_decision"])
        self.assertTrue(plan["human_review_required_for_hiring"])

    def test_empty_skill_gap_is_valid(self):
        candidate = dict(self.candidate, skills_demonstrated=list(self.candidate["required_skills"]))
        plan = build_coaching_plan(candidate)
        self.assertEqual(plan["skills_to_practice"], [])

    def test_candidate_id_required(self):
        candidate = dict(self.candidate)
        candidate.pop("candidate_id")
        with self.assertRaises(ValueError):
            build_coaching_plan(candidate)

    def test_unknown_skill_rejected(self):
        candidate = dict(self.candidate, skills_demonstrated=["mind reading"])
        with self.assertRaises(ValueError):
            build_coaching_plan(candidate)

    def test_invalid_skill_list_rejected(self):
        candidate = dict(self.candidate, required_skills="sql")
        with self.assertRaises(ValueError):
            build_coaching_plan(candidate)

    def test_feature_registry_has_six_features(self):
        self.assertEqual(len(list_features()), 6)

    def test_unknown_feature_raises(self):
        with self.assertRaises(KeyError):
            get_feature("F99")

    def test_report_contains_guardrails(self):
        report = build_proposal_report(self.roadmap, list_features(), build_coaching_plan(self.candidate))
        self.assertFalse(report["principles"]["automatic_rejection_enabled"])
        self.assertFalse(report["principles"]["emotion_inference_for_hiring_enabled"])
        self.assertEqual(report["feature_count"], 6)

    def test_atomic_json_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "report.json"
            atomic_write_json(path, {"ok": True})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"ok": True})

    def test_atomic_json_replaces_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            atomic_write_json(path, {"version": 1})
            atomic_write_json(path, {"version": 2})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["version"], 2)


if __name__ == "__main__":
    unittest.main()
