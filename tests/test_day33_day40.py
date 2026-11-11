"""Comprehensive integration tests for Day 33-40 AI HR Interview Subsystem.

Tests encompass:
- Day 33: Role-specific HR question generator & FSM transitions
- Day 34: Dynamic adaptive follow-up logic
- Day 35: Multi-factor communication evaluation & filler analysis
- Day 36: Confidence & behavioral signals with ethical safeguards
- Day 37: Explainable 0-100 HR interview scoring engine
- Day 38: Reasoning & situational judgment aptitude logic
- Day 39: 11-section recruiter report generator & HTML export
- Day 40: End-to-end persona simulation & Human vs AI comparison
- REST API: Complete lifecycle and recruiter decision recording
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from src import database
from src.auth import hash_recruiter_password
from src.main import app
from src.hr_interview_engine import hr_interview_engine, InterviewFlowStateMachine
from src.hr_followup_engine import hr_followup_engine
from src.hr_communication_evaluator import hr_communication_evaluator
from src.hr_confidence_analyzer import hr_confidence_analyzer
from src.hr_scoring_engine import hr_scoring_engine
from src.hr_aptitude_engine import hr_aptitude_engine
from src.hr_summary_generator import hr_summary_generator
from src.hr_simulation_engine import hr_simulation_engine
from src.hr_interview_pipeline import hr_interview_pipeline


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Isolated test client with ephemeral database and authenticated recruiter."""
    db_file = tmp_path / "day33-40.sqlite3"
    monkeypatch.setenv("ZECPATH_DB_PATH", str(db_file))

    class DeterministicEmbeddingEngine:
        def encode_many(self, texts):
            return [[1.0, 0.0] for _ in texts]

    monkeypatch.setattr(
        "src.integrated_scoring._embedding_engine",
        lambda: DeterministicEmbeddingEngine(),
    )

    salt, password_hash = hash_recruiter_password("test-password-long-enough")
    database.create_first_recruiter_account("hr-recruiter", salt, password_hash)

    with TestClient(app, headers={"Origin": "http://testserver"}) as test_client:
        auth_resp = test_client.post(
            "/api/v1/auth/session",
            json={"username": "hr-recruiter", "password": "test-password-long-enough"},
        )
        assert auth_resp.status_code == 200
        yield test_client


def _setup_candidate_and_job():
    """Helper to seed job opening and candidate."""
    opening_id = f"job_{uuid.uuid4().hex[:8]}"
    opening = database.create_opening({
        "opening_id": opening_id,
        "title": "Software Engineer",
        "description": "Python FastAPI backend development",
        "required_skills": ["Python", "FastAPI", "SQL"],
        "preferred_skills": ["Docker", "AWS"],
        "minimum_education": "BACHELORS",
        "minimum_years_experience": 2,
    })
    candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
    candidate = database.create_candidate({
        "candidate_id": candidate_id,
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "opening_id": opening["opening_id"],
        "skills": ["Python", "FastAPI"],
        "resume_text": "Experienced Python developer with FastAPI and SQL expertise.",
    })
    return candidate, opening


def _setup_session():
    """Helper to seed candidate, opening, and an active HR interview session."""
    cand, op = _setup_candidate_and_job()
    created = hr_interview_engine.create_interview_session(
        candidate_id=cand["candidate_id"],
        opening_id=op["opening_id"],
        experience_level="EXPERIENCED",
        role_type="TECHNICAL",
    )
    return cand, op, created["session"], created["questions"]


# ============================================================================
# Day 33 Tests: Question Engine & FSM
# ============================================================================

def test_day33_fresher_vs_experienced_questions():
    """Verifies question differentiation between fresher and experienced candidates."""
    fresher_q = hr_interview_engine.generate_questions("FRESHER", "TECHNICAL")
    exp_q = hr_interview_engine.generate_questions("EXPERIENCED", "TECHNICAL")

    assert len(fresher_q) >= 4
    assert len(exp_q) >= 4

    fresher_texts = " ".join([q["question_text"] for q in fresher_q]).lower()
    exp_texts = " ".join([q["question_text"] for q in exp_q]).lower()

    # Fresher questions emphasize foundational knowledge, projects, learning agility
    assert any(term in fresher_texts for term in ["project", "learn", "academic", "excited", "start"])
    # Experienced questions emphasize past experience, architecture, conflict, leadership
    assert any(term in exp_texts for term in ["experience", "conflict", "difficult", "disagree", "decision", "trade-off"])


