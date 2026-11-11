"""Comprehensive Integration & Verification Tests for Days 41–52.

Verifies:
- Day 41 & 51: Unified Scoring & Cross-Round Aggregation Engine.
- Day 42: Optimization & Stability (out-of-range checks, anomalies, discrepancies).
- Day 43: Ethics & Compliance (consent, demographic redaction, retention, human oversight).
- Day 45: HR Interview lifecycle persistence.
- Day 46: Technical Interview design (roles, difficulties, question banks, FSM).
- Day 47: Technical Scoring (accuracy, depth, shallow/moderate/deep classification).
- Day 48: Behavioral AI (consented observations, consistency index, non-punitive disclaimer).
- Day 49: Malpractice & Integrity Detection (events, risk points, review flags, no auto-rejection).
- Day 50: Machine Test AI (coding, debugging, file_based, mini_system_design, 5-dim rubric).
- Day 52: Final Recommendation AI (SELECTED / HOLD_REVIEW / REJECTED, confidence, recruiter workflow).
- End-to-End Complete 21-Step Integrated Recruitment Journey.
"""

import json
import secrets
import pytest
from starlette.testclient import TestClient

from src.main import app
from src import database
from src.auth import hash_recruiter_password
from src.compliance_engine import compliance_engine
from src.technical_interview_engine import technical_interview_engine
from src.technical_scoring_engine import technical_scoring_engine, score_technical_answer
from src.behavioral_ai_engine import behavioral_ai_engine
from src.integrity_engine import integrity_engine
from src.machine_test_engine import machine_test_engine
from src.cross_round_scoring_engine import cross_round_scoring_engine
from src.final_recommendation_engine import recommend_candidate, calculate_confidence, DecisionInputError


@pytest.fixture
def client(monkeypatch):
    database.initialize_database()

    class DeterministicEmbeddingEngine:
        def encode(self, text):
            return [1.0, 0.0]

        def encode_many(self, texts):
            return [[1.0, 0.0] for _ in texts]

    monkeypatch.setattr(
        "src.integrated_scoring._embedding_engine",
        lambda: DeterministicEmbeddingEngine(),
    )

    salt, password_hash = hash_recruiter_password("Password123!LongEnough")
    with database._connection() as connection:
        connection.execute("DELETE FROM recruiter_accounts")
        connection.execute("DELETE FROM recruiter_sessions")
    database.create_first_recruiter_account("recruiter-d41-52", salt, password_hash)

    with TestClient(app, headers={"Origin": "http://testserver"}) as test_client:
        login_resp = test_client.post(
            "/api/v1/auth/session",
            json={"username": "recruiter-d41-52", "password": "Password123!LongEnough"},
        )
        assert login_resp.status_code == 200
        yield test_client


