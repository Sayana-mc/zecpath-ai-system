"""Repeatable Day 20 ATS live demo script using synthetic data and the root API."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Use an isolated test database to protect the real database
temp_dir = tempfile.TemporaryDirectory()
os.environ["ZECPATH_DB_PATH"] = str(Path(temp_dir.name) / "demo_ats.sqlite3")

from fastapi.testclient import TestClient

from src.main import app
from src import database
from src.auth import hash_recruiter_password


def run_live_ats_demo():
    print("=" * 60)
    print("ZecPath ATS Live Demo Walkthrough (Day 20)")
    print("=" * 60)

    demo_dir = Path(__file__).resolve().parent
    job_file = demo_dir / "demo_job.json"
    candidates_file = demo_dir / "demo_candidates.json"

    with open(job_file, "r", encoding="utf-8") as f:
        job_data = json.load(f)
    with open(candidates_file, "r", encoding="utf-8") as f:
        candidates_data = json.load(f)

    with TestClient(app, headers={"Origin": "http://testserver"}) as client:
        # Step 1: Recruiter setup and login
        salt, p_hash = hash_recruiter_password("demo-secret-pass-123")
        database.create_first_recruiter_account("demo_recruiter_day20", salt, p_hash)
        login = client.post(
            "/api/v1/auth/session",
            json={"username": "demo_recruiter_day20", "password": "demo-secret-pass-123"},
        )
        print(f"[1] Recruiter Login: Status {login.status_code}")

        # Step 2: Create Job Opening
        opening_resp = client.post("/api/v1/openings", json=job_data)
        opening = opening_resp.json()
        opening_id = opening["opening_id"]
        print(f"[2] Created Opening: '{opening['title']}' (ID: {opening_id})")

        # Step 3: Register candidates and score
        scored = []
        for c in candidates_data:
            c_resp = client.post(
                "/api/v1/candidates",
                json={
                    "name": c["name"],
                    "email": c["email"],
                    "opening_id": opening_id,
                    "skills": c["skills"],
                    "resume_text": c["resume_text"],
                },
            )
            cand = c_resp.json()
            cand_id = cand["candidate_id"]

            score_resp = client.post(
                "/api/v1/ats/score",
                json={"candidate_id": cand_id, "job_id": opening_id},
            )
            s_data = score_resp.json()
            scored.append(s_data)
            print(f"[3] Candidate: {cand['name']} -> ATS Score: {s_data['score']:.1f} (Rank {s_data['ranking']})")

        # Step 4: Shortlist Candidates
        shortlist_resp = client.post(
            "/api/v1/ats/shortlist",
            json={"job_id": opening_id, "minimum_score": 60.0},
        )
        sl_data = shortlist_resp.json()
        print(f"[4] Shortlist Generated: {sl_data['shortlisted_count']} candidate(s) meet threshold >= 60.0")
        for sc in sl_data["candidates"]:
            print(f"    - Rank {sc['rank']}: Candidate ID {sc['candidate_id']} (Score: {sc['score']})")

        print("=" * 60)
        print("Demo completed successfully using real application workflows!")
        print("=" * 60)


if __name__ == "__main__":
    run_live_ats_demo()
