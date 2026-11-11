"""Comprehensive integration tests for Day 24-32 AI Screening subsystem."""

import io
import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from src import database
from src.auth import hash_recruiter_password
from src.main import app
from src.screening_pipeline import ScreeningPipeline
from src.stt_integration import stt_integration
from src.answer_understanding_integration import answer_understanding_integration
from src.screening_scoring_integration import screening_scoring_integration
from src.behavioral_analysis_integration import behavioral_analysis_integration
from src.screening_report_integration import screening_report_integration
from src.conversation_flow_integration import conversation_flow_integration
from src.edge_case_integration import edge_case_integration


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ZECPATH_DB_PATH", str(tmp_path / "day24-32.sqlite3"))

    class DeterministicEmbeddingEngine:
        def encode_many(self, texts):
            return [[1.0, 0.0] for _ in texts]

    monkeypatch.setattr(
        "src.integrated_scoring._embedding_engine",
        lambda: DeterministicEmbeddingEngine(),
    )
    salt, password_hash = hash_recruiter_password("test-password-long-enough")
    database.create_first_recruiter_account(
        "screening-recruiter", salt, password_hash
    )
    with TestClient(app, headers={"Origin": "http://testserver"}) as test_client:
        response = test_client.post(
            "/api/v1/auth/session",
            json={
                "username": "screening-recruiter",
                "password": "test-password-long-enough",
            },
        )
        assert response.status_code == 200
        yield test_client


def create_opening(client, title="Senior Python Developer"):
    response = client.post(
        "/api/v1/openings",
        json={
            "title": title,
            "description": "Looking for Python backend developer with FastAPI and SQL.",
            "required_skills": ["Python", "FastAPI", "SQL"],
            "preferred_skills": ["Docker"],
        },
    )
    assert response.status_code == 201
    return response.json()


def create_candidate(client, opening_id, name="Test Candidate"):
    response = client.post(
        "/api/v1/candidates",
        json={
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@example.test",
            "opening_id": opening_id,
            "skills": ["Python", "SQL"],
        },
    )
    assert response.status_code == 201
    return response.json()


# ==========================================
# Day 24: Speech-to-Text & Transcript Cleaning
# ==========================================

def test_day24_transcript_cleaning():
    """Verify filler removal, punctuation, and repeated word handling."""
    raw = "I um have three years experience in python uh and and django"
    cleaned = stt_integration.clean_transcript(raw)
    assert "um" not in cleaned.lower().split()
    assert "uh" not in cleaned.lower().split()
    assert "and and" not in cleaned.lower()
    assert "python" in cleaned.lower()
    assert "django" in cleaned.lower()


