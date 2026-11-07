import base64
from io import BytesIO

import pytest
from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from src import database
from src import create_recruiter, reset_recruiter
from src.auth import hash_recruiter_password, verify_recruiter_credentials
from src.main import app
from src.jobs import create_job, update_job


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ZECPATH_DB_PATH", str(tmp_path / "ats.sqlite3"))
    class DeterministicEmbeddingEngine:
        def encode_many(self, texts):
            return [[1.0, 0.0] for _ in texts]

    monkeypatch.setattr(
        "src.integrated_scoring._embedding_engine",
        lambda: DeterministicEmbeddingEngine(),
    )
    password = "test-password-long-enough"
    salt, password_hash = hash_recruiter_password(password)
    database.create_first_recruiter_account("demo-recruiter", salt, password_hash)
    with TestClient(app, headers={"Origin": "http://testserver"}) as test_client:
        login = test_client.post(
            "/api/v1/auth/session",
            json={"username": "demo-recruiter", "password": password},
        )
        assert login.status_code == 200
        yield test_client


def create_opening(client, **overrides):
    payload = {
        "title": "Data Analyst",
        "description": "Analyze business data.",
        "required_skills": ["Python", "SQL", "Excel"],
        "preferred_skills": ["Power BI"],
    }
    payload.update(overrides)
    response = client.post("/api/v1/openings", json=payload)
    assert response.status_code == 201
    return response.json()


def create_candidate(client, opening_id, **overrides):
    payload = {
        "name": "Demo Candidate",
        "email": "candidate@example.test",
        "opening_id": opening_id,
        "skills": [],
        "resume_text": "",
    }
    payload.update(overrides)
    response = client.post("/api/v1/candidates", json=payload)
    assert response.status_code == 201
    return response.json()


def test_root_and_health(client):
    root = client.get("/")
    assert root.status_code == 200
    assert "Zecpath AI Hiring System" in root.text
    assert 'const api = "/api/v1";' in root.text
    assert 'href="/docs"' in root.text
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["authentication_configured"] is True
    assert TestClient(app).get("/api/v1/health").status_code == 200
    unauthenticated_session = TestClient(app).get("/api/v1/auth/session")
    assert unauthenticated_session.status_code == 200
    assert unauthenticated_session.json()["authenticated"] is False


def test_existing_database_is_migrated_for_structured_resume_and_job_requirements(
    tmp_path, monkeypatch
):
    database_path = tmp_path / "legacy.sqlite3"
    connection = database.sqlite3.connect(database_path)
    connection.executescript(
        """
        CREATE TABLE openings (
            opening_id TEXT PRIMARY KEY, title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '', required_skills TEXT NOT NULL,
            preferred_skills TEXT NOT NULL, status TEXT NOT NULL,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE candidates (
            candidate_id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT,
            opening_id TEXT NOT NULL, skills TEXT NOT NULL,
            resume_text TEXT NOT NULL DEFAULT '', resume_filename TEXT,
            application_status TEXT NOT NULL, score REAL, score_evidence TEXT,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        """
    )
    connection.close()
    monkeypatch.setenv("ZECPATH_DB_PATH", str(database_path))

    database.initialize_database()
    opening = database.create_opening(
        {
            "opening_id": "legacy-opening",
            "title": "Analyst",
            "description": "",
            "required_skills": ["Python"],
            "preferred_skills": [],
        }
    )
    candidate = database.create_candidate(
        {
            "candidate_id": "legacy-candidate",
            "name": "Legacy Applicant",
            "opening_id": "legacy-opening",
        }
    )
    assert opening["minimum_education"] is None
    assert opening["minimum_years_experience"] is None
    assert candidate["resume_data"] == {}