def test_day33_technical_vs_non_technical_questions():
    """Verifies question differentiation between technical and non-technical tracks."""
    tech_q = hr_interview_engine.generate_questions("EXPERIENCED", "TECHNICAL")
    nontech_q = hr_interview_engine.generate_questions("EXPERIENCED", "NON_TECHNICAL")

    tech_texts = " ".join([q["question_text"] for q in tech_q]).lower()
    nontech_texts = " ".join([q["question_text"] for q in nontech_q]).lower()

    assert any(term in tech_texts for term in ["technical", "engineering", "system", "code", "architecture"])
    assert any(term in nontech_texts for term in ["stakeholder", "client", "customer", "business", "cross-functional"])


def test_day33_fsm_transitions():
    """Verifies state machine transitions and invalid transition safeguards."""
    fsm = InterviewFlowStateMachine()
    assert fsm.current_phase == "CREATED"

    assert fsm.transition_to("INTRODUCTION") == "INTRODUCTION"
    assert fsm.current_phase == "INTRODUCTION"

    assert fsm.transition_to("CORE_HR_QUESTIONS") == "CORE_HR_QUESTIONS"
    assert fsm.transition_to("ROLE_BASED_EVALUATION") == "ROLE_BASED_EVALUATION"
    assert fsm.transition_to("CLOSING") == "CLOSING"
    assert fsm.transition_to("COMPLETED") == "COMPLETED"
    assert fsm.is_completed() is True

    with pytest.raises(ValueError):
        fsm.transition_to("INVALID_PHASE")


# ============================================================================
# Day 34 Tests: Dynamic Follow-up Engine
# ============================================================================

def test_day34_quality_detection():
    """Verifies candidate response classification (incomplete, vague, complete)."""
    assert hr_followup_engine.detect_response_quality("Yes, sure.") == "incomplete"
    assert hr_followup_engine.detect_response_quality(
        "I kind of maybe do things when they happen."
    ) == "vague"
    assert hr_followup_engine.detect_response_quality(
        "In my previous role as an engineer, when a critical payment microservice failed, "
        "I investigated the root cause, identified a deadlock in the database connection pool, "
        "and applied a connection limit fix that reduced downtime by 98%."
    ) == "complete"


def test_day34_followup_types():
    """Verifies appropriate follow-up generation based on response quality and confidence."""
    cand, op, session, questions = _setup_session()
    interview_id = session["interview_id"]

    # Incomplete response triggers clarification
    clarification = hr_followup_engine.evaluate_and_generate_followup(
        interview_id=interview_id,
        question_id=questions[0]["question_id"],
        question_text=questions[0]["question_text"],
        candidate_response="I solved a bug.",
    )
    assert clarification["needed"] is True
    assert clarification["type"] == "clarification"

    # Vague response triggers example-based follow-up
    vague_resp = "I kind of communicate with people and maybe try to do things."
    example = hr_followup_engine.evaluate_and_generate_followup(
        interview_id=interview_id,
        question_id=questions[1]["question_id"],
        question_text=questions[1]["question_text"],
        candidate_response=vague_resp,
    )
    assert example["needed"] is True
    assert example["type"] == "example_based"


# ============================================================================
# Day 35 Tests: Multi-Factor Communication Evaluation
# ============================================================================

