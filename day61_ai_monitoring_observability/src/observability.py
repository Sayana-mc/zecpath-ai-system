import json, uuid
from datetime import datetime, timezone
from pathlib import Path

def now():
    return datetime.now(timezone.utc).isoformat()

def append_jsonl(path, event):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")

class Observability:
    def __init__(self, output_dir, service="zecpath-ai-hiring"):
        self.out, self.service = Path(output_dir), service

    def _base(self, kind, correlation_id=None):
        return {"timestamp": now(), "event_id": str(uuid.uuid4()),
                "event_type": kind, "service": self.service,
                "correlation_id": correlation_id or str(uuid.uuid4())}

    def api(self, endpoint, method, status_code, duration_ms, correlation_id=None):
        e = self._base("api_request", correlation_id)
        e.update(endpoint=endpoint, method=method, status_code=int(status_code),
                 duration_ms=round(float(duration_ms), 2),
                 success=200 <= int(status_code) < 400)
        append_jsonl(self.out/"api_logs.jsonl", e)
        return e

    def model(self, model_name, model_version, task, duration_ms, success, input_ref=None):
        e = self._base("model_run")
        e.update(model_name=model_name, model_version=model_version, task=task,
                 duration_ms=round(float(duration_ms), 2), success=bool(success),
                 input_ref=input_ref)  # reference only; never raw resume text
        append_jsonl(self.out/"model_logs.jsonl", e)
        return e

    def error(self, component, error_type, safe_message, correlation_id=None):
        e = self._base("error", correlation_id)
        e.update(component=component, error_type=error_type, message=safe_message[:300])
        append_jsonl(self.out/"error_logs.jsonl", e)
        return e

    def decision(self, candidate_ref, decision, reason, actor, model_version, human_reviewed,
                 correlation_id=None):
        allowed = {"SHORTLIST", "REVIEW_REQUIRED", "NOT_SHORTLISTED", "PENDING"}
        if decision not in allowed:
            raise ValueError("Unsupported decision status")
        e = self._base("decision_audit", correlation_id)
        e.update(candidate_ref=candidate_ref, decision=decision, reason=reason[:500],
                 actor=actor, model_version=model_version, human_reviewed=bool(human_reviewed))
        append_jsonl(self.out/"decision_audit.jsonl", e)
        return e

def read_jsonl(path):
    p = Path(path)
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []

def percentile(values, pct):
    if not values: return 0.0
    s = sorted(values)
    return round(s[min(len(s)-1, int(round((pct/100)*(len(s)-1))))], 2)

def dashboard(api, models, decisions):
    times = [float(x["duration_ms"]) for x in api]
    failed = sum(not x.get("success", False) for x in api)
    interviews = [x for x in models if x.get("task") == "interview_analysis"]
    decision_counts = {}
    for d in decisions:
        decision_counts[d["decision"]] = decision_counts.get(d["decision"], 0) + 1
    return {
      "generated_at": now(),
      "candidate_processing": {
        "api_requests": len(api), "api_failures": failed,
        "failure_rate_percent": round(failed/len(api)*100, 2) if api else 0.0,
        "p50_response_ms": percentile(times, 50), "p95_response_ms": percentile(times, 95),
        "model_runs": len(models), "model_failures": sum(not x.get("success") for x in models)},
      "interview_metrics": {
        "analysis_runs": len(interviews),
        "analysis_success_rate_percent": round(sum(x.get("success",False) for x in interviews)/len(interviews)*100,2) if interviews else 0.0},
      "decision_audit": {"events": len(decisions),
        "human_reviewed_events": sum(x.get("human_reviewed",False) for x in decisions),
        "decision_counts": decision_counts},
      "accuracy_note": "Calculate accuracy only against reviewed ground-truth labels."
    }

def alerts(summary, cfg):
    m = summary["candidate_processing"]
    out = []
    if m["api_requests"] >= cfg["minimum_events_for_failure_alert"]:
        rate = m["failure_rate_percent"]
        if rate >= cfg["failure_rate_critical_percent"]:
            out.append({"rule":"api_failure_rate","severity":"CRITICAL","value":rate})
        elif rate >= cfg["failure_rate_warning_percent"]:
            out.append({"rule":"api_failure_rate","severity":"WARNING","value":rate})
    p95 = m["p95_response_ms"]
    if p95 >= cfg["latency_critical_ms"]:
        out.append({"rule":"api_p95_latency","severity":"CRITICAL","value":p95})
    elif p95 >= cfg["latency_warning_ms"]:
        out.append({"rule":"api_p95_latency","severity":"WARNING","value":p95})
    return out