def test_job_and_candidate_crud_and_persistence(client, tmp_path):
    opening = create_opening(client)
    edited_opening = client.patch(
        f"/api/v1/openings/{opening['opening_id']}",
        json={
            "title": "Senior Data Analyst",
            "description": "Analyze and explain business data.",
            "preferred_skills": ["Power BI", "Tableau"],
        },
    )
    assert edited_opening.status_code == 200
    assert edited_opening.json()["title"] == "Senior Data Analyst"
    assert edited_opening.json()["preferred_skills"] == ["Power BI", "Tableau"]

    candidate = create_candidate(
        client,
        opening["opening_id"],
        skills=["Python", "SQL"],
    )
    candidate_id = candidate["candidate_id"]

    updated = client.patch(
        f"/api/v1/candidates/{candidate_id}",
        json={
            "name": "Edited Demo Candidate",
            "email": "EDITED@example.test",
            "skills": ["Python", "SQL", "Git"],
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Edited Demo Candidate"
    assert updated.json()["email"] == "edited@example.test"
    assert updated.json()["skills"] == ["Python", "SQL", "Git"]

    updated = client.patch(
        f"/api/v1/candidates/{candidate_id}",
        json={"application_status": "IN_REVIEW"},
    )
    assert updated.status_code == 200
    assert updated.json()["application_status"] == "IN_REVIEW"
    assert client.get("/api/v1/candidates", params={"opening_id": opening["opening_id"]}).json()[0]["candidate_id"] == candidate_id

    database_path = tmp_path / "ats.sqlite3"
    with TestClient(app, headers=client.headers) as restarted_client:
        restarted_client.cookies.update(client.cookies)
        assert restarted_client.get(f"/api/v1/candidates/{candidate_id}").status_code == 200
        assert restarted_client.get(f"/api/v1/openings/{opening['opening_id']}").status_code == 200

    closed = client.patch(
        f"/api/v1/openings/{opening['opening_id']}",
        json={"status": "CLOSED"},
    )
    assert closed.status_code == 200
    assert client.post(
        "/api/v1/candidates",
        json={
            "name": "Blocked Applicant",
            "opening_id": opening["opening_id"],
        },
    ).status_code == 409

    assert client.delete(f"/api/v1/candidates/{candidate_id}").status_code == 204
    assert client.get(f"/api/v1/candidates/{candidate_id}").status_code == 404
    assert client.delete(f"/api/v1/openings/{opening['opening_id']}").status_code == 204
    assert client.get(f"/api/v1/openings/{opening['opening_id']}").status_code == 404
    assert database_path.exists()


def test_score_uses_saved_candidate_and_job_evidence(client):
    opening = create_opening(client)
    candidate = create_candidate(
        client,
        opening["opening_id"],
        resume_text="Python SQL project with team dashboards.",
    )

    response = client.post(
        "/api/v1/candidates/score",
        json={
            "job_id": opening["opening_id"],
            "candidate_id": candidate["candidate_id"],
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["score"] == pytest.approx(53.33, abs=0.01)
    assert result["evidence"]["matched_required_skills"] == ["Python", "SQL"]
    assert result["evidence"]["missing_required_skills"] == ["Excel"]
    assert result["job_title"] == "Data Analyst"
    assert result["candidate_name"] == "Demo Candidate"
    assert result["matching_required_skills"] == ["Python", "SQL"]
    assert result["ranking"] == 1
    assert result["components"]["semantic_similarity"]["score"] == 1.0
    assert result["components"]["education_alignment"]["score"] is None
    assert result["human_review_required"] is True
    assert client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).json()["score"] == result["score"]
    with TestClient(app, headers=client.headers) as restarted_client:
        restarted_client.cookies.update(client.cookies)
        persisted_candidate = restarted_client.get(
            f"/api/v1/candidates/{candidate['candidate_id']}"
        ).json()
        assert persisted_candidate["score"] == result["score"]
        assert persisted_candidate["score_evidence"] == result["evidence"]


def test_semantic_embedding_uses_job_requirements_and_description(
    client, monkeypatch
):
    opening = create_opening(
        client,
        description="Build financial forecasting dashboards.",
        required_skills=["Python", "Financial modeling"],
        preferred_skills=["Power BI"],
        minimum_education="Bachelor",
        minimum_years_experience=3,
    )
    candidate = create_candidate(
        client,
        opening["opening_id"],
        resume_text="Python resume with financial modeling experience.",
    )
    captured_texts = []

    class CapturingEmbeddingEngine:
        def encode_many(self, texts):
            captured_texts.extend(texts)
            return [[1.0, 0.0] for _ in texts]

    monkeypatch.setattr(
        "src.integrated_scoring._embedding_engine",
        lambda: CapturingEmbeddingEngine(),
    )
    response = client.post(
        "/api/v1/candidates/score",
        json={
            "job_id": opening["opening_id"],
            "candidate_id": candidate["candidate_id"],
        },
    )

    assert response.status_code == 200
    assert captured_texts[0] == candidate["resume_text"]
    job_text = captured_texts[1]
    for requirement in (
        opening["title"],
        opening["description"],
        "Python",
        "Financial modeling",
        "Power BI",
        "Bachelor",
        "3",
    ):
        assert requirement in job_text


def test_score_rejects_missing_evidence_and_wrong_job(client):
    opening = create_opening(client)
    other_opening = create_opening(client, title="Another Role")
    candidate = create_candidate(client, opening["opening_id"])

    assert client.post(
        "/api/v1/candidates/score",
        json={
            "job_id": opening["opening_id"],
            "candidate_id": candidate["candidate_id"],
        },
    ).status_code == 422
    assert client.post(
        "/api/v1/candidates/score",
        json={
            "job_id": other_opening["opening_id"],
            "candidate_id": candidate["candidate_id"],
        },
    ).status_code == 409


def test_score_without_resume_reports_semantic_component_as_unavailable(client):
    opening = create_opening(client)
    candidate = create_candidate(
        client,
        opening["opening_id"],
        skills=["Python"],
    )
    response = client.post(
        "/api/v1/candidates/score",
        json={
            "job_id": opening["opening_id"],
            "candidate_id": candidate["candidate_id"],
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["score"] == pytest.approx(11.67, abs=0.01)
    assert result["extracted_skills"] == []
    assert result["evidence"]["scoring_skills"] == ["Python"]
    assert result["components"]["semantic_similarity"]["score"] is None
    assert "readable resume is required" in result["components"]["semantic_similarity"]["reason"]


def test_score_returns_service_unavailable_when_local_model_is_missing(
    client, monkeypatch
):
    opening = create_opening(client)
    candidate = create_candidate(
        client,
        opening["opening_id"],
        resume_text="Python analyst resume.",
    )

    def unavailable_model():
        raise ImportError("model not available")

    monkeypatch.setattr("src.integrated_scoring._embedding_engine", unavailable_model)
    response = client.post(
        "/api/v1/candidates/score",
        json={
            "job_id": opening["opening_id"],
            "candidate_id": candidate["candidate_id"],
        },
    )
    assert response.status_code == 503
    assert "Day 12 semantic scoring is unavailable" in response.json()["detail"]
    assert client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).json()["score"] is None


def test_score_is_invalidated_when_its_inputs_change(client):
    opening = create_opening(client)
    candidate = create_candidate(
        client,
        opening["opening_id"],
        skills=["Python", "SQL", "Excel"],
    )
    score_url = "/api/v1/candidates/score"
    score_request = {
        "job_id": opening["opening_id"],
        "candidate_id": candidate["candidate_id"],
    }

    initial_score = client.post(score_url, json=score_request)
    assert initial_score.status_code == 200
    assert initial_score.json()["score"] == 35

    updated_candidate = client.patch(
        f"/api/v1/candidates/{candidate['candidate_id']}",
        json={"skills": ["Python"]},
    )
    assert updated_candidate.status_code == 200
    assert updated_candidate.json()["score"] is None
    assert updated_candidate.json()["score_evidence"] is None

    rescored_candidate = client.post(score_url, json=score_request)
    assert rescored_candidate.status_code == 200
    assert rescored_candidate.json()["score"] == pytest.approx(11.67, abs=0.01)

    updated_opening = client.patch(
        f"/api/v1/openings/{opening['opening_id']}",
        json={"required_skills": ["Python", "SQL"]},
    )
    assert updated_opening.status_code == 200
    candidate_after_job_edit = client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).json()
    assert candidate_after_job_edit["score"] is None
    assert candidate_after_job_edit["score_evidence"] is None

    rescored_candidate = client.post(score_url, json=score_request)
    assert rescored_candidate.status_code == 200
    assert rescored_candidate.json()["score"] == pytest.approx(17.5, abs=0.01)

    resume = client.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": candidate["candidate_id"]},
        files={"file": ("updated.txt", b"Python SQL", "text/plain")},
    )
    assert resume.status_code == 202
    candidate_after_resume = client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).json()
    assert candidate_after_resume["score"] is None
    assert candidate_after_resume["score_evidence"] is None


def test_score_is_invalidated_when_scoring_evidence_changes(client):
    opening = create_opening(client)
    candidate = create_candidate(
        client,
        opening["opening_id"],
        skills=["Python", "SQL", "Excel"],
    )
    score_request = {
        "job_id": opening["opening_id"],
        "candidate_id": candidate["candidate_id"],
    }
    initial_score = client.post("/api/v1/candidates/score", json=score_request)
    assert initial_score.status_code == 200
    expected_score = initial_score.json()["score"]
    expected_evidence = initial_score.json()["evidence"]

    updated_candidate = client.patch(
        f"/api/v1/candidates/{candidate['candidate_id']}",
        json={
            "name": "Renamed Candidate",
            "email": "renamed@example.test",
            "skills": ["Python", "SQL", "Excel"],
        },
    )
    assert updated_candidate.status_code == 200
    assert updated_candidate.json()["score"] is None
    assert updated_candidate.json()["score_evidence"] is None
    rescored = client.post("/api/v1/candidates/score", json=score_request)
    assert rescored.status_code == 200
    expected_score = rescored.json()["score"]
    expected_evidence = rescored.json()["evidence"]

    updated_opening = client.patch(
        f"/api/v1/openings/{opening['opening_id']}",
        json={
            "title": "Senior Data Analyst",
            "description": "Updated role description.",
            "required_skills": ["Python", "SQL", "Excel"],
            "preferred_skills": ["Tableau"],
            "status": "CLOSED",
        },
    )
    assert updated_opening.status_code == 200
    persisted_candidate = client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).json()
    assert persisted_candidate["score"] is None
    assert persisted_candidate["score_evidence"] is None

    rescored = client.post("/api/v1/candidates/score", json=score_request)
    assert rescored.status_code == 200
    expected_score = rescored.json()["score"]
    expected_evidence = rescored.json()["evidence"]
    updated_opening = client.patch(
        f"/api/v1/openings/{opening['opening_id']}",
        json={"status": "CLOSED"},
    )
    assert updated_opening.status_code == 200
    candidate_after_status_change = client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).json()
    assert candidate_after_status_change["score"] == expected_score
    assert candidate_after_status_change["score_evidence"] == expected_evidence


