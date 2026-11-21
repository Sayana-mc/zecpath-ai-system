# Day 66 Presentation Source Notes

Every claim in `day66_presentation_preparation/presentation/ZecPath_Final_Presentation.pptx` is grounded in actual repository files:

- **API & App Entry:** `src/main.py`, `src/api.py` (125 `/api/v1/*` routes verified via `app.routes`).
- **Frontend:** `static/index.html` (6 tabs: `tab-ats`, `tab-cross-round`, `tab-recommendation`, `tab-report`, `tab-optimization`, `tab-governance`).
- **Scoring & Decisioning:** `src/ats_scoring_engine.py`, `src/eligibility.py`, `src/cross_round_scoring_engine.py`, `src/final_recommendation_engine.py`, `src/hiring_intelligence_report_generator.py`.
- **Security & Monitoring:** `src/auth.py`, `src/security_governance.py`, `src/observability.py`.
- **Demo Dataset:** `demo_data/candidates/candidates.json` (8 profiles), `demo_data/jobs/*.json` (4 openings), `demo_data/resumes/*.txt` (8 resumes), seeded via `src/init_demo_data.py`.
- **Diagrams:** Generated directly by `scripts/generate_day66_diagrams.py` from real module names.
