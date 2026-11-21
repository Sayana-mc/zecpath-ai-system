# ZecPath AI Hiring System — Project-Wide Technical Audit (Phase 1)

**Repository:** `C:\Users\sayan\Documents\zecpath-ai-system`  
**Audit Date:** 2026-11-21  
**Scope:** Full codebase inspection across frontend, backend, database, AI/scoring engines, security/governance, observability, demo dataset, tests, and Day 61–70 deliverables.

---

## 1. Project Architecture

ZecPath is a local-first, FastAPI + SQLite + Vanilla JS recruitment decision-support application (`src/main.py`) accompanied by historical day-by-day prototype modules (`day3_*` through `day68_*`).

- **Presentation Layer:** Single-page recruiter workspace served at `/` from `static/index.html` (2,337 lines, vanilla HTML/CSS/JS with 6 main tabs: `tab-ats`, `tab-cross-round`, `tab-recommendation`, `tab-report`, `tab-optimization`, `tab-governance`, plus recruiter login and live observability monitoring).
- **API Layer:** FastAPI application (`src/main.py`) mounting `router` and `system_router` from `src/api.py` alongside sub-routers for screening, HR interviews, technical interviews, and machine tests (**125 `/api/v1/*` routes** total), plus Swagger UI at `/docs`.
- **Persistence Layer:** SQLite database (`data/zecpath.sqlite3` by default, configurable via `ZECPATH_DB_PATH`) managed in `src/database.py` with foreign keys, schema initialization, and migration helpers.
- **Observability Layer:** `ObservabilityASGIMiddleware` (`src/observability.py`) capturing request latency, status codes, error logs, and JSONL telemetry under `logs/`.
- **Security & Governance Layer:** PBKDF2-SHA256 password hashing (`src/auth.py`), HTTP-only session cookies + HTTP Basic auth, 4 RBAC roles, tenant isolation, SHA-256 hash-chained `audit_events`, candidate consent, retention policies, and anonymization (`src/security_governance.py`).

---

## 2. Frontend and Backend Structure

- **Frontend (`static/index.html`):**
  - Recruiter Sign-In / Sign-Out (`#loginForm`, `#signOutButton`) using `/api/v1/auth/session`.
  - **ATS & Openings (`tab-ats`):** Job opening creation/selection (`#openingSelect`), candidate registration, resume upload (`POST /api/v1/resumes/upload`), ATS scoring, eligibility evaluation, and candidate table (`#candidateTable`).
  - **Cross-Round Aggregation (`tab-cross-round`):** Role weight inspection/update and 5-stage candidate score aggregation.
  - **Final Recommendation (`tab-recommendation`):** Threshold inspection, explainable AI recommendation (`SELECTED`, `HOLD_REVIEW`, `REJECTED`), and mandatory human review (`APPROVED`, `OVERRIDDEN`, `REJECTED`).
  - **Hiring Intelligence Report (`tab-report`):** 14-section report generation and export in JSON, HTML, Markdown, and PDF 1.4.
  - **Optimization (`tab-optimization`):** Synthetic benchmark threshold optimization (`/api/v1/optimization/run`).
  - **Governance (`tab-governance`):** RBAC matrix, audit hash-chain verification (`/api/v1/audit/verify`), consent, retention policies, and anonymization.
  - **Observability (`#monitoringSection`):** Live dashboard latency (P50/P95), error rates, alerts, and decision audit.
- **Backend (`src/`):** 54 Python modules covering ATS (`ats_scoring_engine.py`, `resume_analysis.py`, `eligibility.py`), Screening (`screening_pipeline.py`, `screening_questions.py`, `answer_understanding_integration.py`, `stt_integration.py`), HR Interview (`hr_interview_pipeline.py`, `hr_interview_engine.py`, `hr_followup_engine.py`, `hr_communication_evaluator.py`, `hr_confidence_analyzer.py`, `hr_aptitude_engine.py`, `hr_scoring_engine.py`, `hr_summary_generator.py`), Technical & Machine Test (`technical_interview_engine.py`, `technical_scoring_engine.py`, `machine_test_engine.py`), Behavioral & Integrity (`behavioral_ai_engine.py`, `integrity_engine.py`), Cross-Round & Decisioning (`cross_round_scoring_engine.py`, `final_recommendation_engine.py`, `hiring_intelligence_report_generator.py`, `optimization_engine.py`), and Governance/Monitoring (`auth.py`, `security_governance.py`, `observability.py`, `database.py`).

---

## 3. Implemented Modules & Integration Status