def test_patch_rejects_null_for_required_fields(client):
    opening = create_opening(client)
    candidate = create_candidate(client, opening["opening_id"])

    for field in ("title", "description", "required_skills", "preferred_skills", "status"):
        assert client.patch(
            f"/api/v1/openings/{opening['opening_id']}",
            json={field: None},
        ).status_code == 422

    for field in ("name", "skills", "application_status"):
        assert client.patch(
            f"/api/v1/candidates/{candidate['candidate_id']}",
            json={field: None},
        ).status_code == 422

    cleared_email = client.patch(
        f"/api/v1/candidates/{candidate['candidate_id']}",
        json={"email": None},
    )
    assert cleared_email.status_code == 200
    assert cleared_email.json()["email"] is None


def test_persisted_shortlist_uses_scored_records_and_never_changes_status(client):
    opening = create_opening(client)
    candidates = [
        create_candidate(
            client,
            opening["opening_id"],
            name=name,
            email=f"{name.lower()}@example.test",
            skills=skills,
            resume_text=resume_text,
        )
        for name, skills, resume_text in [
            (
                "High",
                ["Python", "SQL", "Excel"],
                "Python SQL Excel analyst experience.",
            ),
            ("Low", ["Python"], "Python analyst experience."),
        ]
    ]
    for candidate in candidates:
        client.post(
            "/api/v1/candidates/score",
            json={
                "job_id": opening["opening_id"],
                "candidate_id": candidate["candidate_id"],
            },
        )

    response = client.post(
        f"/api/v1/openings/{opening['opening_id']}/shortlist",
        json={"minimum_score": 60},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["shortlisted_count"] == 1
    assert result["candidates"][0]["candidate_id"] == candidates[0]["candidate_id"]
    assert result["human_review_required"] is True
    assert result["simulation_only"] is False
    assert client.get(
        f"/api/v1/candidates/{candidates[0]['candidate_id']}"
    ).json()["application_status"] == "APPLIED"


def test_resume_upload_extracts_text_and_links_candidate(client):
    opening = create_opening(client)
    candidate = create_candidate(client, opening["opening_id"])
    response = client.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": candidate["candidate_id"]},
        files={"file": ("resume.txt", b"Python SQL resume content", "text/plain")},
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    status = client.get(f"/api/v1/jobs/{job_id}")
    assert status.status_code == 200
    assert status.json()["status"] == "COMPLETED"
    assert status.json()["result"]["parsed_text"] == "Python SQL resume content"
    assert "Python" in status.json()["result"]["resume_data"]["skills"]
    assert client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).json()["resume_data"]["skills"] == status.json()["result"]["resume_data"]["skills"]
    parsed = client.post(
        "/api/v1/resumes/parse", json={"job_id": job_id}
    )
    assert parsed.json()["parsed_text"] == "Python SQL resume content"
    assert parsed.json()["extracted_data"]["skills"] == status.json()["result"]["resume_data"]["skills"]

    with TestClient(app, headers=client.headers) as restarted_client:
        restarted_client.cookies.update(client.cookies)
        assert restarted_client.get(f"/api/v1/jobs/{job_id}").json()["status"] == "COMPLETED"
        restarted_candidate = restarted_client.get(
            f"/api/v1/candidates/{candidate['candidate_id']}"
        ).json()
        assert restarted_candidate["resume_text"] == "Python SQL resume content"
        assert restarted_candidate["resume_data"] == status.json()["result"]["resume_data"]


