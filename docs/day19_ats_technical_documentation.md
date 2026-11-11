# Day 19 — ATS Technical Documentation

## System Overview

The ZecPath ATS (Applicant Tracking System) is an AI-powered recruitment support system integrated into the root FastAPI application (`src/main.py`). It automates resume processing, candidate information extraction, candidate-job matching, scoring, ranking, and decision support.

**Key Principle:** Every automated decision requires human review (`human_review_required: true`).

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ZECPATH ATS ROOT APPLICATION                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌────────────────────────────────┐   │
│  │  HTTP    │───▶│  FastAPI     │───▶│  Service Layer                 │   │
│  │  Requests│    │  Router      │    │  (src/services.py,             │   │
│  └──────────┘    │  + Auth      │    │   src/eligibility.py,          │   │
│                  └──────────────┘    │   src/screening_questions.py)  │   │
│                       │              └────────────────────────────────┘   │
│                       ▼                           │                       │
│              ┌──────────────┐                    ▼                       │
│              │  SQLite DB   │    ┌────────────────────────────────┐     │
│              │  (Persistence)   │  AI/ML Engines                 │     │
│              └──────────────┘    │  (Day 9-13, external modules)  │     │
│                       │          └────────────────────────────────┘     │
│                       ▼                           │                       │
│              ┌──────────────┐                    ▼                       │
│              │  Background  │    ┌────────────────────────────────┐     │
│              │  Tasks       │    │  External Dependencies         │     │
│              └──────────────┘    │  - sentence-transformers       │     │
│                                   │  - all-MiniLM-L6-v2 (cached)   │     │
│                                   │  - pymupdf (PDF)               │     │
│                                   │  - python-docx (DOCX)          │     │
│                                   └────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Modules

| Module | File | Responsibility |
|--------|------|----------------|
| API Routes | `src/api.py` | HTTP endpoints, validation, auth |
| Schemas | `src/schemas.py` | Pydantic request/response models |
| Database | `src/database.py` | SQLite persistence, migrations |
| Authentication | `src/auth.py` | Recruiter sessions, password hashing |
| Services | `src/services.py` | Resume parsing, matching, shortlisting |
| Resume Analysis | `src/resume_analysis.py` | Data extraction orchestration |
| Integrated Scoring | `src/integrated_scoring.py` | Day 9-13 scoring pipeline |
| Eligibility | `src/eligibility.py` | Rule-based eligibility evaluation |
| Screening Questions | `src/screening_questions.py` | Question bank loading/filtering |
| JD Parser | `src/job_description_parser.py` | Explicit-heading JD extraction |
| ATS Evaluation | `src/ats_evaluation.py` | Metric calculation helpers |

## Data Flow: Resume Processing Pipeline

```
1. UPLOAD
   POST /resumes/upload (multipart)
   ├── Validate: type, size, candidate_id
   ├── Save: uploads/{job_id}.{ext}
   ├── Create: processing_jobs (QUEUED)
   └── Background: process_resume_job()

2. EXTRACT (Background)
   process_resume_job()
   ├── Status: PROCESSING
   ├── parse_resume() → raw text
   │   ├── TXT: direct read
   │   ├── PDF: pymupdf (fitz)
   │   └── DOCX: python-docx
   ├── extract_resume_data() → structured data
   │   ├── Section segmentation (Day 8)
   │   ├── Skill extraction (Day 9)
   │   ├── Experience parsing (Day 10)
   │   ├── Education parsing (Day 11)
   │   └── Certifications
   ├── Update: candidate (resume_text, resume_data)
   │   └── Invalidate: score, score_evidence
   ├── Update: processing_jobs (COMPLETED + result)
   └── Cleanup: delete temp file

3. PARSE RETRIEVAL
   POST /resumes/parse {job_id}
   ├── Validate: job COMPLETED
   └── Return: parsed_text, extracted_data
```

## Data Flow: ATS Scoring Pipeline