| Capability | Module(s) | Status | Notes |
| :--- | :--- | :--- | :--- |
| Authentication & RBAC | `src/auth.py`, `src/security_governance.py` | **Working** | PBKDF2-SHA256, HTTP-only cookie + Basic auth, 4 roles, login attempt throttling |
| Resume Upload & Parsing | `src/api.py`, `src/resume_analysis.py`, `parsers/` | **Working** | Async 202 upload for TXT/DOCX/PDF (<=5 MiB), section/skill/experience/education extraction |
| 4-Factor ATS Scoring | `src/ats_scoring_engine.py`, `src/ats_evaluation.py` | **Working** | Weighted Skills (0.40) + Semantic (0.25) + Experience (0.20) + Education (0.15) |
| Eligibility Evaluation | `src/eligibility.py` | **Working** | Evaluates mandatory skills/experience/education; surfaces `ELIGIBLE`/`REVIEW`/`REJECTED` |
| Screening Pipeline | `src/screening_pipeline.py`, `src/screening_*.py` | **Working (API)** | Text/audio screening, intent extraction, 4-factor scoring, report generation (API-driven) |
| HR Interview Engine | `src/hr_interview_pipeline.py`, `src/hr_*.py` | **Working (API)** | Role/experience questions, dynamic follow-ups, communication/aptitude, 11-section report (API-driven) |
| Technical Interview & Machine Test | `src/technical_*.py`, `src/machine_test_engine.py` | **Working (API)** | 5-dim technical rubric; AST/static code analysis for machine test (no OS sandbox) |
| Cross-Round Aggregation | `src/cross_round_scoring_engine.py` | **Working (UI+API)** | Role weights, `exclude_and_renormalize` for missing stages, SHA-256 `input_fingerprint` |
| Final Recommendation & Human Review | `src/final_recommendation_engine.py` | **Working (UI+API)** | `SELECTED`/`HOLD_REVIEW`/`REJECTED`, eligibility override, confidence score, human decision log |
| Hiring Intelligence Report | `src/hiring_intelligence_report_generator.py` | **Working (UI+API)** | 14-section report in JSON, HTML, Markdown, and PDF 1.4 |
| Optimization & Simulation | `src/optimization_engine.py`, `src/simulation_pipeline.py` | **Working (UI+API)** | Confusion matrix, Precision/Recall/F1 on synthetic 12-case benchmark |
| Observability & Audit Chain | `src/observability.py`, `src/security_governance.py` | **Working (UI+API)** | P50/P95 latency, alerts, JSONL logs, SHA-256 tamper-evident `audit_events` |

---

## 4. Partially Implemented & Missing Features

- **Partially Implemented:**
  - **Candidate-Facing UI:** Screening, HR Interview, Technical Interview, Machine Test, and Coaching are fully exposed via `/api/v1/*` REST endpoints and Swagger UI (`/docs`), but `static/index.html` is a recruiter-only workspace and does not provide a standalone candidate portal UI for taking interviews/tests interactively.
  - **Machine-Test Code Execution:** `src/machine_test_engine.py` evaluates code submissions via AST and static rubric analysis rather than executing untrusted candidate code inside an isolated container/micro-VM sandbox.
  - **Speech-to-Text (`src/stt_integration.py`):** Audio upload and transcript cleaning work locally; live production Whisper GPU inference requires external model weights/environment setup.
- **Missing Features (Out of Scope for Local Prototype):**
  - External ATS/HRIS webhooks (Greenhouse, Lever, Workday).
  - Real email/SMS/calendar notification delivery.
  - Multi-worker distributed task queue (Redis/Celery) and PostgreSQL connection pooling.

---

## 5. API, Database & AI/Model Integration Status

- **API Integration:** 125 `/api/v1/*` endpoints verified in `src/main.py` (`app.routes`). Swagger OpenAPI schema served at `/docs`.
- **Database Integration:** SQLite (`data/zecpath.sqlite3` or `ZECPATH_DB_PATH`) initialized automatically via `lifespan` in `src/main.py` (`database.initialize_database()`). Demo seeding via `src/init_demo_data.py` populates 4 job openings, 8 synthetic candidates (`demo_data/candidates/candidates.json`), parsed resumes, ATS scores, eligibility, and multi-round assessments.
- **AI / Model Integration (Honest Classification):**
  - **Local ML/NLP:** Sentence-embedding semantic similarity in ATS scoring (with deterministic fallback when model unavailable).
  - **Rule-Based / Deterministic:** Eligibility rules, cross-round weighted renormalization, threshold classification (`SELECTED`/`HOLD_REVIEW`/`REJECTED`), AST-based machine-test checks, filler-word/hesitation detection, and optimization grid search.
  - **No External Paid LLM API Dependency:** System runs offline without requiring OpenAI/Anthropic API keys.

---

## 6. Known Bugs, Limitations & Production-Readiness Gaps

1. **Duplicate/Parallel Day Folders:** Historical `day3_*`–`day68_*` folders coexist alongside `src/` and `final_submission/`.
2. **SQLite Concurrency Ceiling:** Suitable for local single-node demos; concurrent high-throughput writes require PostgreSQL.
3. **No Isolated Code Sandbox:** Machine-test submissions are statically analyzed (`ast`), not executed in an isolated container.
4. **Validation Bias Benchmark:** Day 54 optimization accuracy (91.7% at `selected_min=80.0`) is measured on a 12-case synthetic dataset, not real-world hiring outcomes.
5. **Production-Readiness Verdict:** **Prototype / Demo-Ready, NOT Production-Ready** without PostgreSQL migration, micro-VM code sandbox, external SSO/MFA, TLS termination, legal bias audit, and candidate-facing UI.
