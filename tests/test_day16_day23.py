import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from jsonschema import Draft202012Validator

from src import database
from src.ats_evaluation import binary_metrics, load_reviewed_pairs
from src.auth import hash_recruiter_password
from src.job_description_parser import parse_job_description
from src.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ZECPATH_DB_PATH", str(tmp_path / "day16-23.sqlite3"))

    class DeterministicEmbeddingEngine:
        def encode_many(self, texts):
            return [[1.0, 0.0] for _ in texts]

    monkeypatch.setattr(
        "src.integrated_scoring._embedding_engine",
        lambda: DeterministicEmbeddingEngine(),
    )
    salt, password_hash = hash_recruiter_password("test-password-long-enough")
    database.create_first_recruiter_account(
        "test-recruiter", salt, password_hash
    )
    with TestClient(app, headers={"Origin": "http://testserver"}) as test_client:
        response = test_client.post(
            "/api/v1/auth/session",
            json={
                "username": "test-recruiter",
                "password": "test-password-long-enough",
            },
        )
        assert response.status_code == 200
        yield test_client


def create_opening(client, title="Data Analyst"):
    response = client.post(
        "/api/v1/openings",
        json={
            "title": title,
            "description": "Analyze business data.",
            "required_skills": ["Python", "SQL"],
            "preferred_skills": [],
        },
    )
    assert response.status_code == 201
    return response.json()


def create_candidate(client, opening_id, skills=None, **extra):
    response = client.post(
        "/api/v1/candidates",
        json={
            "name": "Synthetic Candidate",
            "opening_id": opening_id,
            "skills": skills or [],
            **extra,
        },
    )
    assert response.status_code == 201
    return response.json()


def configure_eligibility(client, opening_id, **overrides):
    configuration = {
        "minimum_ats_score": 0,
        "mandatory_skills": ["Python"],
        "location_rules": {},
        "decision_policy": {"manual_review_on_missing_data": True},
    }
    configuration.update(overrides)
    return client.put(
        f"/api/v1/openings/{opening_id}/eligibility-config",
        json=configuration,
    )


def test_eligibility_uses_current_ats_score_and_re_evaluates_after_change(client):
    opening = create_opening(client)
    candidate = create_candidate(client, opening["opening_id"], ["Python", "SQL"])
    configured = configure_eligibility(client, opening["opening_id"])
    assert configured.status_code == 200
    assert configured.json()["version"] == 1

    scored = client.post(
        "/api/v1/candidates/score",
        json={
            "candidate_id": candidate["candidate_id"],
            "job_id": opening["opening_id"],
        },
    )
    assert scored.status_code == 200
    assert scored.json()["evidence"]["scored_at"]

    evaluated = client.post(
        f"/api/v1/candidates/{candidate['candidate_id']}/eligibility/evaluate",
        json={"opening_id": opening["opening_id"]},
    )
    assert evaluated.status_code == 201
    result = evaluated.json()
    assert result["status"] == "ELIGIBLE"
    assert result["mandatory_skills_matched"] == ["Python"]
    assert result["human_review_required"] is True

    latest = client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}/eligibility",
        params={"opening_id": opening["opening_id"]},
    )
    assert latest.status_code == 200
    assert latest.json()["evaluation_id"] == result["evaluation_id"]

    updated = client.patch(
        f"/api/v1/candidates/{candidate['candidate_id']}",
        json={"skills": []},
    )
    assert updated.status_code == 200
    refreshed = client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}/eligibility",
        params={"opening_id": opening["opening_id"]},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["evaluation_id"] != result["evaluation_id"]
    assert refreshed.json()["status"] == "REVIEW"
    assert "A current ATS score is unavailable." in refreshed.json()["missing_information"]


def test_eligibility_rejects_only_explicit_failed_threshold_and_checks_ownership(client):
    opening = create_opening(client)
    candidate = create_candidate(client, opening["opening_id"], ["Python"])
    second_opening = create_opening(client, "Software Developer")
    assert configure_eligibility(
        client,
        opening["opening_id"],
        minimum_ats_score=100,
        mandatory_skills=["Python"],
    ).status_code == 200
    assert configure_eligibility(client, second_opening["opening_id"]).status_code == 200

    assert client.post(
        f"/api/v1/candidates/{candidate['candidate_id']}/eligibility/evaluate",
        json={"opening_id": second_opening["opening_id"]},
    ).status_code == 409
    assert client.post(
        "/api/v1/candidates/score",
        json={
            "candidate_id": candidate["candidate_id"],
            "job_id": opening["opening_id"],
        },
    ).status_code == 200
    result = client.post(
        f"/api/v1/candidates/{candidate['candidate_id']}/eligibility/evaluate",
        json={"opening_id": opening["opening_id"]},
    )
    assert result.status_code == 201
    assert result.json()["status"] == "REJECTED"
    assert result.json()["rules"]["minimum_ats_score"]["status"] == "FAIL"