```
POST /candidates/score {candidate_id, job_id}
    │
    ├── Validate: candidate exists, belongs to job
    │
    ▼
calculate_candidate_match() [services.py]
    │
    ├── Skill matching (exact + fuzzy via normalizer)
    ├── Experience relevance (years, recency, role match)
    └── Education alignment (degree level, field match)
    │
    ▼
calculate_integrated_score() [integrated_scoring.py]
    │
    ├── skill_match_score() [Day 13 params]
    ├── experience_relevance_score() [Day 13 params]
    ├── education_alignment_score() [Day 13 params]
    ├── Semantic similarity (Day 12)
    │   ├── Build matching text (skills + experience + education)
    │   ├── Build job text (title + desc + requirements)
    │   ├── Embed both (all-MiniLM-L6-v2)
    │   └── Cosine similarity → [0, 1]
    │
    └── generate_score_breakdown() [Day 13 weighted formula]
        ├── Role-specific weights
        ├── Component scores → weighted sum
        └── Classification (STRONG_MATCH, GOOD_MATCH, etc.)
    │
    ▼
Persist to candidate
    ├── score (float)
    ├── score_evidence (full breakdown)
    ├── scored_at (timestamp)
    └── scoring_version ("day9-12-13-v1")
    │
    ▼
Compute ranking among scored candidates for job
    │
    ▼
Return ScoreResponse
    ├── score, evidence, ranking
    ├── matched/missing required skills
    ├── education_details, experience_details
    ├── components breakdown
    └── human_review_required: true
```

## Data Flow: Eligibility Evaluation

```
PUT /openings/{opening_id}/eligibility-config
    │
    └── Persist: eligibility_configurations (versioned)
        │
POST /candidates/{candidate_id}/eligibility/evaluate {opening_id}
    │
    ├── Validate: candidate belongs to opening
    ├── GET: eligibility configuration
    │
    ▼
evaluate_eligibility() [eligibility.py]
    │
    ├── Fingerprint inputs (candidate, opening, score, config version)
    │
    ├── Rule: Minimum ATS Score
    │   ├── No current score → REVIEW
    │   ├── Score < minimum → REJECTED (explicit failure)
    │   └── Score ≥ minimum → PASS
    │
    ├── Rule: Mandatory Skills
    │   ├── Check: candidate.skills ∪ resume_data.skills
    │   ├── Missing → REVIEW (not proof of absence)
    │   └── All matched → PASS
    │
    ├── Rule: Experience Range
    │   ├── No parsed experience → REVIEW
    │   ├── < minimum → REJECTED
    │   ├── > maximum → REVIEW
    │   └── In range → PASS
    │
    ├── Rule: Location/Work Mode
    │   ├── Configured allowed_locations + remote_allowed + relocation_required
    │   ├── Candidate location/preference/relocation_willingness
    │   ├── Mismatch → REVIEW
    │   └── Match → PASS
    │
    ├── Rule: Availability
    │   ├── latest_start_date configured
    │   ├── Candidate availability_date
    │   ├── Later than required → REVIEW
    │   └── On time → PASS
    │
    ├── Decision Logic
    │   ├── Any explicit failure (REJECTED rule) → REJECTED
    │   ├── Any missing/uncertain → REVIEW
    │   └── All PASS → ELIGIBLE
    │
    └── Persist: eligibility_evaluations (with fingerprint)
        │
GET /candidates/{candidate_id}/eligibility
    │
    ├── Compare fingerprint
    ├── Changed → re-evaluate
    └── Same → return cached
```

## Database Schema

### Core Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `openings` | Job postings | opening_id, title, required_skills, preferred_skills, minimum_education, minimum_years_experience, status |
| `candidates` | Applications | candidate_id, name, email, opening_id, skills, resume_text, resume_data, resume_filename, application_status, score, score_evidence, location, relocation_willingness, work_mode_preference, availability_date |
| `processing_jobs` | Resume processing | job_id, filename, candidate_id, status, result, error, created_at |

### Eligibility Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `eligibility_configurations` | Per-job rules | opening_id, version, configuration_json, created_at, updated_at |
| `eligibility_evaluations` | Evaluation history | evaluation_id, candidate_id, opening_id, configuration_version, input_fingerprint, result_json, evaluated_at |

### Screening Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `screening_sessions` | Interview sessions | session_id, candidate_id, opening_id, status, language, started_at, completed_at, source, version |
| `transcript_segments` | Conversation turns | segment_id, session_id, question_id, speaker, raw_text, normalized_text, start_time, end_time, confidence, language, source, processing_version, sequence_number |
| `screening_interactions` | Q&A pairs | interaction_id, session_id, question_id, candidate_answer, answer_type, validation_status, display_order, follow_up_to |

### Auth Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `recruiter_accounts` | Single recruiter | username, password_salt, password_hash, created_at |
| `recruiter_sessions` | Active sessions | token_hash, username, expires_at, created_at |
| `recruiter_login_attempts` | Rate limiting | key_hash, attempts, window_started, blocked_until |