def test_day35_communication_evaluation():
    """Tests evaluation of fluency, grammar, vocabulary, clarity, structure, and fillers."""
    cand, op, session, _ = _setup_session()
    interview_id = session["interview_id"]

    answer = (
        "In my previous project, we adopted a microservices architecture. "
        "Firstly, we identified service boundaries. Secondly, we defined strict gRPC contracts. "
        "Consequently, system throughput improved significantly."
    )
    eval_res = hr_communication_evaluator.evaluate_communication(interview_id, answer)

    assert 0.0 <= eval_res["fluency_score"] <= 100.0
    assert 0.0 <= eval_res["grammar_score"] <= 100.0
    assert 0.0 <= eval_res["vocabulary_score"] <= 100.0
    assert 0.0 <= eval_res["clarity_score"] <= 100.0
    assert 0.0 <= eval_res["structure_score"] <= 100.0
    assert 0.0 <= eval_res["filler_control_score"] <= 100.0
    assert 0.0 <= eval_res["total_communication_score"] <= 100.0

    # Structured answer should have high structure score
    assert eval_res["structure_score"] >= 80.0


def test_day35_filler_detection():
    """Tests filler word penalty calculation."""
    cand, op, session, _ = _setup_session()
    interview_id = session["interview_id"]

    clean_text = "I designed the database schema according to standard third normal form."
    filler_text = "Um, like, I basically, you know, designed the schema, uh, like in 3NF, you know."

    clean_eval = hr_communication_evaluator.evaluate_communication(interview_id, clean_text)
    filler_eval = hr_communication_evaluator.evaluate_communication(interview_id, filler_text)

    assert clean_eval["filler_control_score"] > filler_eval["filler_control_score"]
    assert len(filler_eval["fillers_detected"]) > 0


# ============================================================================
# Day 36 Tests: Confidence & Behavioral Signals
# ============================================================================

def test_day36_confidence_and_disclaimer():
    """Tests hesitation, uncertainty signals, and mandatory ethical disclaimer."""
    cand, op, session, _ = _setup_session()
    interview_id = session["interview_id"]

    hesitant_text = "Um... well, maybe I think... I'm not really sure, perhaps it was my fault..."
    signals = hr_confidence_analyzer.analyze_signals(interview_id, hesitant_text)

    assert signals["hesitation_count"] > 0
    assert signals["uncertainty_count"] > 0
    assert "ethical_disclaimer" in signals
    # Must explicitly state it is not psychological or emotional diagnosis
    assert "not" in signals["ethical_disclaimer"].lower()


def test_day36_contradiction_detection():
    """Tests detection of contradictory statements across turns."""
    cand, op, session, _ = _setup_session()
    interview_id = session["interview_id"]

    prev_answers = [
        {"raw_response": "I have over five years of dedicated experience with Kubernetes and cloud infrastructure."}
    ]
    curr_answer = "I actually have never managed any production clusters or worked with Kubernetes before."

    signals = hr_confidence_analyzer.analyze_signals(
        interview_id,
        curr_answer,
        previous_answers=prev_answers,
    )
    assert len(signals["contradictions_detected"]) > 0


# ============================================================================
# Day 37 Tests: HR Scoring Engine
# ============================================================================

def test_day37_scoring_engine_normalization():
    """Tests 0-100 normalization and configurable weight distribution."""
    score = hr_scoring_engine.calculate_hr_score(
        relevance=85.0,
        communication=90.0,
        confidence=80.0,
        consistency=95.0,
    )
    assert 0.0 <= score["overall_hr_score"] <= 100.0
    # Expected weighted: 85*0.40 + 90*0.25 + 80*0.15 + 95*0.20 = 34 + 22.5 + 12 + 19 = 87.5
    assert abs(score["overall_hr_score"] - 87.5) < 0.1
    assert score["score_status"] in ["EXCELLENT", "STRONG", "MODERATE", "DEVELOPING"]


# ============================================================================
# Day 38 Tests: Reasoning & Situational Judgment Aptitude
# ============================================================================