def test_eligibility_configuration_validation_and_authentication(client):
    opening = create_opening(client)
    response = client.put(
        f"/api/v1/openings/{opening['opening_id']}/eligibility-config",
        json={
            "minimum_experience_years": 5,
            "maximum_experience_years": 2,
            "location_rules": {},
        },
    )
    assert response.status_code == 422
    assert TestClient(app).get(
        f"/api/v1/openings/{opening['opening_id']}/eligibility-config"
    ).status_code == 401


def test_screening_question_bank_filters_and_pending_translations(client):
    all_questions = client.get(
        "/api/v1/screening/questions",
        params={"role_id": "DATA_ANALYST", "language": "en"},
    )
    assert all_questions.status_code == 200
    assert len(all_questions.json()) == 10

    salary = client.get(
        "/api/v1/screening/questions",
        params={
            "role_id": "DATA_ANALYST",
            "category": "salary",
            "language": "en",
        },
    )
    assert salary.status_code == 200
    assert len(salary.json()) == 1
    assert salary.json()[0]["mandatory"] is False
    assert salary.json()[0]["scoring_importance"] == "INFORMATIONAL"

    translated = client.get(
        "/api/v1/screening/questions",
        params={"role_id": "DATA_ANALYST", "language": "ml"},
    )
    assert {item["question_id"] for item in translated.json()} == {"HR001", "HR006"}
    assert client.get(
        "/api/v1/screening/questions", params={"language": "fr"}
    ).status_code == 422


def test_transcript_session_lifecycle_and_persistence(client):
    opening = create_opening(client)
    candidate = create_candidate(client, opening["opening_id"])
    created = client.post(
        "/api/v1/screening/sessions",
        json={
            "candidate_id": candidate["candidate_id"],
            "opening_id": opening["opening_id"],
            "language": "en",
            "source": "MANUAL",
        },
    )
    assert created.status_code == 201
    session_id = created.json()["session_id"]
    assert client.post(
        f"/api/v1/screening/sessions/{session_id}/segments",
        json=[{"speaker": "CANDIDATE", "text": "Hi", "sequence_number": 1}],
    ).status_code == 409
    assert client.patch(
        f"/api/v1/screening/sessions/{session_id}",
        json={"status": "IN_PROGRESS"},
    ).status_code == 200

    segments = client.post(
        f"/api/v1/screening/sessions/{session_id}/segments",
        json=[
            {
                "segment_id": "SEG-1",
                "question_id": "HR001",
                "speaker": "RECRUITER",
                "text": "Please introduce yourself.",
                "sequence_number": 1,
            },
            {
                "segment_id": "SEG-2",
                "question_id": "HR001",
                "speaker": "CANDIDATE",
                "text": "  I build   data products. ",
                "sequence_number": 2,
            },
        ],
    )
    assert segments.status_code == 201
    assert segments.json()[0]["segment_id"] == "SEG-1"
    assert segments.json()[1]["raw_text"] == "  I build   data products. "
    assert segments.json()[1]["normalized_text"] == "I build data products."
    assert segments.json()[1]["confidence"] is None

    interaction = client.post(
        f"/api/v1/screening/sessions/{session_id}/interactions",
        json={
            "question_id": "HR001",
            "validation_status": "UNANSWERED",
            "display_order": 1,
        },
    )
    assert interaction.status_code == 201
    assert interaction.json()["candidate_answer"] is None
    assert client.patch(
        f"/api/v1/screening/sessions/{session_id}",
        json={"status": "INTERRUPTED"},
    ).status_code == 200
    assert client.patch(
        f"/api/v1/screening/sessions/{session_id}",
        json={"status": "IN_PROGRESS"},
    ).status_code == 200
    completed = client.patch(
        f"/api/v1/screening/sessions/{session_id}",
        json={"status": "COMPLETED"},
    )
    assert completed.status_code == 200
    assert completed.json()["completed_at"] is not None
    transcript = client.get(f"/api/v1/screening/sessions/{session_id}")
    assert transcript.status_code == 200
    assert len(transcript.json()["segments"]) == 2
    assert len(transcript.json()["interactions"]) == 1
    assert TestClient(app).get(
        f"/api/v1/screening/sessions/{session_id}"
    ).status_code == 401


