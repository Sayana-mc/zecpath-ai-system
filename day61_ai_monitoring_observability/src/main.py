import json
from pathlib import Path
from .observability import Observability, read_jsonl, dashboard, alerts

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"output"
CFG = json.loads((ROOT/"config"/"observability_config.json").read_text(encoding="utf-8"))

def main():
    OUT.mkdir(exist_ok=True)
    for name in ["api_logs.jsonl","model_logs.jsonl","error_logs.jsonl","decision_audit.jsonl"]:
        p=OUT/name
        if p.exists(): p.unlink()
    o=Observability(OUT)
    statuses=[200,200,201,200,500,200,200,429,200,200,200,503]
    durations=[120,145,180,210,3200,160,190,1100,220,175,130,3500]
    for i,(status,ms) in enumerate(zip(statuses,durations),1):
        o.api("/api/candidates/process","POST",status,ms,f"demo-{i:03d}")
    o.model("resume-parser","v1-demo","resume_parsing",340,True,"candidate-ref-001")
    o.model("interview-analyzer","v1-demo","interview_analysis",860,True,"candidate-ref-002")
    o.model("interview-analyzer","v1-demo","interview_analysis",4100,False,"candidate-ref-003")
    o.error("interview-analyzer","TimeoutError","Model request exceeded timeout","demo-003")
    o.decision("candidate-ref-001","REVIEW_REQUIRED","Recruiter review required","system","screening-v1-demo",False,"demo-001")
    o.decision("candidate-ref-002","SHORTLIST","Recruiter approved after evidence review","recruiter-demo","screening-v1-demo",True,"demo-002")
    summary=dashboard(read_jsonl(OUT/"api_logs.jsonl"),read_jsonl(OUT/"model_logs.jsonl"),read_jsonl(OUT/"decision_audit.jsonl"))
    findings=alerts(summary,CFG)
    (OUT/"dashboard_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    (OUT/"alerts.json").write_text(json.dumps(findings,indent=2),encoding="utf-8")
    print("Day 61 synthetic observability demo completed.")
    print("API requests:",summary["candidate_processing"]["api_requests"])
    print("API failure rate:",summary["candidate_processing"]["failure_rate_percent"],"%")
    print("API p95 latency:",summary["candidate_processing"]["p95_response_ms"],"ms")
    print("Decision audit events:",summary["decision_audit"]["events"])
    print("Alerts generated:",len(findings))
    print("Output folder:",OUT)

if __name__ == "__main__": main()
