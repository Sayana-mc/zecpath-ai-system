import json, unittest
from pathlib import Path
from day56_full_system_simulation.src.pipeline import run_candidate, summarize, valid_score
from day56_full_system_simulation.src.reporting import create_report, to_markdown

class Day56Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.config=json.loads((cls.root/"config"/"pipeline_config.json").read_text(encoding="utf-8"))
        cls.candidates=json.loads((cls.root/"data"/"candidates.json").read_text(encoding="utf-8"))
    def test_seven_pipeline_stages_complete(self):
        r=run_candidate(self.candidates[0],self.config,self.root/"data")
        self.assertEqual(len(r["stages"]),7)
        self.assertTrue(all(x["status"]=="COMPLETED" for x in r["stages"].values()))
    def test_score_in_range(self):
        self.assertEqual(valid_score(75),75.0)
        with self.assertRaises(ValueError): valid_score(101)
    def test_human_review_mandatory(self):
        r=run_candidate(self.candidates[0],self.config,self.root/"data")
        self.assertTrue(r["stages"]["final_decision"]["human_review_required"])
    def test_automatic_rejection_disabled(self):
        r=run_candidate(self.candidates[0],self.config,self.root/"data")
        self.assertFalse(r["stages"]["final_decision"]["automatic_rejection_enabled"])
    def test_ats_finds_missing_skills(self):
        r=run_candidate(self.candidates[1],self.config,self.root/"data")
        self.assertIn("machine learning",r["stages"]["ats_scoring"]["missing_skills"])
    def test_comparison_has_score_gap(self):
        r=run_candidate(self.candidates[0],self.config,self.root/"data")
        self.assertGreaterEqual(r["human_comparison"]["score_gap"],0)
    def test_summary_counts_all_stages(self):
        results=[run_candidate(c,self.config,self.root/"data") for c in self.candidates]
        s=summarize(results)
        self.assertEqual(s["total_stage_executions"],len(self.candidates)*7)
        self.assertEqual(s["stage_completion_rate_percent"],100)
    def test_markdown_report(self):
        results=[run_candidate(c,self.config,self.root/"data") for c in self.candidates]
        s=summarize(results); md=to_markdown(create_report(self.config,results,s))
        self.assertIn("End-to-End AI Test Report",md)
        self.assertIn("Improvement recommendations",md)
    def test_weight_sum_validation(self):
        bad=dict(self.config); bad["stage_weights"]=dict(self.config["stage_weights"]); bad["stage_weights"]["ats"]=0.01
        with self.assertRaises(RuntimeError): run_candidate(self.candidates[0],bad,self.root/"data")

if __name__=="__main__": unittest.main()