def test_docx_upload_extracts_document_text(client):
    document = Document()
    document.add_paragraph("Python experience and SQL project")
    stream = BytesIO()
    document.save(stream)

    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "resume.docx",
                stream.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 202
    job = client.get(f"/api/v1/jobs/{response.json()['job_id']}").json()
    assert job["status"] == "COMPLETED"
    assert "Python experience" in job["result"]["parsed_text"]


def test_pdf_upload_extracts_document_text(client):
    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=100)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_reference = writer._add_object(font)
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): font_reference}
            )
        }
    )
    content = DecodedStreamObject()
    content.set_data(b"BT /F1 12 Tf 10 50 Td (Python SQL demo resume) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(content)
    pdf = BytesIO()
    writer.write(pdf)

    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.pdf", pdf.getvalue(), "application/pdf")},
    )
    assert response.status_code == 202
    job = client.get(f"/api/v1/jobs/{response.json()['job_id']}").json()
    assert job["status"] == "COMPLETED"
    assert job["result"]["parsed_text"] == "Python SQL demo resume"


def test_invalid_resume_upload_and_unreadable_pdf_are_reported(client):
    assert client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.exe", b"not a resume", "application/octet-stream")},
    ).status_code == 400
    assert client.post(
        "/api/v1/resumes/upload",
        files={"file": ("mismatched.pdf", b"%PDF-1.4", "text/plain")},
    ).status_code == 400
    assert client.post(
        "/api/v1/resumes/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    ).status_code == 400

    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("broken.pdf", b"not a PDF", "application/pdf")},
    )
    assert response.status_code == 202
    job = client.get(f"/api/v1/jobs/{response.json()['job_id']}").json()
    assert job["status"] == "FAILED"
    assert "invalid format" in job["error"]
    assert client.post(
        "/api/v1/resumes/parse", json={"job_id": response.json()["job_id"]}
    ).status_code == 409


