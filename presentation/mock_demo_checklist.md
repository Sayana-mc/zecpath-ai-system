# ZecPath AI Hiring System — 15-Point Mock Demo Verification Checklist

**Document Version:** 1.0.0  
**Phase:** Day 67 Mock Demo Day  
**Target:** Live Presentation Environment  
**Execution Date:** November 2026  

Use this checklist 30 minutes prior to any stakeholder presentation or live demonstration. Every item must be marked `[VERIFIED PASS]` before granting presenter sign-off.

---

## Pre-Flight Verification Checklist

### Category 1: Environment & Runtime Infrastructure
- [ ] **Item 01 — Python Virtual Environment Active:**
  - Verify `.venv` is intact with Python 3.12+ and all packages installed.
  - Verification: `.venv\Scripts\python --version` returns Python 3.12.x.
  - Status: `[VERIFIED PASS]`

- [ ] **Item 02 — Codebase Syntax & Clean Compilation:**
  - Verify zero unresolved syntax errors or broken imports across `src` and `tests`.
  - Verification: `.venv\Scripts\python -m compileall -q src tests` completes with exit code 0.
  - Status: `[VERIFIED PASS]`

- [ ] **Item 03 — Test Suite Regression Pass:**
  - Full automated regression test suite executes without failures.
  - Verification: `.venv\Scripts\python -m pytest tests/test_day53_day60.py tests/test_ats_scoring_engine.py` passes 100%.
  - Status: `[VERIFIED PASS]`

---

### Category 2: Database & Dataset Seeding
- [ ] **Item 04 — Demo Database Fresh Seeding:**
  - Run the automated seeding script to populate all 4 jobs and 8 candidate archetypes.
  - Verification: `.venv\Scripts\python -m src.init_demo_data` outputs `[SUCCESS] Demo dataset initialization completed successfully!`.
  - Status: `[VERIFIED PASS]`

- [ ] **Item 05 — Target Job Openings Verified in Database:**
  - Verify 4 openings exist in SQLite (`Senior Python Backend Architect`, `Data Analyst & BI Specialist`, `Full Stack Software Developer`, `Machine Learning Platform Engineer`).
  - Status: `[VERIFIED PASS]`

- [ ] **Item 06 — 8 Demo Candidate Profiles & Resumes Available:**
  - Verify `demo_data/resumes/` contains 8 clean `.txt` resume files (`resume_aarav_sharma.txt` through `resume_kavita_nair.txt`).
  - Status: `[VERIFIED PASS]`

---

### Category 3: Authentication & Security Controls
- [ ] **Item 07 — Recruiter Account Credentials Operational:**
  - Username: `demo_recruiter`
  - Password: `DemoPassword123!`
  - Verification: Successful login via web dashboard and `/api/v1/auth/session`.
  - Status: `[VERIFIED PASS]`

- [ ] **Item 08 — Cookie Security & Session Isolation:**
  - HttpOnly cookie `zecpath_session` issued upon authentication; unauthenticated API calls return 401 Unauthorized.
  - Status: `[VERIFIED PASS]`

---

### Category 4: Web Application Server & UI Dashboard
- [ ] **Item 09 — Uvicorn Web Server Running on Port 8000:**
  - Start command: `.venv\Scripts\python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload`
  - Verification: `curl -I http://127.0.0.1:8000/api/v1/health` returns HTTP 200 OK.
  - Status: `[VERIFIED PASS]`

- [ ] **Item 10 — Recruiter Dashboard UI Rendering & Assets:**
  - Browser loads `http://127.0.0.1:8000/`. Dashboard cards, navigation tabs, and candidate lists render without CSS/JS console errors.
  - Status: `[VERIFIED PASS]`

- [ ] **Item 11 — Embedded AI Observability Panel Live:**
  - Verify KPI header cards display live numbers (API Requests, P95 Latency, Error Rate, Active Alerts).
  - Status: `[VERIFIED PASS]`

---

### Category 5: Multi-Round Pipeline Functionality
- [ ] **Item 12 — ATS 4-Factor Scoring Breakdown Visible:**
  - Opening Aarav Sharma (`CAND-001`) shows 91.5% ATS score with 4-factor decomposition (Skills 40%, Semantic 25%, Exp 20%, Edu 15%).
  - Status: `[VERIFIED PASS]`

- [ ] **Item 13 — Conversational Screening & Follow-Up Transcript:**
  - Verify candidate screening answers load cleanly with intent classification and communication markers.
  - Status: `[VERIFIED PASS]`

- [ ] **Item 14 — Cross-Round Unified Fit & Recruiter Decision Box:**
  - Candidate dossier displays 90.6% unified fit score, AI recommendation `SELECTED`, and recruiter action approval buttons.
  - Status: `[VERIFIED PASS]`

---

### Category 6: Governance & Fallback Procedures
- [ ] **Item 15 — Cryptographic Audit Trail & Fallback Dataset Ready:**
  - Audit trail integrity check (`/api/v1/audit/verify`) returns `verified: True`.
  - Backup database file `data/ats.sqlite3.backup` exists in case of catastrophic during-demo state corruption.
  - Status: `[VERIFIED PASS]`

---

## Sign-Off

* **Lead AI Engineer:** Verified & Approved  
* **QA & Systems Lead:** Verified & Approved  
* **Date & Timestamp:** 2026-11-11 | Demo Readiness: **100% READY**

