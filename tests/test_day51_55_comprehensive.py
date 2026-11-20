"""Comprehensive Days 51-55 integration and governance test suite."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import auth, database
from src.main import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "day51_55_test.sqlite3"
    monkeypatch.setenv("ZECPATH_DB_PATH", str(db_path))
    database.initialize_database()

    # Seed 3 accounts: admin, junior recruiter, tenant_b admin
    for uname, pwd, role, tenant in [
        ("admin_recruiter", "AdminPass123!", "admin", "default_tenant"),
        ("junior_recruiter", "JuniorPass123!", "recruiter", "default_tenant"),
        ("tenant_b_admin", "TenantBPass123!", "admin", "tenant_b"),
    ]:
        salt, pw_hash = auth.hash_recruiter_password(pwd)
        database.upsert_recruiter_account(uname, salt, pw_hash, role=role, tenant_id=tenant)

    with TestClient(app) as tc:
        # Create opening & candidate in default_tenant
        tc.auth = ("admin_recruiter", "AdminPass123!")
        op = tc.post(
            "/api/v1/openings",
            json={
                "title": "Python Developer",
                "description": "FastAPI & SQLite backend role",
                "required_skills": ["Python", "FastAPI", "SQL"],
            },
        )
        assert op.status_code == 201, op.text
        opening_id = op.json()["opening_id"]

        cand = tc.post(
            "/api/v1/candidates",
            json={
                "name": "Arun Test",
                "email": "arun.test@zecpath.example",
                "opening_id": opening_id,
                "skills": ["Python", "FastAPI", "SQL"],
                "resume_text": "4 years Python FastAPI SQL backend experience.",
            },
        )
        assert cand.status_code == 201, cand.text
        candidate_id = cand.json()["candidate_id"]

        # Set a persisted ATS score directly for deterministic cross-round tests
        with database._connection() as conn:
            conn.execute("UPDATE candidates SET score = 90.0 WHERE candidate_id = ?", (candidate_id,))

        yield {
            "client": tc,
            "db_path": db_path,
            "opening_id": opening_id,
            "candidate_id": candidate_id,
        }


def test_day51_role_weights_stage_status_gate_and_duplicate_prevention(client):
    tc: TestClient = client["client"]
    cid = client["candidate_id"]
    tc.auth = ("admin_recruiter", "AdminPass123!")

    # Invalid weights (sum != 100) rejected
    bad_w = tc.put(
        "/api/v1/role-weights/python_developer",
        json={
            "weights": {"ats": 50, "screening": 10, "hr_interview": 10, "technical_interview": 10, "machine_test": 10},
            "min_required_stages": 3,
        },
    )
    assert bad_w.status_code == 422

    # Valid weights saved
    good_w = tc.put(
        "/api/v1/role-weights/python_developer",
        json={
            "weights": {"ats": 15, "screening": 15, "hr_interview": 15, "technical_interview": 30, "machine_test": 25},
            "min_required_stages": 3,
        },
    )
    assert good_w.status_code == 200
    assert good_w.json()["min_required_stages"] == 3

    # Below min_required_stages -> INSUFFICIENT_EVIDENCE
    insuff = tc.post(
        f"/api/v1/candidates/{cid}/cross-round-evaluation",
        json={
            "target_role": "python_developer",
            "round_scores": {"ats": 90.0},
            "min_required_stages": 3,
        },
    )
    assert insuff.status_code == 201
    assert insuff.json()["calculation_status"] == "INSUFFICIENT_STAGES"

    # Full 5 stages -> COMPLETED
    payload = {
        "target_role": "python_developer",
        "round_scores": {
            "ats": 90.0,
            "screening": 86.0,
            "hr_interview": 84.0,
            "technical_interview": 92.0,
            "machine_test": 88.0,
        },
        "min_required_stages": 3,
    }
    first = tc.post(f"/api/v1/candidates/{cid}/cross-round-evaluation", json=payload)
    assert first.status_code == 201
    first_data = first.json()
    assert first_data["calculation_status"] == "COMPLETED"
    assert first_data["hiring_fit_percentage"] > 85.0
    assert first_data["duplicate_prevented"] is False

    # Repeat identical call -> duplicate prevented
    dup = tc.post(f"/api/v1/candidates/{cid}/cross-round-evaluation", json=payload)
    assert dup.status_code == 201
    assert dup.json()["duplicate_prevented"] is True
    assert dup.json()["evaluation_id"] == first_data["evaluation_id"]

    # Force recalculate -> new evaluation_id
    recalc = tc.post(
        f"/api/v1/candidates/{cid}/cross-round-evaluation",
        json={**payload, "force_recalculate": True, "recalculation_reason": "Manual audit check"},
    )
    assert recalc.status_code == 201
    assert recalc.json()["evaluation_id"] != first_data["evaluation_id"]


def test_day52_eligibility_override_thresholds_and_recruiter_audit(client):
    tc: TestClient = client["client"]
    cid = client["candidate_id"]
    tc.auth = ("admin_recruiter", "AdminPass123!")

    # Seed cross-round high score
    tc.post(
        f"/api/v1/candidates/{cid}/cross-round-evaluation",
        json={
            "target_role": "python_developer",
            "round_scores": {"ats": 90.0, "screening": 88.0, "hr_interview": 86.0, "technical_interview": 91.0, "machine_test": 90.0},
        },
    )

    # Mandatory eligibility REJECTED overrides high score
    rej_rec = tc.post(
        f"/api/v1/candidates/{cid}/final-recommendation",
        json={
            "target_role": "python_developer",
            "eligibility_status": "REJECTED",
            "eligibility_reason": "Missing mandatory SQL experience",
        },
    )
    assert rej_rec.status_code == 201
    assert rej_rec.json()["decision"] == "REJECTED"
    assert "MANDATORY_ELIGIBILITY_FAILED" in rej_rec.json()["reason_codes"]

    # Eligible -> SELECTED
    sel_rec = tc.post(
        f"/api/v1/candidates/{cid}/final-recommendation",
        json={"target_role": "python_developer", "eligibility_status": "ELIGIBLE"},
    )
    assert sel_rec.status_code == 201
    rec_id = sel_rec.json()["recommendation_id"]
    assert sel_rec.json()["decision"] == "SELECTED"

    # Junior recruiter cannot OVERRIDE (403)
    tc.auth = ("junior_recruiter", "JuniorPass123!")
    denied_override = tc.post(
        f"/api/v1/final-recommendations/{rec_id}/decision",
        json={"recruiter_decision": "OVERRIDDEN", "notes": "Attempting override"},
    )
    assert denied_override.status_code == 403

    # Admin can APPROVE and history is logged
    tc.auth = ("admin_recruiter", "AdminPass123!")
    approved = tc.post(
        f"/api/v1/final-recommendations/{rec_id}/decision",
        json={"recruiter_decision": "APPROVED", "notes": "Strong technical and coding scores"},
    )
    assert approved.status_code == 200
    assert approved.json()["recruiter_decision"] == "APPROVED"

    hist = tc.get(f"/api/v1/final-recommendations/{rec_id}/history")
    assert hist.status_code == 200
    assert len(hist.json()) == 1
    assert hist.json()[0]["actor_id"] == "admin_recruiter"


def test_day53_report_14_sections_html_markdown_and_pdf(client):
    tc: TestClient = client["client"]
    cid = client["candidate_id"]
    tc.auth = ("admin_recruiter", "AdminPass123!")

    rep = tc.post(f"/api/v1/candidates/{cid}/hiring-intelligence-report")
    assert rep.status_code == 201
    data = rep.json()
    assert data["candidate_id"] == cid
    assert "evaluation_summary" in data
    assert "recruiter_decision_workflow" in data

    html_res = tc.get(f"/api/v1/candidates/{cid}/hiring-intelligence-report/html")
    assert html_res.status_code == 200
    assert "text/html" in html_res.headers["content-type"]

    md_res = tc.get(f"/api/v1/candidates/{cid}/hiring-intelligence-report/markdown")
    assert md_res.status_code == 200

    pdf_res = tc.get(f"/api/v1/candidates/{cid}/hiring-intelligence-report/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-1.4")


def test_day54_optimization_metrics_and_history(client):
    tc: TestClient = client["client"]
    tc.auth = ("admin_recruiter", "AdminPass123!")

    run_res = tc.post(
        "/api/v1/optimization/run",
        json={"strong_threshold": 80.0, "potential_threshold": 60.0},
    )
    assert run_res.status_code == 200
    body = run_res.json()
    assert len(body["cases"]) > 0
    assert "accuracy" in body["metrics"]
    assert "confusion_matrix" in body["metrics"]
    assert len(body["threshold_comparisons"]) >= 3
    assert body["benchmark"]["dataset_eval_ms"] >= 0

    hist = tc.get("/api/v1/optimization/history")
    assert hist.status_code == 200
    assert len(hist.json()) >= 1


def test_day55_rbac_tenant_isolation_consent_retention_and_tamper_detection(client):
    tc: TestClient = client["client"]
    cid = client["candidate_id"]

    # 1. Consent ledger
    tc.auth = ("admin_recruiter", "AdminPass123!")
    c_post = tc.post(
        f"/api/v1/candidates/{cid}/consent",
        json={"purpose": "ai_assessment", "granted": True, "consent_version": "consent-v2"},
    )
    assert c_post.status_code == 201
    c_get = tc.get(f"/api/v1/candidates/{cid}/consent")
    assert c_get.status_code == 200
    assert len(c_get.json()) == 1

    # 2. RBAC enforcement: junior_recruiter cannot access audit/verify, optimization, or anonymize
    tc.auth = ("junior_recruiter", "JuniorPass123!")
    assert tc.get("/api/v1/audit/events").status_code == 403
    assert tc.get("/api/v1/audit/verify").status_code == 403
    assert tc.post("/api/v1/optimization/run", json={}).status_code == 403
    assert tc.post(f"/api/v1/governance/candidates/{cid}/anonymize").status_code == 403

    # 3. Cross-tenant isolation: tenant_b_admin cannot access default_tenant candidate
    tc.auth = ("tenant_b_admin", "TenantBPass123!")
    assert tc.get(f"/api/v1/candidates/{cid}/cross-round-evaluation").status_code == 403
    assert tc.get(f"/api/v1/candidates/{cid}/hiring-intelligence-report").status_code == 403

    # 4. Audit verify succeeds before tamper, fails after SQLite tamper
    tc.auth = ("admin_recruiter", "AdminPass123!")
    verify_ok = tc.get("/api/v1/audit/verify")
    assert verify_ok.status_code == 200
    assert verify_ok.json()["verified"] is True

    # 5. Retention policy & anonymization
    ret = tc.get("/api/v1/governance/retention-policies")
    assert ret.status_code == 200
    assert len(ret.json()) >= 1

    anon = tc.post(f"/api/v1/governance/candidates/{cid}/anonymize")
    assert anon.status_code == 200
    assert anon.json()["status"] == "ANONYMIZED"

    # 6. Tamper detection check
    with sqlite3.connect(client["db_path"]) as conn:
        conn.execute("UPDATE audit_events SET details_json = '{\"tampered\":true}' WHERE rowid = 1")
        conn.commit()
    verify_bad = tc.get("/api/v1/audit/verify")
    assert verify_bad.status_code == 200
    assert verify_bad.json()["verified"] is False
