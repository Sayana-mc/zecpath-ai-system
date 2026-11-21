# ZecPath AI Hiring System — Final Presentation Slide Content (20 Slides)

1. **ZecPath AI Hiring System** — Title slide: 70-Day Engineering Portfolio, FastAPI + SQLite + Local NLP + Vanilla JS, Human-in-the-Loop Decision-Support Architecture.
2. **Project Introduction** — Local-first recruitment platform; 125 `/api/v1/*` REST routes + single-page recruiter workspace (`static/index.html`). *(Includes `01_dashboard.png`)*
3. **Problem Statement** — Fragmented evidence across ATS/interviews, silent zero-penalties for missing stages, opaque automated rejections.
4. **Existing Recruitment Challenges** — Slow manual screening, inconsistent interview rubrics, missing audit trails.
5. **Proposed AI Solution (ZecPath)** — Transparent 4-factor ATS scoring with exact snippet evidence, non-punitive safeguard flags, role-weighted cross-round aggregation.
6. **Project Objectives** — Automate structured extraction/rubric scoring, enforce mandatory human review, provide SHA-256 tamper-evident audit logging and 14-section Hiring Intelligence Reports.
7. **Complete System Architecture** — Frontend (`static/index.html`), Swagger (`/docs`), FastAPI (`src/main.py`, `src/api.py`), SQLite (`src/database.py`), JSONL telemetry. *(Includes `system_architecture.png`)*
8. **Technology Stack Actually Used** — Python 3.12, FastAPI, Uvicorn, Pydantic, SQLite, Vanilla HTML/CSS/JS, local sentence embeddings + deterministic NLP/AST rubrics, Pytest + Playwright.
9. **Overall Hiring Pipeline (10 Stages)** — Resume Upload -> Parsing -> ATS -> Eligibility -> Screening -> HR -> Technical -> Machine Test -> Cross-Round -> Final Recommendation -> Human Review -> Report. *(Includes `hiring_pipeline.png`)*
10. **Resume Upload & Parsing** — Async `202 Accepted` upload (`POST /api/v1/resumes/upload`) for TXT, DOCX, PDF (<=5 MiB) with background `processing_jobs`. *(Includes `02_resume_upload.png`)*
11. **ATS Scoring & Candidate Matching** — `0.40*Skills + 0.25*Semantic + 0.20*Experience + 0.15*Education` with whole-word matching and snippet evidence. *(Includes `04_ats_score_breakdown.png`)*
12. **Eligibility & Screening Evaluation** — Mandatory eligibility rules (`ELIGIBLE`, `REVIEW_REQUIRED`, `REJECTED`) + 4-factor screening rubric. *(Includes `05_screening_output.png`)*
13. **HR Interview Assessment** — Role/experience-aware question bank, dynamic follow-ups, communication fluency & aptitude analysis. *(Includes `06_interview_assessments.png`)*
14. **Technical Interview & Machine Test** — 5-dimension technical rubric + depth classification; AST/static code analysis for machine test (no OS container sandbox). *(Includes `07_technical_machine_test.png`)*
15. **Cross-Round Scoring & Aggregation** — Role weights (`role_weight_configurations`), `exclude_and_renormalize` for missing rounds, SHA-256 `input_fingerprint`. *(Includes `ai_module_interaction.png`)*
16. **Final Recommendation & Human Review** — `SELECTED`, `HOLD_REVIEW`, `REJECTED` with mandatory eligibility override and recruiter `APPROVE`/`OVERRIDE`/`REJECT` logging. *(Includes `09_final_recommendation.png`)*
17. **Hiring Intelligence Report** — 14-section executive report exportable in JSON, HTML, Markdown, and PDF 1.4. *(Includes `10_hiring_intelligence_report.png`)*
18. **Data Flow, Security & Observability** — PBKDF2-SHA256 auth, 4 RBAC roles, tenant isolation, SHA-256 hash-chained `audit_events`, P50/P95 latency & alerts. *(Includes `data_flow.png`)*
19. **Actual End-to-End Demo Results (Day 63 Data)** — Verified results across Strong, Partial, Low, Missing-Skills, High-Skills/Low-Exp, Formatting Edge-Case, Data Analyst, and ML Engineer candidates. *(Includes `08_cross_round_score.png`)*
20. **Limitations, Roadmap & Q&A** — Honest prototype boundaries (SQLite single-node, AST-only machine test, 12-case synthetic benchmark) and production roadmap.