def test_transcript_validation_and_candidate_job_binding(client):
    opening = create_opening(client)
    other_opening = create_opening(client, "Backend Developer")
    candidate = create_candidate(client, opening["opening_id"])
    assert client.post(
        "/api/v1/screening/sessions",
        json={
            "candidate_id": candidate["candidate_id"],
            "opening_id": other_opening["opening_id"],
        },
    ).status_code == 409
    session = client.post(
        "/api/v1/screening/sessions",
        json={
            "candidate_id": candidate["candidate_id"],
            "opening_id": opening["opening_id"],
        },
    ).json()
    session_id = session["session_id"]
    client.patch(
        f"/api/v1/screening/sessions/{session_id}",
        json={"status": "IN_PROGRESS"},
    )
    invalid = client.post(
        f"/api/v1/screening/sessions/{session_id}/segments",
        json=[
            {
                "question_id": "UNKNOWN",
                "speaker": "CANDIDATE",
                "text": "Answer",
                "sequence_number": 1,
            }
        ],
    )
    assert invalid.status_code == 422
    invalid_speaker = client.post(
        f"/api/v1/screening/sessions/{session_id}/segments",
        json=[
            {
                "speaker": "UNKNOWN",
                "text": "Answer",
                "sequence_number": 1,
            }
        ],
    )
    assert invalid_speaker.status_code == 422
    invalid_timestamp = client.post(
        f"/api/v1/screening/sessions/{session_id}/segments",
        json=[
            {
                "speaker": "CANDIDATE",
                "text": "Answer",
                "start_time": "2026-01-01T10:00:00",
                "sequence_number": 1,
            }
        ],
    )
    assert invalid_timestamp.status_code == 422
    first = client.post(
        f"/api/v1/screening/sessions/{session_id}/segments",
        json=[
            {
                "segment_id": "SEG-1",
                "speaker": "CANDIDATE",
                "text": "Answer",
                "sequence_number": 1,
            }
        ],
    )
    assert first.status_code == 201
    duplicate = client.post(
        f"/api/v1/screening/sessions/{session_id}/segments",
        json=[
            {
                "segment_id": "SEG-2",
                "speaker": "CANDIDATE",
                "text": "Another answer",
                "sequence_number": 1,
            }
        ],
    )
    assert duplicate.status_code == 409
    out_of_order = client.post(
        f"/api/v1/screening/sessions/{session_id}/segments",
        json=[
            {
                "segment_id": "SEG-3",
                "speaker": "CANDIDATE",
                "text": "Later",
                "sequence_number": 2,
            },
            {
                "segment_id": "SEG-4",
                "speaker": "CANDIDATE",
                "text": "Earlier",
                "sequence_number": 1,
            },
        ],
    )
    assert out_of_order.status_code == 422


def test_job_description_parser_requires_explicit_sections():
    parsed = parse_job_description(
        "Required skills: Python, SQL\n"
        "Preferred skills:\nTableau\n"
        "Experience: 3-5 years\n"
        "Education: Bachelor's degree\n"
        "Responsibilities:\nBuild reports"
    )
    assert parsed["required_skills"] == ["Python", "SQL"]
    assert parsed["preferred_skills"] == ["Tableau"]
    assert parsed["minimum_years_experience"] == 3.0
    assert parsed["minimum_education"] == "Bachelor's degree"
    assert parsed["human_confirmation_required"] is True
    assert parsed["evidence"]["responsibilities"] == ["Build reports"]

    unstructured = parse_job_description(
        "Seeking a Python analyst with five years of experience."
    )
    assert unstructured["required_skills"] == []
    assert unstructured["minimum_years_experience"] is None
    assert unstructured["warnings"]
    assert unstructured["human_confirmation_required"] is True


def test_ats_metrics_only_accept_aligned_reviewed_examples(tmp_path):
    assert binary_metrics(
        [True, False, True, False],
        [True, True, False, False],
    ) == {
        "sample_count": 4,
        "precision": 0.5,
        "recall": 0.5,
        "f1": 0.5,
        "accuracy": 0.5,
        "confusion_matrix": {
            "true_positive": 1,
            "false_positive": 1,
            "false_negative": 1,
            "true_negative": 1,
        },
    }
    with pytest.raises(ValueError):
        binary_metrics([], [])
    review_file = tmp_path / "reviews.csv"
    review_file.write_text(
        "review_status,expected_match,predicted_match\n"
        "PENDING,true,false\n"
        "REVIEWED,true,true\n"
        "REVIEWED,unknown,false\n",
        encoding="utf-8",
    )
    assert load_reviewed_pairs(review_file) == [
        {
            "review_status": "REVIEWED",
            "expected_match": "true",
            "predicted_match": "true",
        }
    ]