def test_day24_audio_upload_and_mock_transcribe(client):
    """Verify audio upload validation and transcription processing."""
    opening = create_opening(client)
    cand = create_candidate(client, opening["opening_id"])
    
    session_resp = client.post(
        "/api/v1/screening/sessions",
        json={"candidate_id": cand["candidate_id"], "opening_id": opening["opening_id"]},
    )
    assert session_resp.status_code == 201
    session_id = session_resp.json()["session_id"]
    
    # Upload dummy WAV audio
    dummy_wav = b"RIFF" + b"\x00" * 36 + b"WAVEfmt " + b"\x00" * 20 + b"data" + b"\x00" * 100
    upload_resp = client.post(
        f"/api/v1/screening/sessions/{session_id}/audio",
        files={"file": ("response.wav", io.BytesIO(dummy_wav), "audio/wav")},
        data={"question_id": "HR001"},
    )
    assert upload_resp.status_code == 202
    audio_id = upload_resp.json()["audio_id"]
    
    # Check status
    status_resp = client.get(f"/api/v1/screening/audio/{audio_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] in ["PENDING", "COMPLETED"]
    
    # Transcribe audio
    transcribe_resp = client.post(f"/api/v1/screening/audio/{audio_id}/transcribe")
    assert transcribe_resp.status_code == 200
    t_data = transcribe_resp.json()
    assert t_data["audio_id"] == audio_id
    assert "cleaned_text" in t_data


# ==========================================
# Day 25: Answer Intent & Information Extraction
# ==========================================

def test_day25_intent_classification_and_extraction():
    """Verify intent detection and structured entity extraction."""
    # Skill answer
    skill_text = "I have 4 years of experience working with Python and FastAPI."
    result = answer_understanding_integration.engine.understand(
        skill_text,
        expected_intent="skills",
    )
    assert result["intent"] == "skills"
    assert "Python" in result["extracted_information"].get("skills", [])
    assert result["answer_status"] == "valid"
    assert not result["validation"].get("off_topic", False)

    # Off-topic answer
    off_topic = "My favorite hobby is playing games and watching movies."
    result_off = answer_understanding_integration.engine.understand(
        off_topic,
        expected_intent="notice_period",
    )
    assert result_off["validation"].get("off_topic") is True


# ==========================================
# Day 26: Screening Scoring Engine
# ==========================================

def test_day26_scoring_parameters_and_breakdown():
    """Verify clarity, relevance, completeness, consistency scoring."""
    question_text = "What is your experience with SQL and relational databases?"
    answer_text = "I have worked with PostgreSQL and MySQL for 3 years writing complex joins and indexes."
    
    score = screening_scoring_integration.scorer.score_answer(
        question_text=question_text,
        answer_text=answer_text,
        expected_intent="SKILL_EXPERIENCE",
        extracted_data={"skills": ["PostgreSQL", "MySQL"], "experience_years": 3},
    )
    assert 0 <= score.clarity <= 5
    assert 0 <= score.relevance <= 5
    assert 0 <= score.completeness <= 5
    assert 0 <= score.consistency <= 5
    assert 0 <= score.normalized_score <= 100
    assert len(score.explanation) > 0


# ==========================================
# Day 27: Confidence & Sentiment Signal Analysis
# ==========================================

def test_day27_sentiment_and_behavioral_signals():
    """Verify sentiment, hesitation, and contradiction signals."""
    hesitant_text = "Um, I think, well, maybe I worked with AWS once, not sure."
    analysis = behavioral_analysis_integration.analyze_text(hesitant_text, duration_seconds=5)
    assert analysis["hesitation_count"] > 0
    assert analysis["uncertainty_count"] > 0
    
    positive_text = "I successfully led the project, optimized query speeds by 40%, and received great team feedback."
    analysis_pos = behavioral_analysis_integration.analyze_text(positive_text, duration_seconds=10)
    assert analysis_pos["sentiment"] == "POSITIVE"


# ==========================================
# Day 28: AI Screening Report Generator
# ==========================================

def test_day28_screening_report_generation(client):
    """Verify complete recruiter report generation and persistence."""
    opening = create_opening(client)
    cand = create_candidate(client, opening["opening_id"])
    
    pipeline = ScreeningPipeline()
    session_data = pipeline.create_screening_session(
        candidate_id=cand["candidate_id"],
        opening_id=opening["opening_id"],
        language="en",
    )
    session_id = session_data["session"].session_id
    
    # Submit answer
    pipeline.process_text_response(
        session_id=session_id,
        question_id="HR001",
        text_answer="I have 4 years of experience building Python and SQL pipelines.",
    )
    
    # Complete session
    summary = pipeline.complete_session(session_id)
    assert summary["status"] == "COMPLETED"
    assert "report" in summary
    assert summary["overall_score"] >= 0


# ==========================================
# Day 29: AI Conversation Flow State Machine
# ==========================================

def test_day29_conversation_state_flow():
    """Verify conversation flow state machine transitions."""
    from day29_ai_conversation_flow.src.conversation_flow import ConversationFlow
    c_flow = ConversationFlow()
    
    start_res = c_flow.start()
    assert start_res["state"] == "asking"
    assert "message" in start_res
    
    # Handle response
    ans_res = c_flow.process_response("I am a Python developer with 3 years of experience.")
    assert ans_res["action"] in ["continue", "follow_up", "clarify", "ask_question"]


# ==========================================
# Day 30 & 31: Edge Cases & Failure Recovery
# ==========================================

def test_day31_edge_case_audio_and_language_handling():
    """Verify edge case handling for invalid audio and language mixing."""
    # Empty transcript
    empty_handling = edge_case_integration.handle_empty_transcript()
    assert empty_handling["action"] == "PROMPT_AGAIN"
    
    # Background noise / low confidence
    noisy_handling = edge_case_integration.handle_low_confidence()
    assert noisy_handling["action"] == "CLARIFY"


# ==========================================
# Day 32: End-to-End Root API Screening Workflow
# ==========================================

def test_day32_complete_screening_workflow_api(client):
    """Test full integrated screening workflow via root REST API."""
    opening = create_opening(client)
    cand = create_candidate(client, opening["opening_id"])
    
    # 1. Start pipeline session
    start_session = client.post(
        "/api/v1/screening/pipeline/sessions",
        json={"candidate_id": cand["candidate_id"], "opening_id": opening["opening_id"]},
    )
    assert start_session.status_code == 201
    session_id = start_session.json()["session"]["session_id"]
    
    # 2. Check session status
    status_resp = client.get(f"/api/v1/screening/sessions/{session_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["session"]["status"] == "CREATED"
    
    # 3. Start conversation flow
    start_flow = client.post(f"/api/v1/screening/sessions/{session_id}/start")
    assert start_flow.status_code == 200
    
    # 4. Submit text answer
    answer_resp = client.post(
        f"/api/v1/screening/sessions/{session_id}/answers/text",
        data={"question_id": "HR001", "answer_text": "I specialize in Python and FastAPI development."},
    )
    assert answer_resp.status_code == 200, answer_resp.json()
    ans_data = answer_resp.json()
    assert "score" in ans_data
    assert "behavioral" in ans_data
    
    # 5. Complete session
    complete_resp = client.post(f"/api/v1/screening/sessions/{session_id}/complete")
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "COMPLETED"
    
    # 6. Retrieve final report
    report_resp = client.get(f"/api/v1/screening/sessions/{session_id}/report")
    assert report_resp.status_code == 200
    rep_data = report_resp.json()
    assert rep_data["session_id"] == session_id
    assert rep_data["candidate_id"] == cand["candidate_id"]
    assert "report_json" in rep_data
    
    # 7. List candidate reports
    cand_reports = client.get(f"/api/v1/screening/candidates/{cand['candidate_id']}/reports")
    assert cand_reports.status_code == 200
    assert len(cand_reports.json()) >= 1
    
    # 8. Get questions for role
    role_questions = client.get("/api/v1/screening/questions/SOFTWARE_DEVELOPER")
    assert role_questions.status_code == 200
    assert len(role_questions.json()) > 0

