import json
import math
import tempfile
import unittest
from pathlib import Path
from day57_debugging_stabilization.src.validation import validate_config, validate_candidates, validate_score, ValidationError
from day57_debugging_stabilization.src.pipeline import read_resume, keyword_matches, score_to_advisory, summarize
from day57_debugging_stabilization.src.reporting import create_report, to_markdown, validate_report_shape, write_json_atomic

ROOT = Path(__file__).resolve().parents[1]

def good_config():
    return json.loads((ROOT / "config" / "stabilization_config.json").read_text(encoding="utf-8"))

def good_candidate():
    return {"candidate_id":"T-1","name":"Test Candidate","resume_file":"test.txt","screening_score":80,
        "hr_interview_score":75,"technical_interview_score":90,"machine_test_score":85,"human_judgment":"SELECTED","human_score":82}

class TestValidation(unittest.TestCase):
    def test_valid_config(self): self.assertEqual(validate_config(good_config())["version"], "day57-v1")
    def test_weight_sum_rejected(self):
        c=good_config(); c["stage_weights"]["ats"]=.9
        with self.assertRaises(ValidationError): validate_config(c)
    def test_auto_rejection_must_be_false(self):
        c=good_config(); c["governance"]["automatic_rejection_enabled"]=True
        with self.assertRaises(ValidationError): validate_config(c)
    def test_bool_score_rejected(self):
        with self.assertRaises(ValidationError): validate_score(True)
    def test_nan_rejected(self):
        with self.assertRaises(ValidationError): validate_score(float("nan"))
    def test_out_of_range_score_rejected(self):
        with self.assertRaises(ValidationError): validate_score(101)
    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValidationError): validate_candidates([good_candidate(),good_candidate()])
    def test_path_traversal_rejected(self):
        c=good_candidate(); c["resume_file"]="../secret.txt"
        with self.assertRaises(ValidationError): validate_candidates([c])
    def test_unknown_human_label_rejected(self):
        c=good_candidate(); c["human_judgment"]="AUTO_REJECT"
        with self.assertRaises(ValidationError): validate_candidates([c])

class TestPipelineEdgeCases(unittest.TestCase):
    def test_empty_resume_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"empty.txt"; p.write_text("  ",encoding="utf-8")
            with self.assertRaises(ValueError): read_resume(p)
    def test_missing_resume_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError): read_resume(Path(d)/"missing.txt")
    def test_resume_size_limit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"long.txt"; p.write_text("x"*20,encoding="utf-8")
            with self.assertRaises(ValueError): read_resume(p,max_characters=10)
    def test_whole_token_matching(self):
        matched,missing=keyword_matches("I use NoSQL only",["sql","nosql"])
        self.assertEqual(matched,["nosql"])
        self.assertEqual(missing,["sql"])
    def test_threshold_boundaries(self):
        t=good_config()["thresholds"]
        self.assertEqual(score_to_advisory(80,t),"STRONG_FIT_REVIEW_REQUIRED")
        self.assertEqual(score_to_advisory(60,t),"POTENTIAL_FIT_REVIEW_REQUIRED")
        self.assertEqual(score_to_advisory(59.99,t),"ADDITIONAL_REVIEW_REQUIRED")
    def test_summary_empty(self):
        s=summarize([]); self.assertEqual(s["candidate_count"],0); self.assertEqual(s["stage_completion_rate_percent"],0)
    def test_report_shape_and_atomic_json(self):
        report={"report_schema_version":"1.0","project_name":"test","module_version":"v1","generated_at_utc":"now","test_mode":"test","candidate_results":[],"performance_analysis":{},"recommendations":[],"limitations":[]}
        validate_report_shape(report)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"report.json"; write_json_atomic(p,report)
            self.assertEqual(json.loads(p.read_text(encoding="utf-8"))["project_name"],"test")
            self.assertFalse(p.with_suffix(".json.tmp").exists())

if __name__ == "__main__": unittest.main(verbosity=2)
