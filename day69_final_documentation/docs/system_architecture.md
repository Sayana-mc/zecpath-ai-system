# ZecPath System Architecture

- **Client:** Browser (`static/index.html` with 6 tabs: `tab-ats`, `tab-cross-round`, `tab-recommendation`, `tab-report`, `tab-optimization`, `tab-governance`) or REST/Swagger client (`/docs`).
- **API & Middleware:** `src/main.py` wraps `src/api.py` with `ObservabilityASGIMiddleware` and `lifespan` DB initialization.
- **Core Engines (`src/`):** `resume_analysis.py`, `ats_scoring_engine.py`, `eligibility.py`, `screening_pipeline.py`, `hr_interview_pipeline.py`, `technical_interview_engine.py`, `machine_test_engine.py`, `cross_round_scoring_engine.py`, `final_recommendation_engine.py`, `hiring_intelligence_report_generator.py`, `optimization_engine.py`, `security_governance.py`.
- **Database & Artifacts:** SQLite (`src/database.py`), `uploads/`, `logs/*.jsonl`, and exported reports.