## API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/auth/session` | Login |
| GET | `/api/v1/auth/session` | Session status |
| DELETE | `/api/v1/auth/session` | Logout |
| POST | `/api/v1/openings/parse-description` | Parse JD |
| CRUD | `/api/v1/openings` | Job openings |
| CRUD | `/api/v1/candidates` | Candidate applications |
| POST | `/api/v1/resumes/upload` | Upload resume |
| GET | `/api/v1/jobs/{job_id}` | Processing status |
| POST | `/api/v1/resumes/parse` | Get parsed resume |
| POST | `/api/v1/candidates/score` | Calculate ATS score |
| POST | `/api/v1/openings/{id}/shortlist` | Generate shortlist |
| POST | `/api/v1/candidates/shortlist` | Demo shortlist |
| PUT/GET | `/api/v1/openings/{id}/eligibility-config` | Eligibility config |
| POST/GET | `/api/v1/candidates/{id}/eligibility` | Eligibility eval |
| GET | `/api/v1/screening/questions` | Filter questions |
| CRUD | `/api/v1/screening/sessions` | Screening sessions |
| POST | `/api/v1/screening/sessions/{id}/segments` | Add transcript |
| POST/GET | `/api/v1/screening/sessions/{id}/interactions` | Add/get interactions |
| POST | `/api/v1/candidates/{id}/screening-reports` | Screening report |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ZECPATH_DB_PATH` | `data/zecpath.sqlite3` | SQLite database path |
| `ZECPATH_UPLOAD_DIR` | `uploads/` | Resume upload directory |
| `ZECPATH_MAX_RESUME_MB` | `5` | Max resume size (MiB) |

### Scoring Weights (Day 13)

Defined in `day13_ats_scoring/src/scoring_parameters.py` — role-specific weight configurations for skill, experience, education, semantic components.

## External Dependencies

| Dependency | Purpose | Version Pinning |
|------------|---------|-----------------|
| `fastapi` | Web framework | Latest compatible |
| `uvicorn` | ASGI server | Latest compatible |
| `pydantic` | Validation | v2 |
| `sqlite3` | Database | Stdlib |
| `sentence-transformers` | Embeddings | Pinned in requirements |
| `all-MiniLM-L6-v2` | Embedding model | Local cache required |
| `pymupdf` | PDF extraction | Latest |
| `python-docx` | DOCX extraction | Latest |
| `pytest` | Testing | Latest |

## Security

- **Authentication:** Session cookies (HttpOnly, Secure, SameSite=Strict)
- **Authorization:** Ownership validation on every candidate/job operation
- **File Upload:** Type validation, size limit, storage outside web root
- **SQL Injection:** Parameterized queries only
- **Rate Limiting:** 5 login attempts per 15 min per IP/username
- **Passwords:** PBKDF2-HMAC-SHA256 with per-user salt

## Known Limitations

See `docs/day16_day23_known_limitations.md` for complete list.

Key limitations:
- No tenant isolation (single recruiter)
- No human-labeled evaluation data
- No production performance baseline
- Semantic model requires local cache
- Background tasks not durable across restarts
- Limited resume format coverage (PDF/DOCX extraction basic)

## Versioning

| Component | Version |
|-----------|---------|
| API | v1 (in URL path) |
| Scoring | `day9-12-13-v1` (in evidence) |
| Eligibility Config | Per-opening version counter |
| Screening Questions | Dataset version 1.0 |
| Transcript Processing | `transcript-v1` |

## Deployment

```bash
# Activate venv
. .venv/Scripts/Activate.ps1

# Run server
python -m src.main

# Or with uvicorn directly
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Testing

```bash
# Full suite
python -m pytest tests/ -v

# Focused ATS tests
python -m pytest tests/test_day16_day23.py tests/test_schemas.py -v

# Validate screening dataset
python -m src.validate_screening_dataset
```

## Related Documentation

- `docs/day16_ats_api_specification.md` — Complete API reference
- `docs/day16_ats_api_schemas.md` — Request/response schemas
- `docs/day16_ats_integration_flow.md` — Data flow sequences
- `docs/diagrams/day16_ats_api_flow.mmd` — Architecture diagram
- `docs/day17_ats_testing_report.md` — Test results
- `docs/day21_eligibility_decision_engine.md` — Eligibility details
- `docs/day22_hr_screening_dataset.md` — Question bank
- `docs/day23_transcript_data_architecture.md` — Transcript storage