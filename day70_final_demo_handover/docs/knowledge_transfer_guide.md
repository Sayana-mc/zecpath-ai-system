# ZecPath Knowledge Transfer Guide (Day 70)

## 1. Key Source Files
- **Entrypoint & API:** `src/main.py` (FastAPI + middleware + lifespan), `src/api.py` (125 `/api/v1/*` routes), `src/schemas.py` (Pydantic contracts).
- **Frontend:** `static/index.html` (single-page Vanilla JS recruiter workspace with 6 tabs + login + monitoring).
- **Database:** `src/database.py` (SQLite persistence, migrations, audit chain).
- **Scoring & Decisioning:** `src/resume_analysis.py`, `src/ats_scoring_engine.py`, `src/eligibility.py`, `src/cross_round_scoring_engine.py`, `src/final_recommendation_engine.py`, `src/hiring_intelligence_report_generator.py`.
- **Assessments:** `src/screening_pipeline.py`, `src/hr_interview_pipeline.py`, `src/technical_interview_engine.py`, `src/machine_test_engine.py`.
- **Governance & Monitoring:** `src/auth.py`, `src/security_governance.py`, `src/observability.py`.
- **Demo Seeder:** `src/init_demo_data.py` + `demo_data/`.

## 2. How to Start & Run the Demo
```powershell
python -m src.init_demo_data
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000` (UI) or `http://127.0.0.1:8000/docs` (Swagger), sign in with your recruiter account, and walk through ATS -> Cross-Round -> Recommendation -> Human Review -> Report -> Governance.

## 3. Troubleshooting
- **Port 8000 already in use (`Errno 10048`):** Stop the existing `uvicorn` process (`Get-Process python` / `Stop-Process`) before restarting.
- **401 Unauthorized in browser:** Sign in via `#loginForm` (`POST /api/v1/auth/session`); HTTP-only session cookie expires after 8 hours.
- **Login rate-limited:** Wait or clear `recruiter_login_attempts` in local dev DB.
