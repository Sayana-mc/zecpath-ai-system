"""Tests for Days 53–60: Hiring Intelligence Reports, Security, Simulation, Coaching & Scalability."""

import json
import pytest
from starlette.testclient import TestClient

from src.main import app
from src import database
from src.auth import hash_recruiter_password
from src.hiring_intelligence_report_generator import generate_candidate_hiring_report
from src.optimization_engine import optimization_engine
from src.security_governance import security_governance
from src.simulation_pipeline import system_simulation_pipeline
from src.coaching_engine import coaching_engine
from src.batch_processing import TTLCache, chunked, run_scalability_benchmark


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_day53_60.db")
    monkeypatch.setenv("ZECPATH_DB_PATH", str(test_db))
    database._init_db()

    # Seed authenticated recruiter
    salt, hashed = hash_recruiter_password("TestSecret123!")
    database.create_first_recruiter_account(
        username="recruiter_day53",
        password_salt=salt,
        password_hash=hashed,
    )
    test_client = TestClient(app, headers={"Origin": "http://testserver"})
    # Login
    login_resp = test_client.post(
        "/api/v1/auth/session",
        json={"username": "recruiter_day53", "password": "TestSecret123!"},
    )
    assert login_resp.status_code == 200
    return test_client


def _setup_full_evaluation_candidate():
    """Seeds a candidate with comprehensive multi-round data."""
    op = database.save_opening(
        title="Senior Python Architect",
        description="Lead backend platform",
        requirements=["Python", "FastAPI", "PostgreSQL", "Docker"],
        preferred_skills=["Kubernetes", "Redis"],
    )
    cand = database.create_candidate(
        name="Alex Rivera",
        email="alex.rivera@example.com",
        opening_id=op["opening_id"],
        skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
    )
    database.save_candidate_resume(
        candidate_id=cand["candidate_id"],
        filename="resume.txt",
        parsed_text="Experienced engineer in Python, FastAPI, Docker, and PostgreSQL architecture.",
        resume_data={"skills": ["Python", "FastAPI", "PostgreSQL", "Docker"]},
    )
    database.save_candidate_score(
        candidate_id=cand["candidate_id"],
        score=88.0,
        evidence={"matched_required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"], "missing_required_skills": []},
    )
    # Screening
    database.save_screening_session_full(
        candidate_id=cand["candidate_id"],
        opening_id=op["opening_id"],
        overall_score=85.0,
        status="COMPLETED",
        summary_notes="Clear communication and strong system design fundamentals.",
    )
    # Technical
    t_sess = database.create_technical_interview_session(
        candidate_id=cand["candidate_id"],
        opening_id=op["opening_id"],
        target_role=op["title"],
        experience_level="senior",
    )
    database.save_technical_interview_response({
        "response_id": "trsp_01",
        "interview_id": t_sess["session_id"],
        "question_id": "q_arch_01",
        "answer_text": "Detailed PostgreSQL connection pooling and read-replica architecture.",
        "accuracy_score": 4.8,
        "depth_score": 4.6,
        "reasoning_score": 4.5,
        "applicability_score": 4.5,
        "depth_classification": "deep",
        "weighted_score": 92.0,
        "normalized_score": 92.0,
        "explanation": "Deep architectural understanding.",
    })
    database.update_technical_interview_session_status(t_sess["session_id"], "COMPLETED")
    # Machine Test
    m_test = database.create_machine_test_assignment(
        candidate_id=cand["candidate_id"],
        opening_id=op["opening_id"],
        task_type="coding",
        task_id="t_01",
        title="Async Task Queue",
        description="Resilient worker queue",
    )
    database.save_machine_test_submission({
        "submission_id": "sub_01",
        "test_id": m_test["test_id"],
        "candidate_id": cand["candidate_id"],
        "code_content": "async def queue(): pass",
        "elapsed_time_minutes": 25.0,
        "correctness_score": 95.0,
        "efficiency_score": 90.0,
        "code_quality_score": 92.0,
        "problem_solving_score": 90.0,
        "time_management_score": 95.0,
        "total_score": 92.5,
        "test_results": [{"passed": True}],
        "evaluation_summary": "Passed all unit tests.",
    })
    database.update_machine_test_assignment_status(m_test["test_id"], "EVALUATED")
    # Cross-Round Evaluation
    database.save_cross_round_evaluation({
        "candidate_id": cand["candidate_id"],
        "opening_id": op["opening_id"],
        "target_role": op["title"],
        "hiring_fit_percentage": 89.4,
        "round_scores": {"ats": 88.0, "screening": 85.0, "technical_interview": 92.0, "machine_test": 92.5},
        "effective_weights": {"ats": 0.25, "screening": 0.25, "technical_interview": 0.25, "machine_test": 0.25},
        "completed_rounds": 4,
        "missing_rounds": ["hr_interview"],
        "anomalies": [],
    })
    # Final Recommendation
    database.save_final_recommendation(
        candidate_id=cand["candidate_id"],
        opening_id=op["opening_id"],
        target_role=op["title"],
        decision="SELECTED",
        score=89.4,
        confidence=0.88,
        completed_rounds=4,
        expected_rounds=5,
        reasons=["High overall score exceeding 80% threshold", "Deep architectural performance in technical rounds"],
        risk_factors={"integrity": {"flag": False}, "behavior": {"flag": False}},
    )
    return cand, op