def test_day38_aptitude_evaluation():
    """Tests multi-dimensional rubric scoring of aptitude answers."""
    questions = hr_aptitude_engine.get_aptitude_questions()
    assert len(questions) >= 4

    answer = (
        "When faced with contradictory stakeholder requirements, I first organize a alignment workshop. "
        "I map out business impact versus technical feasibility on a 2x2 matrix, present the trade-offs "
        "transparently to leadership, and reach a consensus based on core Q3 revenue targets."
    )
    eval_res = hr_aptitude_engine.evaluate_aptitude_answer(
        question_id=questions[0]["question_id"],
        category=questions[0]["category"],
        candidate_answer=answer,
    )

    assert 0.0 <= eval_res["overall_score"] <= 100.0
    assert eval_res["logic_score"] >= 75.0
    assert eval_res["problem_solving_score"] >= 75.0


# ============================================================================
# Day 39 Tests: Interview Summary Generator & HTML Report
# ============================================================================

def test_day39_11_section_summary_and_html():
    """Verifies generation of 11-section recruiter report and HTML export."""
    candidate_meta = {
        "candidate_id": "CAND_99",
        "candidate_name": "Alice Smith",
        "opening_title": "Senior AI Architect",
    }
    session = {
        "interview_id": "INT_99",
        "experience_level": "EXPERIENCED",
        "role_type": "TECHNICAL",
        "status": "COMPLETED",
        "created_at": "2026-11-11T10:00:00",
    }
    score_data = {
        "overall_hr_score": 88.5,
        "relevance_score": 90.0,
        "communication_score": 85.0,
        "confidence_score": 86.0,
        "consistency_score": 92.0,
        "score_status": "STRONG",
        "breakdown": {"weights": {"relevance": 0.4, "communication": 0.25, "confidence": 0.15, "consistency": 0.2}},
    }
    questions = [
        {"question_id": "Q1", "category": "TECHNICAL_ALIGNMENT", "question_text": "Describe your system design process."},
        {"question_id": "Q2", "category": "TEAMWORK", "question_text": "How do you resolve team conflicts?"},
    ]
    responses = [
        {"question_id": "Q1", "raw_response": "I always start with data flow diagrams and scalability requirements."},
        {"question_id": "Q2", "raw_response": "I schedule 1-on-1 conversations to understand differing viewpoints."},
    ]

    report = hr_summary_generator.generate_summary_report(
        session=session,
        candidate=candidate_meta,
        score_data=score_data,
        questions=questions,
        responses=responses,
        comm_evals=[],
        signals=[],
        aptitude_evals=[],
    )

    # 11 required sections check
    required_keys = [
        "interview_details",
        "candidate_summary",
        "performance_breakdown",
        "identified_strengths",
        "areas_for_improvement",
        "teamwork_and_culture",
        "career_alignment",
        "availability_and_expectations",
        "aptitude_assessment",
        "review_flags_and_contradictions",
        "recruiter_review_and_decision",
    ]
    for key in required_keys:
        assert key in report, f"Missing section {key}"

    # Verify HTML generation
    html = hr_summary_generator.generate_html_report(report)
    assert "<!DOCTYPE html>" in html
    assert "ZecPath AI HR Interview Report" in html
    assert "Alice Smith" in html
    assert "Senior AI Architect" in html


# ============================================================================
# Day 40 Tests: Simulation Suite & Human vs AI Comparison
# ============================================================================

def test_day40_candidate_persona_simulations():
    """Tests full simulated interview across contrasting candidate personas."""
    confident_res = hr_simulation_engine.simulate_interview(
        candidate_type="EXPERIENCED",
        role_type="TECHNICAL",
        persona="confident",
    )
    assert confident_res["score"]["overall_hr_score"] >= 80.0
    assert confident_res["report"]["report_json"]["recruiter_review"]["suggested_action"] in [
        "PROCEED_TO_FINAL_ROUND",
        "MANUAL_RECRUITER_REVIEW",
    ]

    hesitant_res = hr_simulation_engine.simulate_interview(
        candidate_type="FRESHER",
        role_type="NON_TECHNICAL",
        persona="hesitant",
    )
    assert hesitant_res["score"]["confidence_score"] < confident_res["score"]["confidence_score"]

    comparison = hr_simulation_engine.compare_human_ai_evaluations(
        ai_score=confident_res["score"]["overall_hr_score"],
        human_score=85.0,
    )
    assert "score_difference" in comparison
    assert "agreement_level" in comparison


