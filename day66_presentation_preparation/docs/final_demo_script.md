# ZecPath AI Hiring System — Final Demo Script (Day 66)

## 1. Opening Introduction (1.5 min)
"Welcome to the ZecPath AI Hiring System demonstration. ZecPath is a local-first, FastAPI and SQLite recruitment decision-support platform designed to unify resume parsing, 4-factor ATS scoring, multi-round assessments, cross-round aggregation, and human-in-the-loop final recommendations."

## 2. Problem & Architecture Explanation (2.5 min)
- **Problem:** Traditional pipelines lose context between ATS and interviews, silently penalize candidates with `0` for uncompleted rounds, and lack auditable explanations.
- **Architecture:** Show `system_architecture.png` — Vanilla JS Recruiter Workspace (`static/index.html`) + FastAPI (`src/api.py`, 125 `/api/v1/*` routes) + SQLite (`src/database.py`) + `ObservabilityASGIMiddleware`.

## 3. Step-by-Step Live Demo Sequence (8 min)
1. **Recruiter Sign-In:** Log in at `http://127.0.0.1:8000` (`POST /api/v1/auth/session`, HTTP-only cookie).
2. **Job Openings & Candidate Registration (`tab-ats`):** Select `Senior Python Backend Architect`, show Day 63 seeded candidates, and upload `resume_strong_python.txt` (`POST /api/v1/resumes/upload` -> `202 Accepted`).
3. **ATS & Eligibility:** Trigger `POST /api/v1/ats/score` and `POST /api/v1/candidates/{id}/eligibility/evaluate`; show exact weighted breakdown (Skills 40%, Semantic 25%, Experience 20%, Education 15%) and snippet evidence.
4. **Multi-Round API Stages:** Show Screening, HR Interview, Technical Interview, and Machine Test API outputs (noting honestly that these 4 stages are API-driven via `/docs` or REST clients, while Machine Test uses AST static analysis).
5. **Cross-Round Aggregation (`tab-cross-round`):** Run evaluation, highlight `exclude_and_renormalize` and SHA-256 `input_fingerprint`.
6. **Final Recommendation & Human Review (`tab-recommendation`):** Generate recommendation, explain confidence formula (`50%` coverage + `30%` evidence + `20%` consistency), and submit recruiter `APPROVE` decision.
7. **Hiring Intelligence Report (`tab-report`):** Generate 14-section report and open HTML/PDF export.
8. **Governance & Monitoring (`tab-governance`, `#monitoringSection`):** Verify SHA-256 `audit_events` chain (`/api/v1/audit/verify`) and live P50/P95 latency metrics.

## 4. Business Impact, Limitations & Closing (2 min)
- **Impact:** Consistent rubric scoring, zero silent penalties, full decision auditability, mandatory human sign-off.
- **Honest Limitations:** SQLite single-node prototype, AST-only machine test (no container sandbox), synthetic 12-case optimization benchmark.
- **Closing:** Thank stakeholders and open the floor for Q&A.