# ============================================================================
# Day 53: Hiring Intelligence Report Generator Tests
# ============================================================================

def test_day53_hiring_intelligence_report_generation(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_day53.db")
    monkeypatch.setenv("ZECPATH_DB_PATH", str(test_db))
    database._init_db()

    cand, op = _setup_full_evaluation_candidate()
    report = generate_candidate_hiring_report(candidate_id=cand["candidate_id"], save_to_db=True)

    assert "report_id" in report
    assert report["candidate_name"] == "Alex Rivera"
    assert report["unified_hiring_fit_score"] == 89.4
    assert report["final_recommendation"]["decision"] == "SELECTED"
    assert len(report["strengths"]) >= 1
    assert "evaluation_summary" in report
    assert report["evaluation_summary"]["ats"]["score"] == 88.0
    assert report["evaluation_summary"]["technical_interview"]["score"] == 92.0
    assert "advisory only" in report["disclaimer"].lower()

    # Verify database persistence
    saved = database.get_hiring_intelligence_report(report["report_id"])
    assert saved is not None
    assert saved["candidate_id"] == cand["candidate_id"]
    assert "<h1>" in saved["html_content"]
    assert "# ZecPath" in saved["markdown_content"]


def test_day53_report_versioning_and_history(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_day53_ver.db")
    monkeypatch.setenv("ZECPATH_DB_PATH", str(test_db))
    database._init_db()

    cand, op = _setup_full_evaluation_candidate()
    r1 = generate_candidate_hiring_report(candidate_id=cand["candidate_id"], save_to_db=True)
    assert r1["version"] == 1

    # Regenerate report (e.g. after score change)
    r2 = generate_candidate_hiring_report(candidate_id=cand["candidate_id"], save_to_db=True)
    assert r2["version"] == 2

    history = database.list_hiring_intelligence_reports(cand["candidate_id"])
    assert len(history) == 2
    assert history[0]["version"] == 2
    assert history[1]["version"] == 1


# ============================================================================
# Day 54: Optimization & Refinement Tests
# ============================================================================

def test_day54_threshold_accuracy_metrics():
    cases = [
        {"score": 85.0, "ground_truth": "SELECTED"},
        {"score": 82.0, "ground_truth": "SELECTED"},
        {"score": 75.0, "ground_truth": "HOLD_REVIEW"},
        {"score": 65.0, "ground_truth": "HOLD_REVIEW"},
        {"score": 45.0, "ground_truth": "REJECTED"},
        {"score": 88.0, "ground_truth": "HOLD_REVIEW"},  # False positive
    ]
    res = optimization_engine.analyze_threshold_accuracy(cases)
    assert res["total_cases"] == 6
    assert res["accuracy"] >= 0.80
    assert res["confusion_matrix"]["tp"] == 2
    assert res["confusion_matrix"]["fp"] == 1
    assert res["precision"] > 0.60


def test_day54_score_contradiction_detection():
    # ATS says 95, Technical Interview says 30
    scores = {"ats": 95.0, "technical_interview": 30.0, "machine_test": 35.0}
    contradictions = optimization_engine.detect_score_contradictions(scores)
    assert len(contradictions) >= 1
    assert "contradiction" in contradictions[0].lower()


def test_day54_intent_refinement():
    # Ambiguous short response
    res_ambiguous = optimization_engine.refine_candidate_intent("yes okay")
    assert res_ambiguous["requires_clarification"] is True
    assert res_ambiguous["refined_intent"] == "clarification_needed"

    # Confident detailed response
    res_confident = optimization_engine.refine_candidate_intent(
        "I have 5 years experience designing PostgreSQL distributed systems with connection pooling.",
        detected_intent="provide_experience",
        confidence=0.92,
    )
    assert res_confident["requires_clarification"] is False
    assert res_confident["refined_intent"] == "provide_experience"


# ============================================================================
# Day 55: Security & AI Governance Tests
# ============================================================================

def test_day55_audit_trail_tamper_detection(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_audit.db")
    monkeypatch.setenv("ZECPATH_DB_PATH", str(test_db))
    database._init_db()

    # Append 3 legitimate events
    e1 = security_governance.log_audit_event("SCORE_RECORDED", "rec_01", "cand_01", {"score": 85})
    e2 = security_governance.log_audit_event("RECOMMENDATION_MADE", "rec_01", "cand_01", {"decision": "SELECTED"})
    e3 = security_governance.log_audit_event("REPORT_EXPORTED", "rec_01", "cand_01", {"format": "HTML"})

    # Verify intact chain
    v1 = security_governance.verify_audit_trail()
    assert v1["verified"] is True
    assert v1["event_count"] == 3

    # Tamper with an event in SQLite directly
    with database._connection() as conn:
        conn.execute("UPDATE audit_events SET event_hash = 'TAMPERED_HASH' WHERE event_id = ?", (e2["event_id"],))

    v2 = security_governance.verify_audit_trail()
    assert v2["verified"] is False
    assert v2["tampered_at_index"] == 1


def test_day55_rbac_and_retention():
    # RBAC permissions
    assert security_governance.check_permission("recruiter", "score_candidate") is True
    assert security_governance.check_permission("recruiter", "manage_users") is False
    assert security_governance.check_permission("admin", "manage_users") is True
    assert security_governance.check_permission("auditor", "verify_audit_integrity") is True

    # Retention calculation
    retention = security_governance.check_data_retention("2026-01-01T00:00:00Z", retention_days=180)
    assert retention["retention_days"] == 180
    assert "expires_at" in retention


# ============================================================================
# Day 56: System Simulation Pipeline Tests
# ============================================================================

def test_day56_system_simulation_pipeline(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_sim.db")
    monkeypatch.setenv("ZECPATH_DB_PATH", str(test_db))
    database._init_db()

    candidate_input = {
        "name": "Jordan Lee",
        "email": "jordan.lee@example.com",
        "ats_score": 86.0,
        "screening_score": 84.0,
        "hr_interview_score": 82.0,
        "technical_interview_score": 90.0,
        "machine_test_score": 88.0,
    }
    opening_input = {
        "title": "Cloud Solutions Architect",
        "description": "Design high-throughput distributed systems",
        "requirements": ["Python", "FastAPI", "PostgreSQL", "AWS"],
    }
    sim_result = system_simulation_pipeline.simulate_candidate_pipeline(candidate_input, opening_input)
    assert sim_result["pipeline_success"] is True
    assert sim_result["unified_fit_score"] >= 80.0
    assert sim_result["ai_recommendation"] == "SELECTED"
    assert "hiring_report_generation" in sim_result["stage_statuses"]


def test_day56_ai_vs_human_comparison():
    simulations = [
        {"candidate_id": "c1", "unified_fit_score": 88.0, "ai_recommendation": "SELECTED"},
        {"candidate_id": "c2", "unified_fit_score": 72.0, "ai_recommendation": "HOLD_REVIEW"},
        {"candidate_id": "c3", "unified_fit_score": 45.0, "ai_recommendation": "REJECTED"},
    ]
    human_evaluations = [
        {"candidate_id": "c1", "human_score": 85.0, "human_decision": "SELECTED"},
        {"candidate_id": "c2", "human_score": 75.0, "human_decision": "HOLD_REVIEW"},
        {"candidate_id": "c3", "human_score": 40.0, "human_decision": "REJECTED"},
    ]
    res = system_simulation_pipeline.compare_ai_vs_human_evaluations(simulations, human_evaluations)
    assert res["total_evaluated"] == 3
    assert res["decision_alignment_rate_percent"] == 100.0
    assert res["average_score_gap"] <= 5.0


# ============================================================================
# Day 58: Candidate Coaching & Guardrails Tests
# ============================================================================

def test_day58_candidate_coaching_guardrails(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_coach.db")
    monkeypatch.setenv("ZECPATH_DB_PATH", str(test_db))
    database._init_db()

    cand, op = _setup_full_evaluation_candidate()
    coaching = coaching_engine.generate_candidate_coaching(cand["candidate_id"], target_role="Python Architect")

    assert coaching["candidate_id"] == cand["candidate_id"]
    assert len(coaching["identified_skill_gaps"]) >= 1
    assert len(coaching["practice_questions"]) >= 2
    assert coaching["governance_guardrails"]["influences_hiring_status"] is False
    assert coaching["governance_guardrails"]["emotion_detection_enabled"] is False
    assert coaching["governance_guardrails"]["automatic_rejection_enabled"] is False
    assert "developmental aids" in coaching["disclaimer"].lower()


# ============================================================================
# Day 60: Batching, Caching & Scalability Tests
# ============================================================================

def test_day60_batching_and_lru_cache():
    # 1. Chunked helper
    items = [1, 2, 3, 4, 5, 6, 7]
    chunks = list(chunked(items, 3))
    assert chunks == [[1, 2, 3], [4, 5, 6], [7]]

    # 2. TTLCache LRU & Hit rate
    cache = TTLCache(max_entries=2, ttl_seconds=30)
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    assert cache.get("k1") == "v1"
    # Overwrite by inserting k3 -> k2 evicted
    cache.set("k3", "v3")
    assert cache.size == 2
    assert cache.get("k2") is None
    assert cache.get("k3") == "v3"
    assert cache.hit_rate > 0.0

    # 3. Scalability benchmark
    bench = run_scalability_benchmark(sample_count=20, concurrency_levels=[1, 2])
    assert len(bench["concurrency_cases"]) == 2
    assert bench["concurrency_cases"][0]["throughput_items_per_sec"] > 0.0


# ============================================================================
# Integrated REST API Endpoints Tests
# ============================================================================

def test_day53_to_day60_integrated_rest_api(client):
    """Verifies all new endpoints via authenticated HTTP calls."""
    # 1. Create opening & candidate
    op_resp = client.post("/api/v1/openings", json={"title": "ML Platform Engineer", "description": "PyTorch & FastAPI", "required_skills": ["Python", "PyTorch", "FastAPI"]})
    assert op_resp.status_code == 201
    op_id = op_resp.json()["opening_id"]

    cand_resp = client.post("/api/v1/candidates", json={
        "name": "Sam Taylor",
        "email": "sam.taylor@example.com",
        "opening_id": op_id,
        "skills": ["Python", "PyTorch", "FastAPI"],
    })
    assert cand_resp.status_code == 201
    cand_id = cand_resp.json()["candidate_id"]

    # 2. Generate Hiring Intelligence Report
    rep_resp = client.post(f"/api/v1/candidates/{cand_id}/hiring-intelligence-report")
    assert rep_resp.status_code == 201
    rep_data = rep_resp.json()
    assert "report_id" in rep_data
    report_id = rep_data["report_id"]

    # Get latest report
    latest_resp = client.get(f"/api/v1/candidates/{cand_id}/hiring-intelligence-report")
    assert latest_resp.status_code == 200
    assert latest_resp.json()["report_id"] == report_id

    # Get report history
    hist_resp = client.get(f"/api/v1/candidates/{cand_id}/hiring-intelligence-report/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1

    # Get HTML export
    html_resp = client.get(f"/api/v1/hiring-intelligence-reports/{report_id}/html")
    assert html_resp.status_code == 200
    assert "<!DOCTYPE html>" in html_resp.text

    # Get Markdown export
    md_resp = client.get(f"/api/v1/hiring-intelligence-reports/{report_id}/markdown")
    assert md_resp.status_code == 200
    assert "# ZecPath" in md_resp.text

    # 3. Audit trail endpoints
    audit_resp = client.get("/api/v1/audit/events")
    assert audit_resp.status_code == 200
    assert len(audit_resp.json()) >= 1

    verify_resp = client.get("/api/v1/audit/verify")
    assert verify_resp.status_code == 200
    assert verify_resp.json()["verified"] is True

    # 4. Candidate AI Coaching endpoint
    coach_resp = client.post(f"/api/v1/candidates/{cand_id}/coaching")
    assert coach_resp.status_code == 201
    assert len(coach_resp.json()["practice_questions"]) >= 1

    # 5. Full Simulation run
    sim_resp = client.post("/api/v1/simulation/run", json={
        "candidate": {"name": "Simulated Alex", "email": "sim_alex@example.com"},
        "opening": {"title": "Platform Lead", "description": "Lead team"},
    })
    assert sim_resp.status_code == 201
    assert sim_resp.json()["pipeline_success"] is True

    # 6. Batch Resume Processing
    batch_resp = client.post("/api/v1/resumes/batch-process", json={
        "resumes": [
            {"candidate_id": "c1", "text": "Senior Python developer with FastAPI"},
            {"candidate_id": "c2", "text": "Frontend engineer with React and Docker"},
        ],
        "batch_size": 2,
        "max_concurrency": 2,
    })
    assert batch_resp.status_code == 200
    assert batch_resp.json()["successful_count"] == 2