# ============================================================================
# REST API Integration Tests: Full HR Interview Lifecycle
# ============================================================================

def test_api_hr_interview_lifecycle(client):
    """Verifies end-to-end REST API workflow for AI HR interviews."""
    candidate, opening = _setup_candidate_and_job()

    # 1. Create session
    create_resp = client.post(
        "/api/v1/hr-interviews",
        json={
            "candidate_id": candidate["candidate_id"],
            "opening_id": opening["opening_id"],
            "experience_level": "EXPERIENCED",
            "role_type": "TECHNICAL",
        },
    )
    assert create_resp.status_code == 201
    session_data = create_resp.json()
    interview_id = session_data["interview_id"]
    assert session_data["status"] == "CREATED"

    # 2. Get questions
    q_resp = client.get(f"/api/v1/hr-interviews/{interview_id}/questions")
    assert q_resp.status_code == 200
    questions = q_resp.json()
    assert len(questions) >= 4
    first_q = questions[0]

    # 3. Start session
    start_resp = client.post(f"/api/v1/hr-interviews/{interview_id}/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "IN_PROGRESS"

    # 4. Submit answer
    ans_resp = client.post(
        f"/api/v1/hr-interviews/{interview_id}/answers",
        json={
            "question_id": first_q["question_id"],
            "answer_text": (
                "In my previous architecture role, I led the migration of a legacy monolithic API "
                "to FastAPI microservices running on AWS EKS. We designed clean domain events with Kafka, "
                "which decreased latency by 45% and handled 10x traffic during high-load sales events."
            ),
        },
    )
    assert ans_resp.status_code == 200
    ans_data = ans_resp.json()
    assert "response" in ans_data
    assert "communication_evaluation" in ans_data
    assert "behavioral_signals" in ans_data

    # 5. Submit adaptive follow-up
    fu_resp = client.post(
        f"/api/v1/hr-interviews/{interview_id}/follow-ups",
        json={
            "parent_question_id": first_q["question_id"],
            "followup_type": "deepening",
            "followup_question": "What unexpected trade-offs arose during the Kafka implementation?",
            "candidate_response": "We had to manage schema versioning tightly using Confluent schema registry.",
        },
    )
    assert fu_resp.status_code == 201

    # 6. Pause and Resume session
    pause_resp = client.post(f"/api/v1/hr-interviews/{interview_id}/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "PAUSED"

    resume_resp = client.post(f"/api/v1/hr-interviews/{interview_id}/resume")
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "IN_PROGRESS"

    # 7. Complete interview
    comp_resp = client.post(f"/api/v1/hr-interviews/{interview_id}/complete")
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert comp_data["status"] == "COMPLETED"
    assert "score" in comp_data
    assert "report" in comp_data

    # 8. Get evaluation
    eval_resp = client.get(f"/api/v1/hr-interviews/{interview_id}/evaluation")
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["score"]["overall_hr_score"] > 0

    # 9. Get report (JSON and HTML)
    report_json_resp = client.get(f"/api/v1/hr-interviews/{interview_id}/report")
    assert report_json_resp.status_code == 200
    assert "report_json" in report_json_resp.json()

    report_html_resp = client.get(f"/api/v1/hr-interviews/{interview_id}/report?format=html")
    assert report_html_resp.status_code == 200
    assert "text/html" in report_html_resp.headers["content-type"]
    assert "<!DOCTYPE html>" in report_html_resp.text

    # 10. Record recruiter decision
    dec_resp = client.post(
        f"/api/v1/hr-interviews/{interview_id}/decision",
        json={
            "decision": "PROCEED",
            "notes": "Candidate demonstrated stellar system architecture expertise and clear communication.",
        },
    )
    assert dec_resp.status_code == 200
    assert dec_resp.json()["recruiter_decision"] == "PROCEED"

    # 11. List candidate reports
    cand_reports_resp = client.get(f"/api/v1/hr-interviews/candidates/{candidate['candidate_id']}/reports")
    assert cand_reports_resp.status_code == 200
    assert len(cand_reports_resp.json()) >= 1
