import json, tempfile, unittest
from pathlib import Path
from day61_ai_monitoring_observability.src.observability import Observability, dashboard, alerts, read_jsonl

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.o=Observability(self.root)
    def tearDown(self): self.temp.cleanup()
    def test_api_jsonl(self):
        e=self.o.api("/health","GET",200,10,"trace-1")
        self.assertTrue(e["success"])
        self.assertEqual(read_jsonl(self.root/"api_logs.jsonl")[0]["correlation_id"],"trace-1")
    def test_model_and_error_logs(self):
        self.o.model("parser","v1","resume_parsing",20,True,"ref")
        self.o.error("parser","ValueError","safe message")
        self.assertTrue((self.root/"model_logs.jsonl").exists())
        self.assertTrue((self.root/"error_logs.jsonl").exists())
    def test_audit_status_validation(self):
        self.o.decision("ref","REVIEW_REQUIRED","check evidence","system","v1",False)
        with self.assertRaises(ValueError):
            self.o.decision("ref","AUTO_REJECT","reason","system","v1",False)
    def test_dashboard(self):
        s=dashboard([{"duration_ms":100,"success":True},{"duration_ms":400,"success":False}],
                    [{"task":"interview_analysis","success":True},{"task":"interview_analysis","success":False}],
                    [{"decision":"REVIEW_REQUIRED","human_reviewed":False}])
        self.assertEqual(s["candidate_processing"]["failure_rate_percent"],50.0)
        self.assertEqual(s["interview_metrics"]["analysis_success_rate_percent"],50.0)
    def test_alerts(self):
        s={"candidate_processing":{"api_requests":20,"failure_rate_percent":12,"p95_response_ms":4000}}
        c={"minimum_events_for_failure_alert":10,"failure_rate_warning_percent":5,
           "failure_rate_critical_percent":10,"latency_warning_ms":1000,"latency_critical_ms":3000}
        a=alerts(s,c)
        self.assertEqual(len(a),2)
        self.assertTrue(all(x["severity"]=="CRITICAL" for x in a))

if __name__=="__main__": unittest.main()