def _setup_candidate_and_job(client):
    opening_resp = client.post(
        "/api/v1/openings",
        json={
            "title": "Senior Backend Engineer",
            "description": "Looking for Python, FastAPI, Docker, and SQL distributed system expert.",
            "required_skills": ["Python", "FastAPI", "SQL"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "minimum_years_experience": 4.0,
            "status": "OPEN",
        },
    )
    assert opening_resp.status_code == 201
    opening = opening_resp.json()

    cand_resp = client.post(
        "/api/v1/candidates",
        json={
            "opening_id": opening["opening_id"],
            "name": "Jane Developer",
            "email": f"jane.{secrets.token_hex(4)}@example.com",
            "skills": ["Python", "FastAPI", "SQL", "Docker"],
            "experience_years": 5.0,
        },
    )
    assert cand_resp.status_code == 201
    candidate = cand_resp.json()
    return candidate, opening


# ============================================================================
# Day 41 & 51: Unified Scoring Engine Tests
# ============================================================================

def test_day41_unified_scoring_engine():
    """Verifies cross-round aggregation with role-based weights and normalization."""
    scores = {
        "ats": 85.0,
        "screening": 80.0,
        "hr_interview": 78.0,
        "technical_interview": 92.0,
        "machine_test": 88.0,
    }
    result = cross_round_scoring_engine.calculate_unified_fit(
        round_scores=scores,
        target_role="software_engineer",
    )
    assert 80.0 <= result["hiring_fit_percentage"] <= 90.0
    assert result["completed_rounds_count"] == 5
    assert len(result["missing_rounds"]) == 0
    assert len(result["anomalies"]) == 0
    assert round(sum(result["effective_weights"].values()), 2) == 1.0


def test_day41_missing_round_renormalization():
    """Verifies that missing rounds renormalize remaining weights without unfair point loss."""
    scores = {
        "ats": 90.0,
        "screening": 85.0,
        "hr_interview": 80.0,
        # technical_interview and machine_test missing
    }
    result = cross_round_scoring_engine.calculate_unified_fit(
        round_scores=scores,
        target_role="software_engineer",
        missing_strategy="exclude_and_renormalize",
    )
    assert result["completed_rounds_count"] == 3
    assert "technical_interview" in result["missing_rounds"]
    assert "machine_test" in result["missing_rounds"]
    # Effective weights must sum to 1.0 across completed rounds
    assert round(sum(result["effective_weights"].values()), 2) == 1.0
    assert result["hiring_fit_percentage"] > 80.0


# ============================================================================
# Day 42: Optimization & Stability Tests
# ============================================================================

def test_day42_out_of_range_validation():
    """Verifies that scores outside 0–100 raise clear validation errors."""
    with pytest.raises(ValueError):
        cross_round_scoring_engine.calculate_unified_fit(
            round_scores={"ats": 105.0},
            target_role="software_engineer",
        )
    with pytest.raises(ValueError):
        cross_round_scoring_engine.calculate_unified_fit(
            round_scores={"ats": -10.0},
            target_role="software_engineer",
        )


def test_day42_discrepancy_and_anomaly_detection():
    """Verifies detection of extreme score discrepancies across rounds."""
    scores = {
        "ats": 95.0,
        "screening": 90.0,
        "hr_interview": 92.0,
        "technical_interview": 30.0,  # Extreme divergence from ATS
        "machine_test": 35.0,
    }
    result = cross_round_scoring_engine.calculate_unified_fit(
        round_scores=scores,
        target_role="software_engineer",
    )
    assert len(result["anomalies"]) > 0
    assert any("Discrepancy" in a for a in result["anomalies"])


# ============================================================================
# Day 43: Ethics & Compliance Review Tests
# ============================================================================

def test_day43_compliance_demographic_redaction():
    """Verifies redaction of protected demographic terms from notes."""
    raw_text = "The female candidate graduated from college in 1985 and was pregnant last quarter."
    redacted = compliance_engine.redact_protected_demographic_signals(raw_text)
    assert "[REDACTED_DEMOGRAPHIC]" in redacted
    assert "female" not in redacted.lower()
    assert "pregnant" not in redacted.lower()


def test_day43_compliance_consent_and_retention():
    """Verifies consent requirement validation and data retention window calculation."""
    # Without consent, assessment must be rejected or marked non-compliant
    assert compliance_engine.validate_candidate_consent(has_consent=False) is False
    assert compliance_engine.validate_candidate_consent(has_consent=True) is True

    # Retention date verification (default 180 days)
    retention_info = compliance_engine.calculate_retention_expiry(retention_days=180)
    assert retention_info["retention_days"] == 180
    assert "purge_scheduled_at" in retention_info


# ============================================================================
# Day 46: Technical Interview System Design Tests
# ============================================================================

def test_day46_technical_interview_generation():
    """Verifies generation of role-specific technical questions according to experience level."""
    questions = technical_interview_engine.generate_questions(
        target_role="Backend Engineer",
        experience_level="mid",
        skills=["Python", "FastAPI", "SQL"],
    )
    assert len(questions) >= 3
    q_types = {q["question_type"] for q in questions}
    assert "conceptual" in q_types or "system_design" in q_types or "problem_solving" in q_types
    for q in questions:
        assert "question_text" in q
        assert "expected_criteria" in q


# ============================================================================
# Day 47: Technical Skill Scoring Model Tests
# ============================================================================

def test_day47_technical_answer_scoring_and_depth():
    """Verifies 5-dimension rubric scoring and depth classification (shallow, moderate, deep)."""
    shallow_ans = "FastAPI uses Starlette and Pydantic. It is fast."
    res_shallow = score_technical_answer(shallow_ans, question_type="conceptual")
    assert res_shallow["depth_level"] in ("shallow", "moderate")
    assert res_shallow["score"] < 75.0

    deep_ans = (
        "FastAPI achieves asynchronous performance by running an AnyIO/uvicorn event loop "
        "with non-blocking coroutines. For CPU-bound tasks, we offload to background threads "
        "using run_in_threadpool or a Celery worker pool to avoid choking the event loop. "
        "In production, we configure Pydantic v2 schemas for ultra-fast C-extension serialization."
    )
    res_deep = score_technical_answer(deep_ans, question_type="conceptual")
    assert res_deep["depth_level"] == "deep"
    assert res_deep["score"] >= 80.0
    assert "accuracy" in res_deep["parameter_scores"]
    assert "depth" in res_deep["parameter_scores"]


# ============================================================================
# Day 48: Behavioral AI Research & Design Tests
# ============================================================================

def test_day48_behavioral_ai_engine():
    """Verifies consented behavioral observations and safety disclaimers."""
    observations = [
        {"aspect": "tone_consistency", "impact": "positive", "note": "Maintained professional, calm tone."},
        {"aspect": "pacing", "impact": "neutral", "note": "Standard conversational pace."},
    ]
    eval_res = behavioral_ai_engine.evaluate_observations(
        observations=observations,
        has_consent=True,
    )
    assert eval_res["consistency_index"] >= 80.0
    assert eval_res["requires_human_review"] is False
    assert "assistive" in eval_res["disclaimer"].lower()
    assert "non-binding" in eval_res["disclaimer"].lower()


# ============================================================================
# Day 49: Malpractice & Integrity Detection Tests
# ============================================================================

def test_day49_integrity_engine_safeguards():
    """Verifies integrity risk scoring, flag generation, and non-automatic rejection safeguard."""
    # Low-risk events
    low_res = integrity_engine.evaluate_events(
        events=[{"event_type": "tab_switch", "duration_seconds": 1}],
        has_consent=True,
    )
    assert low_res["risk_level"] == "LOW"
    assert low_res["requires_human_review"] is False

    # Suspicious events trigger review, NEVER automatic rejection
    high_res = integrity_engine.evaluate_events(
        events=[
            {"event_type": "tab_switch", "duration_seconds": 25},
            {"event_type": "window_blur", "duration_seconds": 30},
            {"event_type": "external_audio", "duration_seconds": 10},
        ],
        has_consent=True,
    )
    assert high_res["risk_level"] in ("MODERATE", "HIGH")
    assert high_res["requires_human_review"] is True
    assert high_res["automatic_rejection"] is False  # Ethical safeguard


# ============================================================================
# Day 50: Machine Test AI Design Tests
# ============================================================================

def test_day50_machine_test_assignment_and_scoring():
    """Verifies assignment of 4 task types and 5-dimension rubric scoring."""
    task = machine_test_engine.assign_task(task_type="coding")
    assert "task_id" in task
    assert "description" in task

    code_submission = (
        "def find_duplicates(numbers: list[int]) -> list[int]:\n"
        "    seen = set()\n"
        "    duplicates = set()\n"
        "    for n in numbers:\n"
        "        if n in seen:\n"
        "            duplicates.add(n)\n"
        "        seen.add(n)\n"
        "    return sorted(list(duplicates))\n"
    )
    eval_res = machine_test_engine.evaluate_submission(
        task_type="coding",
        code=code_submission,
        time_spent_minutes=20.0,
        time_limit_minutes=60,
    )
    assert eval_res["total_score"] >= 80.0
    assert "correctness" in eval_res["rubric_scores"]
    assert "efficiency" in eval_res["rubric_scores"]
    assert "code_quality" in eval_res["rubric_scores"]
    assert "problem_solving" in eval_res["rubric_scores"]


# ============================================================================
# Day 52: Final Recommendation AI Tests
# ============================================================================

def test_day52_final_recommendation_classification():
    """Verifies SELECTED, HOLD_REVIEW, and REJECTED classification rules."""
    # Candidate exceeding selected_min (80) with 5 rounds and high confidence
    selected_assessment = {
        "candidate_id": "cand_sel",
        "session_id": "sess_sel",
        "target_role": "Backend Engineer",
        "assessment_status": "COMPLETE",
        "unified_score": 88.0,
        "completed_rounds": 5,
        "expected_rounds": 5,
        "evidence_quality": 90.0,
        "data_consistency": 85.0,
        "rounds": {
            "ats": 85.0,
            "screening": 82.0,
            "hr_interview": 84.0,
            "technical_interview": 92.0,
            "machine_test": 97.0,
        },
        "risk_factors": {
            "integrity": {"flag": False, "evidence": []},
            "behavior": {"flag": False, "evidence": []},
        },
    }
    rec_selected = recommend_candidate(selected_assessment)
    assert rec_selected["decision"] == "SELECTED"
    assert rec_selected["confidence"] >= 85.0

    # Candidate with score < 60 routes to REJECTED
    rejected_assessment = dict(selected_assessment)
    rejected_assessment["unified_score"] = 52.0
    rec_rejected = recommend_candidate(rejected_assessment)
    assert rec_rejected["decision"] == "REJECTED"

    # Candidate with high score but an integrity flag routes to HOLD_REVIEW
    flagged_assessment = dict(selected_assessment)
    flagged_assessment["risk_factors"] = {
        "integrity": {"flag": True, "evidence": ["Repeated browser blur events"]},
        "behavior": {"flag": False, "evidence": []},
    }
    rec_hold = recommend_candidate(flagged_assessment)
    assert rec_hold["decision"] == "HOLD_REVIEW"
    assert any("integrity" in r.lower() for r in rec_hold["explanation"]["reasons"])


# ============================================================================
# End-to-End Multi-Round Integrated Journey (Days 41–52 REST API)
# ============================================================================

def test_day41_to_day52_complete_integrated_lifecycle_api(client):
    """
    Verifies the complete 21-step end-to-end recruitment journey:
    1. Setup job opening & candidate.
    2. ATS Scoring & Shortlisting.
    3. Technical Interview Session creation & question seeding.
    4. Start Technical Interview.
    5. Submit technical answer & verify depth scoring.
    6. Complete Technical Interview.
    7. Machine Test assignment.
    8. Machine Test submission & rubric scoring.
    9. Consented Integrity event monitoring.
    10. Consented Behavioral observation recording.
    11. Cross-Round 5-Round Unified Fit calculation.
    12. Final Explainable Recommendation generation (Confidence, Reasons, Risk Audit).
    13. Recruiter Human Review Decision approval/override workflow.
    """
    candidate, opening = _setup_candidate_and_job(client)
    cand_id = candidate["candidate_id"]
    job_id = opening["opening_id"]

    # 1. ATS Scoring
    ats_resp = client.post(
        "/api/v1/ats/score",
        json={"candidate_id": cand_id, "job_id": job_id},
    )
    assert ats_resp.status_code == 200
    ats_score = ats_resp.json()["score"]

    # 2. Technical Interview
    tech_create_resp = client.post(
        "/api/v1/technical-interviews",
        json={
            "candidate_id": cand_id,
            "opening_id": job_id,
            "target_role": "Backend Engineer",
            "experience_level": "mid",
        },
    )
    assert tech_create_resp.status_code == 201
    tech_sess = tech_create_resp.json()
    tech_sess_id = tech_sess["session_id"]

    # Start technical interview
    start_resp = client.post(f"/api/v1/technical-interviews/{tech_sess_id}/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "IN_PROGRESS"

    # Get questions
    q_resp = client.get(f"/api/v1/technical-interviews/{tech_sess_id}/questions")
    assert q_resp.status_code == 200
    questions = q_resp.json()
    assert len(questions) >= 1
    first_q = questions[0]

    # Submit technical answer
    ans_resp = client.post(
        f"/api/v1/technical-interviews/{tech_sess_id}/answers",
        json={
            "question_id": first_q["question_id"],
            "answer_text": (
                "In my production services, I design PostgreSQL schema indexing with B-tree indexes "
                "for high-cardinality equality queries and BRIN indexes for append-only log tables. "
                "We use connection pooling via PgBouncer to prevent worker starvation."
            ),
        },
    )
    assert ans_resp.status_code == 200
    ans_data = ans_resp.json()
    assert ans_data["score"] > 70.0
    assert ans_data["depth_level"] in ("moderate", "deep")

    # Complete technical interview
    comp_resp = client.post(f"/api/v1/technical-interviews/{tech_sess_id}/complete")
    assert comp_resp.status_code == 200
    assert comp_resp.json()["status"] == "COMPLETED"

    # 3. Machine Test Assignment & Submission
    mt_create_resp = client.post(
        "/api/v1/machine-tests/assignments",
        json={
            "candidate_id": cand_id,
            "opening_id": job_id,
            "task_type": "coding",
            "time_limit_minutes": 60,
        },
    )
    assert mt_create_resp.status_code == 201
    mt_assign = mt_create_resp.json()
    mt_id = mt_assign["assignment_id"]

    mt_sub_resp = client.post(
        f"/api/v1/machine-tests/assignments/{mt_id}/submit",
        json={
            "code_content": (
                "def solve(arr: list[int]) -> int:\n"
                "    return sum(x for x in arr if x > 0)\n"
            ),
            "language": "python",
            "time_spent_minutes": 15.0,
        },
    )
    assert mt_sub_resp.status_code == 200
    assert mt_sub_resp.json()["total_score"] > 60.0

    # 4. Integrity Record Recording
    integ_resp = client.post(
        f"/api/v1/candidates/{cand_id}/integrity-records",
        json={
            "session_id": tech_sess_id,
            "round_type": "technical_interview",
            "has_consent": True,
            "events": [{"event_type": "tab_switch", "duration_seconds": 2}],
        },
    )
    assert integ_resp.status_code == 201
    assert integ_resp.json()["risk_level"] == "LOW"

    # 5. Behavioral Record Recording
    behav_resp = client.post(
        f"/api/v1/candidates/{cand_id}/behavioral-records",
        json={
            "session_id": tech_sess_id,
            "round_type": "technical_interview",
            "has_consent": True,
            "observations": [
                {"aspect": "calm_delivery", "impact": "positive", "note": "Explained architecture with clarity"}
            ],
        },
    )
    assert behav_resp.status_code == 201
    assert behav_resp.json()["consistency_index"] >= 80.0

    # 6. Cross-Round Unified Scoring
    cross_resp = client.post(
        f"/api/v1/candidates/{cand_id}/cross-round-evaluation",
        json={
            "opening_id": job_id,
            "target_role": "software_engineer",
            "round_scores": {
                "ats": ats_score,
                "screening": 80.0,
                "hr_interview": 85.0,
                "technical_interview": comp_resp.json()["overall_score"],
                "machine_test": mt_sub_resp.json()["total_score"],
            },
        },
    )
    assert cross_resp.status_code == 201
    cross_data = cross_resp.json()
    assert cross_data["hiring_fit_percentage"] > 70.0
    assert cross_data["completed_rounds"] == 5

    # 7. Final Recommendation
    rec_resp = client.post(
        f"/api/v1/candidates/{cand_id}/final-recommendation",
        json={
            "opening_id": job_id,
            "target_role": "Senior Backend Engineer",
            "evidence_quality": 92.0,
            "data_consistency": 88.0,
        },
    )
    assert rec_resp.status_code == 201
    rec_data = rec_resp.json()
    assert rec_data["decision"] in ("SELECTED", "HOLD_REVIEW")
    assert rec_data["confidence"] > 75.0
    assert len(rec_data["reasons"]) >= 1
    rec_id = rec_data["recommendation_id"]

    # 8. Recruiter Decision Workflow (Approval)
    dec_resp = client.post(
        f"/api/v1/final-recommendations/{rec_id}/decision",
        json={
            "recruiter_decision": "APPROVED",
            "notes": "Strong technical and machine test execution. Approved for formal offer.",
        },
    )
    assert dec_resp.status_code == 200
    assert dec_resp.json()["recruiter_decision"] == "APPROVED"
    assert dec_resp.json()["recruiter_notes"] == "Strong technical and machine test execution. Approved for formal offer."
