from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "ZecPath ATS API"


def test_health():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_shortlist():
    payload = {
        "job_id": "JOB001",
        "minimum_score": 60,
        "candidates": [
            {
                "candidate_id": "C001",
                "score": 85,
            },
            {
                "candidate_id": "C002",
                "score": 55,
            },
            {
                "candidate_id": "C003",
                "score": 75,
            },
        ],
    }

    response = client.post(
        "/api/v1/candidates/shortlist",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["shortlisted_count"] == 2
    assert data["candidates"][0]["candidate_id"] == "C001"
    assert data["candidates"][0]["rank"] == 1


def test_score():
    payload = {
        "job_id": "JOB001",
        "candidate_id": "C001",
    }

    response = client.post(
        "/api/v1/candidates/score",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "SCORED"


def test_invalid_job():
    response = client.get(
        "/api/v1/jobs/non-existing-job"
    )

    assert response.status_code == 404


def test_invalid_resume_extension():
    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "resume.exe",
                b"invalid",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400