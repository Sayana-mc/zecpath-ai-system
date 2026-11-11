# ZecPath AI Hiring System — Master Technical Handbook

**Version:** 2.0.0  
**Target Architecture:** Complete Integrated AI Recruitment Platform (Days 1–70)  
**Project Location:** `C:\Users\sayan\Documents\zecpath-ai-system`  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [System Objectives](#3-system-objectives)
4. [Technology Stack](#4-technology-stack)
5. [System Architecture](#5-system-architecture)
6. [Root Application Structure](#6-root-application-structure)
7. [Backend Architecture](#7-backend-architecture)
8. [Frontend Architecture](#8-frontend-architecture)
9. [Database Design](#9-database-design)
10. [Authentication & Authorization](#10-authentication--authorization)
11. [Resume Upload & Parsing](#11-resume-upload--parsing)
12. [Skill Extraction](#12-skill-extraction)
13. [Experience & Education Analysis](#13-experience--education-analysis)
14. [Semantic Matching Engine](#14-semantic-matching-engine)
15. [ATS Scoring Methodology](#15-ats-scoring-methodology)
16. [Eligibility Evaluation Engine](#16-eligibility-evaluation-engine)
17. [Voice & Text HR Screening Engine](#17-voice--text-hr-screening-engine)
18. [Structured HR Interview Engine](#18-structured-hr-interview-engine)
19. [Technical Depth Evaluation Engine](#19-technical-depth-evaluation-engine)
20. [Machine Coding Test Engine](#20-machine-coding-test-engine)
21. [Unified Cross-Round Scoring](#21-unified-cross-round-scoring)
22. [Explainable Final Recommendation AI](#22-explainable-final-recommendation-ai)
23. [Hiring Intelligence Reports](#23-hiring-intelligence-reports)
24. [AI Monitoring & Observability](#24-ai-monitoring--observability)
25. [Cryptographic Audit Logging](#25-cryptographic-audit-logging)
26. [API Integration & Contracts](#26-api-integration--contracts)
27. [Security & Responsible AI Governance](#27-security--responsible-ai-governance)
28. [Testing Architecture](#28-testing-architecture)
29. [Known Limitations](#29-known-limitations)
30. [Future AI Roadmap](#30-future-ai-roadmap)

---

## 1. Project Overview

The **ZecPath AI Hiring System** is an enterprise-grade, end-to-end recruitment intelligence platform designed to automate, evaluate, and explain every stage of the talent acquisition lifecycle. Built entirely with Python, FastAPI, SQLite, and vanilla modern JavaScript, ZecPath unifies resume parsing, semantic matching, pre-screening eligibility, conversational voice screening, structured behavioral/HR interviews, deep technical assessments, and machine coding tests into a cohesive, explainable hiring intelligence report.

---

## 2. Problem Statement

Modern talent acquisition teams face several compounding challenges:
- **Volume Overload:** Hundreds of resumes per job opening overwhelm human recruiters, leading to superficial reviews and missed talent.
- **Keyword-Only ATS Fragility:** Legacy Applicant Tracking Systems reject qualified candidates due to minor phrasing differences or lack of exact keyword matches.
- **Fragmented Evaluation Stages:** Screening, technical interviews, and coding tests typically live in disjointed tools with no unified fit scoring.
- **Black-Box AI Decisions:** Opaque AI systems that reject candidates without explainable evidence violate regulatory frameworks (e.g., EEOC, EU AI Act).
- **Inconsistent Evaluations:** Different interviewers apply disparate standards, leading to biased, uncalibrated hiring choices.

---

## 3. System Objectives

- **Complete Recruitment Pipeline:** Provide an uninterrupted workflow from resume upload to final recruiter hire decision.
- **Explainability & Evidence:** Every score, recommendation, and shortlist must be backed by transparent, traceable evidence (matched skills, interview transcripts, code test metrics).
- **Human Recruiter Primacy:** The AI functions as an assistive intelligence layer. Automated rejection is strictly prohibited; all final employment choices require human sign-off.
- **Privacy & Ethical Governance:** Prohibit demographic-based scoring, eliminate emotion-based disqualification, verify candidate consent, and enforce 180-day retention policies.
- **High Performance & Local Execution:** Run locally without mandatory external paid API dependencies using cached local embeddings (`all-MiniLM-L6-v2`) and thread-safe in-memory caching.

---

## 4. Technology Stack

- **Backend Runtime:** Python 3.12 (Python 3.12.4).
- **Web Framework:** FastAPI, Starlette, AnyIO, Uvicorn.
- **Data Validation & Schemas:** Pydantic v2.
- **Database & Storage:** SQLite3 with WAL mode, foreign keys enabled, and indexed queries.
- **NLP & Embeddings:** HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`), local scikit-learn, regex tokenizers.
- **Document Extractors:** `python-docx` for `.docx`, `pypdf` for `.pdf`, native UTF-8 stream readers for `.txt`.
- **Frontend:** Vanilla HTML5, modern CSS3, and standard ECMAScript (no heavy node_modules build chain).
- **Testing:** `pytest`, `pytest-asyncio`, `starlette.testclient`.
- **Cryptography:** Python standard library `hashlib` (SHA-256) and `secrets`.

---

## 5. System Architecture

```mermaid
flowchart TD
    Client[Recruiter Dashboard Browser / API Clients] -->|HTTP / JSON| API[FastAPI Application Layer (src/main.py)]
    API --> Auth[Authentication & Session Guard (src/auth.py)]
    API --> Obs[Observability & Audit Subsystem (src/observability.py)]
    
    subgraph "Core Evaluation Engines"
        P[Resume Parser & Extractor (src/services.py, src/resume_analysis.py)]
        ATS[ATS Weighted Scorer (src/ats_scoring_engine.py)]
        SEM[Semantic Matcher (src/integrated_scoring.py)]
        ELIG[Eligibility Engine (src/eligibility.py)]
        SCR[Voice & Phone Screening (src/screening_pipeline.py)]
        HR[Structured HR Interview (src/hr_interview_engine.py)]
        TECH[Technical Depth Evaluator (src/technical_interview_engine.py)]
        CODE[Machine Test Engine (src/machine_test_engine.py)]
        CROSS[Cross-Round Unified Scorer (src/cross_round_scoring_engine.py)]
        REC[Final Recommendation AI (src/final_recommendation_engine.py)]
        REP[Hiring Intelligence Compiler (src/hiring_intelligence_report_generator.py)]
    end

    API --> Core Evaluation Engines
    Core Evaluation Engines --> DB[(SQLite Database: data/zecpath.sqlite3)]
    Core Evaluation Engines --> Cache[(In-Memory TTLCache / Rolling Buffers)]
```

---

## 6. Root Application Structure

```
zecpath-ai-system/
├── data/                       # Local SQLite databases (zecpath.sqlite3)
├── demo_data/                  # Synthetic demo job descriptions, candidates, and resumes
├── docs/                       # Comprehensive technical reports and handbooks
├── logs/                       # Privacy-guarded structured JSONL logs
├── presentation/               # Presentation slides, demo script, and stakeholder Q&A
├── src/                        # Root application source code
│   ├── api.py                  # Consolidated REST API router
│   ├── auth.py                 # Recruiter cookie authentication & session hashing
│   ├── batch_processing.py     # Async batch resume chunking & TTLCache
│   ├── coaching_engine.py      # Candidate developmental AI coaching
│   ├── cross_round_scoring_engine.py # 5-round unified scoring
│   ├── database.py             # SQLite schema, tables, and CRUD helpers
│   ├── eligibility.py          # Pre-screening eligibility decision engine
│   ├── final_recommendation_engine.py # Explainable recommendation engine
│   ├── hiring_intelligence_report_generator.py # 15-section report compiler
│   ├── hr_interview_engine.py  # Structured HR interview engine
│   ├── integrated_scoring.py   # Semantic embedding matching
│   ├── main.py                 # FastAPI application root & middleware
│   ├── observability.py        # Logging, metrics, alerting & decision audit
│   ├── optimization_engine.py  # Confusion matrix & contradiction detection
│   ├── resume_analysis.py      # Section segmentation & skill parsing
│   ├── schemas.py              # Pydantic request & response models
│   ├── security_governance.py  # SHA-256 audit chaining & RBAC
│   ├── services.py             # High-level ATS & resume parsing services
│   ├── simulation_pipeline.py  # 15-stage recruitment lifecycle simulator
│   └── technical_interview_engine.py # Technical depth & coding tests
├── static/                     # Recruiter dashboard UI (index.html)
├── submission/                 # Final internship submission deliverables
└── tests/                      # Automated test suite (101 tests across Days 1–70)
```

---

## 7. Backend Architecture

FastAPI provides an asynchronous request processing pipeline. The backend is configured with:
- Strict CORS and Same-Origin validation for write operations (`POST`, `PATCH`, `DELETE`).
- Centralized exception handlers for graceful `400`, `401`, `403`, `404`, and `422` error formatting.
- `lifespan` context manager that initializes SQLite tables, creates default indexes, and safely fails interrupted background jobs.
- Asynchronous HTTP middleware logging all `/api/` requests directly to `ObservabilityEngine`.

---

## 8. Frontend Architecture

The user interface in [`static/index.html`](file:///c:/Users/sayan/Documents/zecpath-ai-system/static/index.html) is a single-page responsive dashboard communicating via same-origin relative `/api/v1` routes:
- **Authentication View:** Displays when unauthenticated; handles credential submission, session cookies, and login throttling.
- **Job Opening Workspace:** Creation, editing, eligibility rule configuration, and job deletion.
- **Application Management:** Candidate registration, multi-format resume drag-and-drop, and application status filtering.
- **Evaluation Drawers:** Real-time ATS match breakdown, AI HR interview cards, technical depth metrics, candidate coaching drawers, and complete hiring intelligence reports with HTML/Markdown export.
- **System Observability Panel:** Real-time KPI cards tracking operational throughput, P95 latency, AI model inferences, decision audit counts, and active health alert banners.

---

## 9. Database Design

The relational SQLite schema enforces data integrity through foreign keys with cascading deletions:
- `recruiter_accounts`: Salted SHA-256 recruiter credentials and lockouts.
- `openings`: Job title, description, required/preferred skills, education, experience, status.
- `candidates`: Profile information, reported skills, email, status.
- `candidate_resumes`: Extracted raw text, parsed JSON metadata, checksums.
- `candidate_scores`: ATS match scores, evidence JSON, classification tiers.
- `eligibility_configurations` & `eligibility_evaluations`: Versioned pre-screening rules and audit results.
- `screening_sessions` & `screening_aggregate_scores`: Voice screening sessions and scores.
- `hr_interview_sessions`, `hr_interview_questions`, `hr_interview_scores`: Structured behavioral interview rounds.
- `technical_interview_sessions` & `technical_interview_responses`: Depth classifications and skill evaluations.
- `machine_test_assignments` & `machine_test_submissions`: Coding test problem instances and automated grading.
- `cross_round_evaluations` & `final_recommendations`: Unified multi-round percentage scores and AI recommendations.
- `hiring_intelligence_reports`: Multi-round comprehensive report archives with versioning (`1.0`, `1.1`).
- `audit_events`: Tamper-evident cryptographic ledger linked via SHA-256 hash chains.
- `candidate_coaching_records`: Growth-oriented candidate guidance and practice questions.

---

## 10. Authentication & Authorization

- **Credential Security:** Passwords hashed with unique per-account random salts using `hashlib.pbkdf2_hmac` (`sha256`, 100,000 iterations).
- **Session Tokens:** 32-byte cryptographically secure random tokens (`secrets.token_hex`), hashed with SHA-256 before storage in SQLite.
- **Cookie Security:** Delivered in `SameSite=Strict`, `HttpOnly` cookies expiring in 8 hours.
- **Brute-Force Protection:** 5 consecutive failed login attempts trigger an automatic 15-minute client address lockout.
- **Role-Based Access Control (RBAC):** Distinct permission tiers for `admin`, `lead_recruiter`, `recruiter`, `interviewer`, and `auditor`.

---

## 11. Resume Upload & Parsing

- **Supported File Types:** Plain Text (`.txt`), Microsoft Word (`.docx`), text-based PDF (`.pdf`).
- **File Validation:** Size-capped at 5 MiB; strict MIME-type and extension inspection.
- **Security:** Uploaded binary files are parsed in-memory or in temporary files and immediately deleted after text extraction; raw binaries are never permanently retained.

---

## 12. Skill Extraction

- **Pattern Matching:** Case-insensitive phrase boundary tokenization matching both exact names and standardized aliases (e.g., "Postgres" -> "PostgreSQL", "JS" -> "JavaScript").
- **Classification:** Distinguishes core programming languages, frameworks, cloud infrastructure, databases, and DevOps tools.

---

## 13. Experience & Education Analysis

- **Experience Parser:** Extracts chronological company tenures, computes total verified years, and detects senior/lead seniority indicators.
- **Education Parser:** Recognizes degrees (B.Tech, B.S., M.S., Ph.D., MCA), fields of study, and graduation years.

---

## 14. Semantic Matching Engine

- **Model:** Local `sentence-transformers/all-MiniLM-L6-v2`.
- **Cos-Similarity:** Encodes resume work experience and job requirement descriptions into 384-dimensional dense vectors, computing cosine similarity.
- **Privacy Guard:** Demographic personal details (names, contact info, personal pronouns) are stripped prior to vector embedding generation.

---

## 15. ATS Scoring Methodology

The weighted ATS score (0–100) is computed as follows:
- **Skill Match (40%):** Weighted overlap between candidate skills and required/preferred opening skills.
- **Semantic Text Relevance (25%):** Embedding cosine similarity between resume text and job description.
- **Experience Relevance (20%):** Proximity of candidate experience years to target role requirements.
- **Education Alignment (15%):** Degree level alignment against minimum specified educational criteria.

---

## 16. Eligibility Evaluation Engine

- **Configurable Rules:** Minimum ATS score, mandatory skills, experience bounds (min/max), location restrictions, work-mode constraints (ONSITE/HYBRID/REMOTE).
- **Evaluation Statuses:** `ELIGIBLE`, `INELIGIBLE`, `REVIEW_REQUIRED` (triggered when required evidence is absent or uncertain).

---

## 17. Voice & Text HR Screening Engine

- **Conversational State Machine:** Manages question sequences, introduction, core questions, clarification, and closing.
- **Audio Processing:** Audio ingestion (WAV, MP3, M4A, OGG), STT transcript cleaning (filler word stripping, punctuation normalization).
- **Communication Analysis:** Pacing (WPM), speech hesitation markers, clarity scoring, and relevance scoring.

---

## 18. Structured HR Interview Engine

- **Adaptive Questioning:** Role-specific question selection tailored to candidate experience level (`FRESHER` vs. `EXPERIENCED`).
- **Dynamic Follow-Ups:** Evaluates initial answer completeness and generates contextual follow-up inquiries.
- **Behavioral Evaluation:** Evaluates communication clarity, structural articulation, situational judgment, and aptitude.

---

## 19. Technical Depth Evaluation Engine

- **Depth Classification:** Categorizes technical answers into `shallow` (superficial keywords), `moderate` (correct general explanation), or `deep` (architectural tradeoffs, failure modes, implementation internals).
- **Evaluation Dimensions:** Accuracy, depth, reasoning, and practical applicability.

---

## 20. Machine Coding Test Engine

- **Archetypes:** Algorithmic coding, system design, bug fixing, SQL query optimization.
- **Automated Grading:** Test case correctness, execution time efficiency, code quality metrics, problem-solving, and time management.

---

## 21. Unified Cross-Round Scoring

- **5-Round Aggregation:** Synthesizes scores from ATS, HR Screening, HR Interview, Technical Interview, and Machine Test.
- **Dynamic Re-weighting:** If an optional round is missing, the `exclude_and_renormalize` policy redistributes weights proportionally among completed rounds.
- **Anomaly Detection:** Flags significant score contradictions between rounds (e.g., ATS 95% vs Technical 40%).

---

## 22. Explainable Final Recommendation AI

- **Recommendation Tiers:** `SELECTED`, `HOLD_REVIEW`, `REJECTED`.
- **Evidence Confidence:** Metric between 0.00 and 1.00 reflecting evaluation completeness.
- **Auditable Rationale:** Specific bullet-point reasons citing concrete strengths, risks, and round performances.

---

## 23. Hiring Intelligence Reports

- **Compilation:** Synthesizes all 11 evaluation dimensions into an archived record.
- **Export Capabilities:** Structured JSON, clean Markdown, and polished standalone HTML with modern CSS cards.
- **Versioning:** Incremental report versioning (`1.0`, `1.1`).
- **Human-in-the-Loop Safeguard:** Mandatory advisory notice emphasizing human recruiter responsibility for final decisions.

---

## 24. AI Monitoring & Observability

- **Structured Logging:** Privacy-safe `.jsonl` logging under `logs/`.
- **Operational Metrics:** Request throughput, failure rates, P50/P95 response latency, model execution times.
- **Alerting Engine:** Threshold-based alerts for elevated latency, high failure rates, and database errors.
- **Monitoring UI:** Real-time recruiter dashboard panel.

---

## 25. Cryptographic Audit Logging

- **SHA-256 Hash Chaining:** Every recruitment event is cryptographically linked to the preceding event hash.
- **Tamper Evidence:** Verification function traverses the log and flags any manual edits, deletions, or data corruption.

---

## 26. API Integration & Contracts

All endpoints follow strict REST principles under `/api/v1` with Pydantic request/response validation:
- Authentication & Sessions: `/api/v1/auth/*`
- Job Openings: `/api/v1/openings/*`
- Candidates & Applications: `/api/v1/candidates/*`
- Resume Ingestion & Batching: `/api/v1/resumes/*`
- Eligibility: `/api/v1/eligibility/*`
- Screening: `/api/v1/screening/*`
- HR Interviews: `/api/v1/hr-interviews/*`
- Technical Assessments: `/api/v1/technical/*`
- Machine Tests: `/api/v1/machine-tests/*`
- Cross-Round Scoring & Recommendations: `/api/v1/cross-round/*`
- Hiring Reports: `/api/v1/hiring-intelligence-reports/*`
- Observability & Audit: `/api/v1/monitoring/*`, `/api/v1/audit/*`
- Simulation & Benchmarking: `/api/v1/simulation/*`

---

## 27. Security & Responsible AI Governance

- **Advisory Only:** No candidate is ever rejected automatically by an AI algorithm.
- **Anti-Bias Demographics Scrubber:** Filters names, gender, pronouns, age, and contact markers from model inputs.
- **Prohibition of Tone & Emotion Disqualification:** Disallows rejection based on pitch or sentiment inflections.
- **Data Retention:** Enforces 180-day automated purge manifests compliant with GDPR.

---

## 28. Testing Architecture

- **Suite Size:** 101 automated tests across 12 test suites.
- **Pass Rate:** 100% (101 passed, 0 failed).
- **Execution Speed:** ~65 seconds for full system regression.

---

## 29. Known Limitations

- **Local Prototype Scope:** Uses SQLite and single-node in-memory concurrency.
- **Scanned Document OCR:** PDF parsing requires embedded text layers; scanned images require external OCR libraries (e.g., Tesseract).
- **Speech Ingestion:** STT transcript evaluation processes text representations; real-time streaming audio requires external WebRTC/LiveKit integrations.

---

## 30. Future AI Roadmap

- **Phase 1:** Real-time bi-directional voice streaming via WebRTC.
- **Phase 2:** Distributed background workers with Celery/Redis and PostgreSQL with `pgvector`.
- **Phase 3:** Autonomous recruiter copilot for natural language candidate search.

