from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_score_candidate():

    response = client.post(
        "/api/v1/scoring",
        json={
            "candidate_id": "CAND001",
            "job_id": "JOB001",
            "skills": [
                "python",
                "sql",
                "power bi",
            ],
            "experience_years": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_id"] == "CAND001"
    assert data["job_id"] == "JOB001"
    assert 0 <= data["score"] <= 100


def test_shortlist():

    response = client.post(
        "/api/v1/shortlist",
        json={
            "job_id": "JOB001",
            "candidate_ids": [
                "CAND001",
                "CAND002",
                "CAND003",
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 3


def test_job_not_found():

    response = client.get(
        "/api/v1/jobs/invalid-job-id"
    )

    assert response.status_code == 404