def test_upload_limit_and_interrupted_job_recovery(client):
    oversized = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("large.txt", b"x" * (5 * 1024 * 1024 + 1), "text/plain")},
    )
    assert oversized.status_code == 413

    job_id = create_job("interrupted.txt")
    update_job(job_id, "PROCESSING")
    with TestClient(app, headers=client.headers) as restarted_client:
        restarted_client.cookies.update(client.cookies)
        job = restarted_client.get(f"/api/v1/jobs/{job_id}").json()
        assert job["status"] == "FAILED"
        assert "interrupted by a server restart" in job["error"]


def test_validation_duplicate_email_and_missing_records(client):
    opening = create_opening(client)
    create_candidate(client, opening["opening_id"])
    assert client.post(
        "/api/v1/candidates",
        json={
            "name": "Duplicate Applicant",
            "email": "candidate@example.test",
            "opening_id": opening["opening_id"],
        },
    ).status_code == 409
    assert client.post(
        "/api/v1/openings",
        json={"title": "Missing skills", "required_skills": []},
    ).status_code == 422
    assert client.post(
        "/api/v1/candidates",
        json={
            "name": "Invalid Email",
            "email": "not-an-email",
            "opening_id": opening["opening_id"],
        },
    ).status_code == 422
    assert client.post(
        "/api/v1/candidates",
        json={"name": "Orphan", "opening_id": "missing-opening"},
    ).status_code == 404
    assert client.get("/api/v1/openings/missing-opening").status_code == 404
    assert client.patch(
        "/api/v1/openings/missing-opening",
        json={"title": "Missing"},
    ).status_code == 404
    assert client.delete("/api/v1/openings/missing-opening").status_code == 404
    assert client.get("/api/v1/candidates/missing-candidate").status_code == 404
    assert client.patch(
        "/api/v1/candidates/missing-candidate",
        json={"name": "Missing"},
    ).status_code == 404
    assert client.delete("/api/v1/candidates/missing-candidate").status_code == 404
    assert client.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": "missing-candidate"},
        files={"file": ("resume.txt", b"Python", "text/plain")},
    ).status_code == 404
    assert client.get("/api/v1/jobs/unknown").status_code == 404
    assert client.get(
        "/api/v1/candidates",
        params={"application_status": "INVALID"},
    ).status_code == 422


