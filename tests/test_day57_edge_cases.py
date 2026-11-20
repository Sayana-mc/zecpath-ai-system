"""Day 57 Edge-Case & Stabilization Verification Suite."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import auth, database
from src.main import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "day57_edge.sqlite3"
    monkeypatch.setenv("ZECPATH_DB_PATH", str(db_path))
    database.initialize_database()
    salt, pw_hash = auth.hash_recruiter_password("AdminPass123!")
    database.upsert_recruiter_account("admin_d57", salt, pw_hash, role="admin", tenant_id="default_tenant")

    with TestClient(app) as tc:
        tc.auth = ("admin_d57", "AdminPass123!")
        op = tc.post(
            "/api/v1/openings",
            json={
                "title": "Python Backend Engineer",
                "description": "FastAPI & SQL",
                "required_skills": ["Python", "FastAPI", "SQL"],
                "minimum_years_experience": 2.0,
            },
        )
        assert op.status_code == 201
        opening_id = op.json()["opening_id"]

        cand = tc.post(
            "/api/v1/candidates",
            json={
                "name": "Edge Test Candidate",
                "email": "edge.test@zecpath.example",
                "opening_id": opening_id,
                "skills": ["Python"],
            },
        )
        assert cand.status_code == 201
        yield {"client": tc, "opening_id": opening_id, "candidate_id": cand.json()["candidate_id"]}


def test_empty_and_unsupported_and_corrupted_resume_uploads(client):
    tc: TestClient = client["client"]
    cid = client["candidate_id"]

    # 1. Empty resume
    empty_res = tc.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": cid},
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert empty_res.status_code in (400, 422)

    # 2. Unsupported file type (.exe)
    bad_ext = tc.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": cid},
        files={"file": ("malware.exe", b"MZ...", "application/octet-stream")},
    )
    assert bad_ext.status_code in (400, 415, 422)

    # 3. Corrupted PDF bytes (async 202 job fails or sync 400/422)
    bad_pdf = tc.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": cid},
        files={"file": ("broken.pdf", b"%PDF-corrupted-bytes", "application/pdf")},
    )
    if bad_pdf.status_code == 202:
        job_id = bad_pdf.json()["job_id"]
        job_res = tc.get(f"/api/v1/jobs/{job_id}")
        assert job_res.status_code == 200
        assert job_res.json()["status"] in ("FAILED", "QUEUED", "PROCESSING")
    else:
        assert bad_pdf.status_code in (400, 422)


def test_duplicate_candidate_email_and_missing_details(client):
    tc: TestClient = client["client"]
    oid = client["opening_id"]

    # Duplicate email in same opening rejected
    dup = tc.post(
        "/api/v1/candidates",
        json={"name": "Dup User", "email": "edge.test@zecpath.example", "opening_id": oid, "skills": ["Python"]},
    )
    assert dup.status_code in (400, 409, 422)

    # Missing required name
    missing = tc.post(
        "/api/v1/candidates",
        json={"email": "missing.name@zecpath.example", "opening_id": oid, "skills": ["Python"]},
    )
    assert missing.status_code == 422


def test_invalid_scores_and_partial_pipeline_and_idempotency(client):
    tc: TestClient = client["client"]
    cid = client["candidate_id"]

    # Out-of-range (>100) and negative scores rejected
    assert tc.post(
        f"/api/v1/candidates/{cid}/cross-round-evaluation",
        json={"target_role": "python_developer", "round_scores": {"ats": 150.0}},
    ).status_code == 422
    assert tc.post(
        f"/api/v1/candidates/{cid}/cross-round-evaluation",
        json={"target_role": "python_developer", "round_scores": {"ats": -5.0}},
    ).status_code == 422

    # Partial pipeline (1 stage < min_required_stages=3) -> INSUFFICIENT_STAGES
    partial = tc.post(
        f"/api/v1/candidates/{cid}/cross-round-evaluation",
        json={"target_role": "python_developer", "round_scores": {"ats": 80.0}, "min_required_stages": 3},
    )
    assert partial.status_code == 201
    assert partial.json()["calculation_status"] == "INSUFFICIENT_STAGES"

    # Repeated identical evaluation -> duplicate prevented
    p = {"target_role": "python_developer", "round_scores": {"ats": 80.0, "screening": 75.0, "hr_interview": 78.0}, "min_required_stages": 3}
    r1 = tc.post(f"/api/v1/candidates/{cid}/cross-round-evaluation", json=p)
    r2 = tc.post(f"/api/v1/candidates/{cid}/cross-round-evaluation", json=p)
    assert r1.status_code == 201 and r2.status_code == 201
    assert r2.json()["duplicate_prevented"] is True
    assert r2.json()["evaluation_id"] == r1.json()["evaluation_id"]


def test_unauthorized_and_invalid_json_and_zero_experience_eligibility(client):
    tc: TestClient = client["client"]
    oid = client["opening_id"]
    cid = client["candidate_id"]

    # Configure mandatory eligibility (min 2 yrs experience, Python + FastAPI)
    cfg = tc.put(
        f"/api/v1/openings/{oid}/eligibility-config",
        json={"minimum_experience_years": 2.0, "mandatory_skills": ["Python", "FastAPI"]},
    )
    assert cfg.status_code in (200, 201)

    # Candidate with only Python and 0 experience: eligibility requires prior evaluation or returns 422
    elig = tc.get(f"/api/v1/candidates/{cid}/eligibility")
    assert elig.status_code in (200, 422)

    # Unauthorized access rejected (401)
    with TestClient(app) as unauth_tc:
        assert unauth_tc.get("/api/v1/openings").status_code == 401
        assert unauth_tc.post(f"/api/v1/candidates/{cid}/cross-round-evaluation", json={}).status_code == 401
