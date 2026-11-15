"""Execute and verify all HR interview endpoints against running FastAPI server."""
import json
import requests

BASE = "http://127.0.0.1:8000"
session = requests.Session()

# 1. Authenticate recruiter
auth_res = session.post(
    f"{BASE}/api/v1/auth/session",
    json={"username": "recruiter-d41-52", "password": "Password123!LongEnough"},
    headers={"Origin": BASE}
)
assert auth_res.status_code == 200, f"Auth failed: {auth_res.text}"

log = []

def record(name, method, url, status, req=None, resp=None, note=""):
    actual = resp.status_code if resp is not None else None
    passed = (actual == status)
    preview = None
    if resp is not None:
        if "application/json" in resp.headers.get("content-type", ""):
            try:
                preview = resp.json()
            except Exception:
                preview = resp.text[:200]
        else:
            preview = resp.text[:200]
    entry = {
        "test_name": name,
        "method": method,
        "url": url,
        "expected_status": status,
        "actual_status": actual,
        "pass": passed,
        "request_body": req,
        "response_preview": preview,
        "note": note
    }
    log.append(entry)
    print(f"[{name}] {method} {url} -> {actual} (PASS: {passed})")

# 1. Get existing candidate and opening
cand_res = session.get(f"{BASE}/api/v1/candidates?limit=1")
cand_id = cand_res.json()[0]["candidate_id"]
op_id = cand_res.json()[0]["opening_id"]

# 2. POST /api/v1/hr-interviews (Valid)
create_payload = {
    "candidate_id": cand_id,
    "opening_id": op_id,
    "experience_level": "EXPERIENCED",
    "role_type": "TECHNICAL"
}
r = session.post(f"{BASE}/api/v1/hr-interviews", json=create_payload, headers={"Origin": BASE})
record("Create Session", "POST", "/api/v1/hr-interviews", 201, create_payload, r)
iid = r.json()["interview_id"]

# 3. POST /api/v1/hr-interviews (Invalid candidate 404)
r_inv = session.post(f"{BASE}/api/v1/hr-interviews", json={**create_payload, "candidate_id": "non_existent_c999"}, headers={"Origin": BASE})
record("Create Session - Invalid Candidate", "POST", "/api/v1/hr-interviews", 404, {**create_payload, "candidate_id": "non_existent_c999"}, r_inv)

# 4. GET /api/v1/hr-interviews/{iid}
r = session.get(f"{BASE}/api/v1/hr-interviews/{iid}")
record("Get Session", "GET", f"/api/v1/hr-interviews/{iid}", 200, None, r)

# 5. GET /api/v1/hr-interviews/{iid}/questions
r = session.get(f"{BASE}/api/v1/hr-interviews/{iid}/questions")
record("Get Questions", "GET", f"/api/v1/hr-interviews/{iid}/questions", 200, None, r)
questions = r.json()
first_qid = questions[0]["question_id"]

# 6. POST /api/v1/hr-interviews/{iid}/start
r = session.post(f"{BASE}/api/v1/hr-interviews/{iid}/start", headers={"Origin": BASE})
record("Start Session", "POST", f"/api/v1/hr-interviews/{iid}/start", 200, None, r)

# 7. POST /api/v1/hr-interviews/{iid}/answers (Valid)
ans_payload = {
    "question_id": first_qid,
    "answer_text": "I designed and deployed scalable microservices using Python FastAPI and AWS EKS with zero downtime deployments."
}
r = session.post(f"{BASE}/api/v1/hr-interviews/{iid}/answers", json=ans_payload, headers={"Origin": BASE})
record("Submit Answer", "POST", f"/api/v1/hr-interviews/{iid}/answers", 200, ans_payload, r)

# 8. POST /api/v1/hr-interviews/{iid}/follow-ups (Valid)
fu_payload = {
    "parent_question_id": first_qid,
    "followup_type": "deepening",
    "followup_question": "How did you handle distributed transactions and database rollback scenarios?",
    "candidate_response": "We implemented the Saga pattern with compensating transactions orchestrated via Kafka event topics."
}
r = session.post(f"{BASE}/api/v1/hr-interviews/{iid}/follow-ups", json=fu_payload, headers={"Origin": BASE})
record("Submit Follow-up", "POST", f"/api/v1/hr-interviews/{iid}/follow-ups", 201, fu_payload, r)

# 9. POST /api/v1/hr-interviews/{iid}/pause & resume
r = session.post(f"{BASE}/api/v1/hr-interviews/{iid}/pause", headers={"Origin": BASE})
record("Pause Session", "POST", f"/api/v1/hr-interviews/{iid}/pause", 200, None, r)
r = session.post(f"{BASE}/api/v1/hr-interviews/{iid}/resume", headers={"Origin": BASE})
record("Resume Session", "POST", f"/api/v1/hr-interviews/{iid}/resume", 200, None, r)

# 10. POST /api/v1/hr-interviews/{iid}/complete
r = session.post(f"{BASE}/api/v1/hr-interviews/{iid}/complete", headers={"Origin": BASE})
record("Complete Session", "POST", f"/api/v1/hr-interviews/{iid}/complete", 200, None, r)

# 11. GET /api/v1/hr-interviews/{iid}/evaluation
r = session.get(f"{BASE}/api/v1/hr-interviews/{iid}/evaluation")
record("Get Evaluation Breakdown", "GET", f"/api/v1/hr-interviews/{iid}/evaluation", 200, None, r)

# 12. GET /api/v1/hr-interviews/{iid}/report (JSON)
r = session.get(f"{BASE}/api/v1/hr-interviews/{iid}/report")
record("Get JSON Report", "GET", f"/api/v1/hr-interviews/{iid}/report", 200, None, r)

# 13. GET /api/v1/hr-interviews/{iid}/report?format=html
r = session.get(f"{BASE}/api/v1/hr-interviews/{iid}/report?format=html")
record("Get HTML Report", "GET", f"/api/v1/hr-interviews/{iid}/report?format=html", 200, None, r, "Rendered HTML report")

# 14. POST /api/v1/hr-interviews/{iid}/decision
dec_payload = {"decision": "PROCEED", "notes": "Exceptional architecture depth, articulate communication, strong aptitude."}
r = session.post(f"{BASE}/api/v1/hr-interviews/{iid}/decision", json=dec_payload, headers={"Origin": BASE})
record("Record Decision", "POST", f"/api/v1/hr-interviews/{iid}/decision", 200, dec_payload, r)

# 15. GET /api/v1/hr-interviews/candidates/{cand_id}/reports
r = session.get(f"{BASE}/api/v1/hr-interviews/candidates/{cand_id}/reports")
record("List Candidate Reports", "GET", f"/api/v1/hr-interviews/candidates/{cand_id}/reports", 200, None, r)

out_file = "day33_40_screenshot_audit/server_diagnostics/swagger_api_execution_log.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(log, f, indent=2)

print(f"\nAll {len(log)} API executions logged to {out_file}")