def test_root_day16_to_day23_workflow_with_synthetic_resume(client):
    parsed_jd = client.post(
        "/api/v1/openings/parse-description",
        json={
            "description": (
                "Required skills: Python, SQL\n"
                "Preferred skills: Tableau\n"
                "Experience: 2+ years\n"
                "Education: Bachelor's degree"
            )
        },
    )
    assert parsed_jd.status_code == 200
    parsed = parsed_jd.json()
    assert parsed["required_skills"] == ["Python", "SQL"]
    assert parsed["human_confirmation_required"] is True

    opening_response = client.post(
        "/api/v1/openings",
        json={
            "title": "Data Analyst",
            "description": "Analyze synthetic business data.",
            "required_skills": parsed["required_skills"],
            "preferred_skills": parsed["preferred_skills"],
            "minimum_education": parsed["minimum_education"],
            "minimum_years_experience": parsed["minimum_years_experience"],
        },
    )
    assert opening_response.status_code == 201
    opening = opening_response.json()
    candidate_response = client.post(
        "/api/v1/candidates",
        json={
            "name": "Synthetic Candidate",
            "opening_id": opening["opening_id"],
        },
    )
    assert candidate_response.status_code == 201
    candidate = candidate_response.json()

    resume = (
        "Synthetic Candidate\n"
        "Skills\nPython, SQL, Tableau\n"
        "Experience\nData Analyst at Synthetic Example from 2021 to 2024\n"
        "Education\nBachelor of Science\n"
    )
    upload = client.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": candidate["candidate_id"]},
        files={"file": ("synthetic_resume.txt", resume, "text/plain")},
    )
    assert upload.status_code == 202
    job = client.get(f"/api/v1/jobs/{upload.json()['job_id']}")
    assert job.status_code == 200
    assert job.json()["status"] == "COMPLETED"
    parsed_resume = client.post(
        "/api/v1/resumes/parse",
        json={"job_id": upload.json()["job_id"]},
    )
    assert parsed_resume.status_code == 200
    assert "Python" in parsed_resume.json()["parsed_text"]

    score = client.post(
        "/api/v1/candidates/score",
        json={
            "job_id": opening["opening_id"],
            "candidate_id": candidate["candidate_id"],
        },
    )
    assert score.status_code == 200
    assert score.json()["human_review_required"] is True
    assert score.json()["evidence"]["scoring_version"] == "day9-12-13-v1"
    shortlist = client.post(
        f"/api/v1/openings/{opening['opening_id']}/shortlist",
        json={"minimum_score": 0},
    )
    assert shortlist.status_code == 200
    assert shortlist.json()["candidates"][0]["candidate_id"] == candidate["candidate_id"]
    assert shortlist.json()["human_review_required"] is True

    configured = client.put(
        f"/api/v1/openings/{opening['opening_id']}/eligibility-config",
        json={
            "minimum_ats_score": 0,
            "mandatory_skills": ["Python"],
            "location_rules": {},
            "decision_policy": {"manual_review_on_missing_data": True},
        },
    )
    assert configured.status_code == 200
    evaluated = client.post(
        f"/api/v1/candidates/{candidate['candidate_id']}/eligibility/evaluate",
        json={"opening_id": opening["opening_id"]},
    )
    assert evaluated.status_code == 201
    assert evaluated.json()["status"] == "ELIGIBLE"
    assert evaluated.json()["human_review_required"] is True
    retrieved = client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}/eligibility",
        params={"opening_id": opening["opening_id"]},
    )
    assert retrieved.json()["evaluation_id"] == evaluated.json()["evaluation_id"]

    questions = client.get(
        "/api/v1/screening/questions",
        params={"role_id": "DATA_ANALYST", "language": "en"},
    )
    assert questions.status_code == 200
    schema_dir = Path(__file__).resolve().parents[1] / "docs" / "schemas"
    assert questions.json()[0]["question_id"] == "HR001"

    session = client.post(
        "/api/v1/screening/sessions",
        json={
            "candidate_id": candidate["candidate_id"],
            "opening_id": opening["opening_id"],
        },
    )
    assert session.status_code == 201
    session_id = session.json()["session_id"]
    assert client.patch(
        f"/api/v1/screening/sessions/{session_id}",
        json={"status": "IN_PROGRESS"},
    ).status_code == 200
    assert client.post(
        f"/api/v1/screening/sessions/{session_id}/interactions",
        json={
            "question_id": "HR001",
            "candidate_answer": "I use Python for analysis.",
            "validation_status": "VALID",
            "display_order": 1,
        },
    ).status_code == 201
    assert client.post(
        f"/api/v1/screening/sessions/{session_id}/segments",
        json=[
            {
                "question_id": "HR001",
                "speaker": "CANDIDATE",
                "text": "I use Python for analysis.",
                "sequence_number": 1,
            }
        ],
    ).status_code == 201
    transcript = client.get(
        f"/api/v1/screening/sessions/{session_id}"
    )
    assert transcript.status_code == 200
    transcript_schema = json.loads(
        (schema_dir / "screening_transcript.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(transcript_schema).validate(transcript.json())
