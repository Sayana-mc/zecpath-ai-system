# ZecPath Module Reference (`src/`)

- `main.py` / `api.py`: FastAPI entrypoint, middleware, and 125 `/api/v1/*` routes.
- `database.py`: SQLite schema, migrations, CRUD, and audit-chain persistence.
- `auth.py` / `security_governance.py`: PBKDF2-SHA256 auth, cookies, RBAC, tenant isolation, consent, retention, anonymization.
- `resume_analysis.py` / `ats_scoring_engine.py` / `eligibility.py`: Resume parsing, 4-factor ATS, and eligibility gate.
- `screening_pipeline.py` / `hr_interview_pipeline.py` / `technical_interview_engine.py` / `machine_test_engine.py`: Stage-specific assessment engines.
- `cross_round_scoring_engine.py` / `final_recommendation_engine.py` / `hiring_intelligence_report_generator.py`: Aggregation, recommendation, human review, and 14-section report export.
- `observability.py` / `optimization_engine.py` / `init_demo_data.py`: Telemetry, synthetic threshold sweep, and Day 63 seeding.
