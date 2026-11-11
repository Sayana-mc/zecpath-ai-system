# Day 53–60 API & Integration Planning — ZecPath AI Hiring System

## Overview

Days 53–60 introduce production REST endpoints to support advanced hiring analytics, security governance, end-to-end recruitment simulations, and high-concurrency batch processing.

---

## 1. New API Endpoints Reference

### Hiring Intelligence Reports
- `POST /api/v1/candidates/{candidate_id}/hiring-intelligence-report`
  - Generates a new multi-round Hiring Intelligence Report, saves it to SQLite, and returns the full JSON representation.
- `GET /api/v1/candidates/{candidate_id}/hiring-intelligence-report`
  - Retrieves the most recently generated intelligence report for the candidate.
- `GET /api/v1/candidates/{candidate_id}/hiring-intelligence-report/history`
  - Returns a list of all historical versions of intelligence reports generated for the candidate.
- `GET /api/v1/hiring-intelligence-reports/{report_id}/html`
  - Streams the formatted HTML document for display, print, or download.
- `GET /api/v1/hiring-intelligence-reports/{report_id}/markdown`
  - Streams the report formatted in standard Markdown (`text/markdown`).

### Security & Governance
- `GET /api/v1/audit/events`
  - Retrieves paginated audit log events from the cryptographic ledger.
- `GET /api/v1/audit/verify`
  - Traverses the entire audit log and verifies SHA-256 hash-chain integrity. Returns verification status, total events checked, and error details if tampering is detected.

### Candidate AI Coaching
- `POST /api/v1/candidates/{candidate_id}/coaching`
  - Generates developmental candidate coaching guidance based on interview records and persists it.
- `GET /api/v1/candidates/{candidate_id}/coaching`
  - Retrieves the latest coaching recommendations and practice questions for the candidate.

### Simulation & Benchmarking
- `POST /api/v1/simulation/run`
  - Executes the full 15-stage recruitment lifecycle for a synthetic or actual candidate.
- `POST /api/v1/simulation/benchmark`
  - Compares AI scoring rubrics against human recruiter evaluations across 5 stages, returning mean absolute error and alignment rates.

### Performance & Batch Processing
- `POST /api/v1/resumes/batch-process`
  - Accepts a batch of candidate resumes with configurable `batch_size` and `max_concurrency` parameters, returning parallelized extraction results and latency benchmarks.

---

## 2. Authentication & Authorization

All Day 53–60 endpoints require an authenticated recruiter session cookie (`zecpath_session`). Non-authenticated requests receive `401 Unauthorized`.
Endpoints modifying retention or inspecting cryptographic chains additionally check RBAC roles.