def test_caller_supplied_shortlist_is_labeled_as_simulation(client):
    response = client.post(
        "/api/v1/candidates/shortlist",
        json={
            "candidates": [
                {"candidate_id": "SYNTHETIC-01", "score": 85},
                {"candidate_id": "SYNTHETIC-02", "score": 55},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["simulation_only"] is True
    assert response.json()["status"] == "SIMULATION_ONLY"


def test_recruiter_authentication_is_required_and_configuration_is_checked(
    client, monkeypatch, tmp_path
):
    unauthorized = client.get(
        "/api/v1/openings",
        headers={"Authorization": "Basic bm90LXRoZS1yZWNydWl0ZXI="},
    )
    assert unauthorized.status_code == 401
    assert unauthorized.headers["www-authenticate"] == "Basic"

    basic_value = base64.b64encode(
        b"demo-recruiter:test-password-long-enough"
    ).decode("ascii")
    with TestClient(
        app, headers={"Authorization": f"Basic {basic_value}"}
    ) as basic_client:
        assert basic_client.get("/api/v1/openings").status_code == 200

    client.cookies.clear()
    monkeypatch.setenv("ZECPATH_DB_PATH", str(tmp_path / "unconfigured.sqlite3"))
    health = TestClient(app).get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["authentication_configured"] is False
    unconfigured = client.get("/api/v1/openings")
    assert unconfigured.status_code == 503
    assert "not configured" in unconfigured.json()["detail"]


def test_recruiter_session_survives_restart_and_logout_revokes_it(client):
    login = client.post(
        "/api/v1/auth/session",
        json={
            "username": "demo-recruiter",
            "password": "test-password-long-enough",
        },
    )
    assert login.status_code == 200
    assert login.json()["authenticated"] is True
    assert login.json()["expires_at"] > 0
    cookie = login.headers["set-cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=strict" in cookie
    assert "Max-Age=28800" in cookie
    assert "Path=/api/v1" in cookie
    token = client.cookies.get("zecpath_session")
    assert token

    with TestClient(app) as restarted_client:
        restarted_client.cookies.set("zecpath_session", token)
        session = restarted_client.get("/api/v1/auth/session")
        assert session.status_code == 200
        assert session.json()["username"] == "demo-recruiter"
        assert session.json()["expires_at"] == login.json()["expires_at"]
        assert restarted_client.get("/api/v1/openings").status_code == 200

        payload = {
            "title": "Session Protected Role",
            "required_skills": ["Python"],
        }
        blocked = restarted_client.post("/api/v1/openings", json=payload)
        assert blocked.status_code == 403
        created = restarted_client.post(
            "/api/v1/openings",
            json=payload,
            headers={"Origin": "http://testserver"},
        )
        assert created.status_code == 201

        signed_out = restarted_client.delete(
            "/api/v1/auth/session",
            headers={"Origin": "http://testserver"},
        )
        assert signed_out.status_code == 204
        assert restarted_client.get("/api/v1/openings").status_code == 401


def test_first_recruiter_cli_creates_account_and_completes_login_flow(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setenv("ZECPATH_DB_PATH", str(tmp_path / "setup.sqlite3"))
    monkeypatch.setattr("builtins.input", lambda _: "first-recruiter")
    passwords = iter(("first-recruiter-password-2026", "first-recruiter-password-2026"))
    monkeypatch.setattr(create_recruiter, "getpass", lambda _: next(passwords))

    create_recruiter.main()

    account = database.get_recruiter_account("first-recruiter")
    assert account is not None
    assert "first-recruiter-password-2026" not in account["password_hash"]
    assert "first-recruiter-password-2026" not in capsys.readouterr().out

    with TestClient(app) as setup_client:
        invalid = setup_client.post(
            "/api/v1/auth/session",
            json={
                "username": "first-recruiter",
                "password": "incorrect-password",
            },
        )
        assert invalid.status_code == 401

        login = setup_client.post(
            "/api/v1/auth/session",
            json={
                "username": "first-recruiter",
                "password": "first-recruiter-password-2026",
            },
        )
        assert login.status_code == 200
        assert setup_client.get("/").status_code == 200
        assert setup_client.get("/api/v1/auth/session").json()["authenticated"] is True
        assert setup_client.get("/api/v1/openings").status_code == 200

        signed_out = setup_client.delete(
            "/api/v1/auth/session",
            headers={"Origin": "http://testserver"},
        )
        assert signed_out.status_code == 204
        assert setup_client.get("/api/v1/openings").status_code == 401


def test_expired_recruiter_session_is_rejected(client):
    token = "expired-test-session"
    database.create_recruiter_session(token, "demo-recruiter", -1)
    client.cookies.set("zecpath_session", token)

    assert client.get("/api/v1/auth/session").json()["authenticated"] is False
    assert client.get("/api/v1/openings").status_code == 401


def test_recruiter_reset_changes_credentials_and_revokes_sessions(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("ZECPATH_DB_PATH", str(tmp_path / "reset.sqlite3"))
    old_password = "old-recruiter-password-2026"
    old_salt, old_hash = hash_recruiter_password(old_password)
    database.create_first_recruiter_account("old-recruiter", old_salt, old_hash)

    with TestClient(app) as reset_client:
        login = reset_client.post(
            "/api/v1/auth/session",
            json={"username": "old-recruiter", "password": old_password},
        )
        assert login.status_code == 200
        old_token = reset_client.cookies.get("zecpath_session")
        assert old_token

        monkeypatch.setattr("builtins.input", lambda _: "new-recruiter")
        passwords = iter(("new-recruiter-password-2026", "new-recruiter-password-2026"))
        monkeypatch.setattr(reset_recruiter, "getpass", lambda _: next(passwords))
        reset_recruiter.main()

        assert database.get_recruiter_session(old_token) is None
        assert reset_client.get("/api/v1/openings").status_code == 401
        old_login = reset_client.post(
            "/api/v1/auth/session",
            json={"username": "old-recruiter", "password": old_password},
        )
        assert old_login.status_code == 401
        new_login = reset_client.post(
            "/api/v1/auth/session",
            json={
                "username": "new-recruiter",
                "password": "new-recruiter-password-2026",
            },
        )
        assert new_login.status_code == 200


def test_recruiter_login_is_rate_limited(client):
    for _ in range(4):
        response = client.post(
            "/api/v1/auth/session",
            json={"username": "demo-recruiter", "password": "incorrect"},
        )
        assert response.status_code == 401

    blocked = client.post(
        "/api/v1/auth/session",
        json={"username": "demo-recruiter", "password": "incorrect"},
    )
    assert blocked.status_code == 429
    assert blocked.headers["retry-after"] == "900"


def test_recruiter_password_is_persisted_as_a_salted_hash(tmp_path, monkeypatch):
    monkeypatch.setenv("ZECPATH_DB_PATH", str(tmp_path / "hashed-account.sqlite3"))
    password = "strong-test-password-2026"
    salt, password_hash = hash_recruiter_password(password)
    database.create_first_recruiter_account("hashed-recruiter", salt, password_hash)

    account = database.get_recruiter_account("hashed-recruiter")
    assert account is not None
    assert account["password_salt"] != account["password_hash"]
    assert password not in account["password_hash"]
    assert verify_recruiter_credentials("hashed-recruiter", password) == "hashed-recruiter"
    assert verify_recruiter_credentials("hashed-recruiter", "wrong-password") is None


def test_health_reports_database_unavailable(client, monkeypatch):
    def fail_database_check():
        raise database.sqlite3.OperationalError("private database detail")

    monkeypatch.setattr(database, "check_database", fail_database_check)
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "The application database is unavailable."


def test_score_normalizes_duplicate_case_variant_requirements_and_keeps_evidence(
    client,
):
    opening = create_opening(
        client,
        required_skills=["Python", "python", " SQL ", "SQL"],
    )
    candidate = create_candidate(
        client,
        opening["opening_id"],
        resume_text="Built a Python data tool.",
    )

    response = client.post(
        "/api/v1/candidates/score",
        json={
            "job_id": opening["opening_id"],
            "candidate_id": candidate["candidate_id"],
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["score"] == pytest.approx(47.5)
    assert result["evidence"]["required_skills"] == ["Python", "SQL"]
    assert result["evidence"]["matched_required_skills"] == ["Python"]
    assert result["evidence"]["missing_required_skills"] == ["SQL"]
    assert result["evidence"]["resume_evidence"] == [
        {"skill": "Python", "excerpt": "Built a Python data tool."}
    ]


def test_deleting_candidate_redacts_saved_resume_processing_results(client):
    opening = create_opening(client)
    candidate = create_candidate(client, opening["opening_id"])
    uploaded = client.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": candidate["candidate_id"]},
        files={"file": ("resume.txt", b"Private synthetic resume text", "text/plain")},
    )
    job_id = uploaded.json()["job_id"]
    assert client.get(f"/api/v1/jobs/{job_id}").json()["result"]["parsed_text"]

    assert client.delete(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).status_code == 204
    assert client.get(f"/api/v1/jobs/{job_id}").json()["result"] is None
    parse_result = client.post("/api/v1/resumes/parse", json={"job_id": job_id})
    assert parse_result.status_code == 410
    assert parse_result.json()["detail"] == "Extracted resume text is no longer available."


def test_deleting_opening_redacts_linked_resume_processing_results(client):
    opening = create_opening(client)
    candidate = create_candidate(client, opening["opening_id"])
    uploaded = client.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": candidate["candidate_id"]},
        files={"file": ("resume.txt", b"Resume tied to deleted opening", "text/plain")},
    )
    job_id = uploaded.json()["job_id"]

    assert client.delete(
        f"/api/v1/openings/{opening['opening_id']}"
    ).status_code == 204
    job = client.get(f"/api/v1/jobs/{job_id}").json()
    assert job["result"] is None
    assert client.post(
        "/api/v1/resumes/parse", json={"job_id": job_id}
    ).status_code == 410


def test_candidate_deletion_during_resume_processing_does_not_restore_resume_text(
    client, monkeypatch
):
    opening = create_opening(client)
    candidate = create_candidate(client, opening["opening_id"])
    original_save_resume = database.save_candidate_resume

    def save_then_delete(candidate_id, filename, parsed_text, resume_data):
        saved = original_save_resume(candidate_id, filename, parsed_text, resume_data)
        assert saved
        assert database.delete_candidate(candidate_id)
        return saved

    monkeypatch.setattr(database, "save_candidate_resume", save_then_delete)
    uploaded = client.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": candidate["candidate_id"]},
        files={"file": ("resume.txt", b"Race condition synthetic resume", "text/plain")},
    )
    job_id = uploaded.json()["job_id"]

    job = client.get(f"/api/v1/jobs/{job_id}").json()
    assert job["status"] == "FAILED"
    assert job["result"] is None
    assert client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).status_code == 404


def test_screening_report_is_rule_based_persisted_and_deleted_with_candidate(
    client,
):
    opening = create_opening(client)
    candidate = create_candidate(client, opening["opening_id"])
    response = client.post(
        f"/api/v1/candidates/{candidate['candidate_id']}/screening-reports",
        json={
            "answers": [
                {
                    "question_id": "Q1",
                    "question": "Which technical skills have you used?",
                    "answer": "I have experience with Python and SQL.",
                    "expected_intent": "skills",
                }
            ]
        },
    )
    assert response.status_code == 201
    report = response.json()
    assert report["method"] == "day25_keyword_and_regex_rules"
    assert report["human_review_required"] is True
    assert report["answers"][0]["detected_intent"] == "skills"
    assert report["answers"][0]["extracted_information"]["skills"] == [
        "Python",
        "SQL",
    ]
    assert report["review_flags"] == []

    with TestClient(app, headers=client.headers) as restarted_client:
        restarted_client.cookies.update(client.cookies)
        saved_reports = restarted_client.get(
            f"/api/v1/candidates/{candidate['candidate_id']}/screening-reports"
        )
        assert saved_reports.status_code == 200
        assert saved_reports.json() == [report]

    assert client.delete(
        f"/api/v1/candidates/{candidate['candidate_id']}"
    ).status_code == 204
    assert client.get(
        f"/api/v1/candidates/{candidate['candidate_id']}/screening-reports"
    ).status_code == 404
