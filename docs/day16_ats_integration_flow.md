# Day 16 — ATS Integration Flow

## Overview

This document describes the end-to-end data flow for the ATS subsystem integrated into the root ZecPath application. The flow covers the complete recruiter workflow from job creation to candidate shortlisting.

## Architecture Components

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Recruiter  │────▶│  FastAPI    │────▶│  Services   │────▶│  SQLite DB  │
│  Dashboard  │     │   Router    │     │   Layer     │     │  Persistence│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Auth/Session│    │  AI Engines │
                    │  Middleware  │    │  (Day 9-13) │
                    └─────────────┘     └─────────────┘
```

## Data Flow Sequences

### 1. Job Creation & Description Parsing

```
Recruiter → POST /openings/parse-description
    │
    ▼
JobDescriptionParser.parse_job_description()
    │
    ├── Extracts: required_skills, preferred_skills
    ├── Extracts: minimum_education, minimum_years_experience
    ├── Returns: evidence (source text lines), warnings
    └── human_confirmation_required: true
    │
    ▼
Recruiter reviews → POST /openings (confirmed values)
    │
    ▼
Database: openings table (OPEN status)
```

**Key Points:**
- Parser is conservative: only explicit headings
- No inference from free text
- Recruiter must confirm before saving

---

### 2. Candidate Application

```
Candidate/Recruiter → POST /candidates
    │
    ▼
Validation: opening exists, OPEN, email unique per opening
    │
    ▼
Database: candidates table (APPLIED status)
    ├── skills: candidate-reported
    ├── location, relocation_willingness, work_mode_preference
    ├── availability_date
    └── resume_text: empty initially
```

---

### 3. Resume Upload & Processing

```
Recruiter → POST /resumes/upload (multipart)
    │
    ├── Validates: file type (PDF/DOCX/TXT), size (≤5 MiB)
    ├── Validates: candidate_id exists (if provided)
    │
    ▼
Saves file to uploads/{job_id}.{ext}
Creates processing_jobs record (QUEUED)
    │
    ▼
Background Task: process_resume_job()
    │
    ├── UPDATE status: PROCESSING
    ├── parse_resume() → extracted text
    ├── extract_resume_data() → structured data
    │   ├── skills
    │   ├── experience_years, experience[]
    │   ├── education[]
    │   └── certifications[]
    │
    ├── UPDATE candidate: resume_filename, resume_text, resume_data
    │   CLEAR score & score_evidence (invalidate)
    │
    ├── UPDATE processing_jobs: COMPLETED with result
    │
    └── Cleanup: delete temp file
```

**Error Handling:**
- InvalidResumeError → FAILED with message
- Any exception → FAILED with generic message
- Candidate deleted during processing → FAILED

---

### 4. Resume Parse Retrieval

```
Recruiter → POST /resumes/parse {job_id}
    │
    ▼
GET processing_jobs
    │
    ├── status != COMPLETED → 409 error
    ├── No parsed_text → 410 error
    │
    ▼
Returns: parsed_text, extracted_data (resume_data)
```

---

### 5. ATS Scoring

```
Recruiter → POST /candidates/score {candidate_id, job_id}
    │
    ├── Validates: candidate exists, belongs to job
    │
    ▼
calculate_candidate_match() [Day 9-11 services]
    │
    ├── Skill matching (exact + fuzzy)
    ├── Experience relevance
    └── Education alignment
    │
    ▼
calculate_integrated_score() [Day 12-13]
    │
    ├── skill_match_score (configured weights)
    ├── experience_relevance_score
    ├── education_alignment_score
    ├── semantic_similarity (Day 12 embeddings)
    │   └── Requires readable resume text
    │
    └── generate_score_breakdown() [Day 13 weighted formula]
    │
    ▼
Persist: candidate.score, candidate.score_evidence
    ├── scored_at timestamp
    ├── scoring_version: "day9-12-13-v1"
    ├── components breakdown
    ├── matched/missing required skills
    ├── education_details, experience_details
    └── fairness_safeguards metadata
    │
    ▼
Compute ranking among scored candidates for this job
    │
    ▼
Returns: ScoreResponse with evidence, ranking, human_review_required
```

**Scoring Pipeline:**
1. Day 9: Skill extraction from resume
2. Day 10: Experience parsing & relevance
3. Day 11: Education/certification parsing
4. Day 12: Semantic matching (embeddings)
5. Day 13: Weighted ATS formula

**Model Dependency:**
- Day 12 requires sentence-transformers + all-MiniLM-L6-v2 cached locally
- Unavailable → 503 Service Unavailable

---

### 6. Shortlisting

```
Recruiter → POST /openings/{opening_id}/shortlist {minimum_score}
    │
    ▼
GET candidates for opening WHERE score IS NOT NULL AND score ≥ minimum_score
    │
    ▼
Sort by score DESC, name ASC
    │
    ▼
Assign rank (1-based)
    │
    ▼
Returns: ShortlistResponse
    ├── status: REVIEW_SUGGESTIONS_READY
    ├── shortlisted_count
    ├── candidates: [{candidate_id, score, rank}]
    ├── human_review_required: true
    └── simulation_only: false
```

---

### 7. Eligibility Evaluation

```
Recruiter → PUT /openings/{opening_id}/eligibility-config {configuration}
    │
    ▼
Persist: eligibility_configurations (versioned)
    │
    ▼
Recruiter → POST /candidates/{candidate_id}/eligibility/evaluate {opening_id}
    │
    ├── Validates: candidate belongs to opening
    ├── GET eligibility configuration
    │
    ▼
evaluate_eligibility() [src/eligibility.py]
    │
    ├── Fingerprint: candidate_id, candidate.updated_at, score, score_evidence,
    │                opening_id, opening.updated_at, configuration.version
    │
    ├── Check: current ATS score available & timestamped
    ├── Check: mandatory skills (profile ∪ resume extraction)
    ├── Check: experience_years from resume_data
    ├── Check: location/work_mode/relocation/availability
    │
    ├── explicit_failures → REJECTED
    ├── missing_information/review_reasons → REVIEW
    └── all_pass → ELIGIBLE
    │
    ▼
Persist: eligibility_evaluations (with fingerprint)
    │
    ▼
Returns: EligibilityEvaluationResponse
```

**Fingerprint Re-evaluation:**
- GET /candidates/{candidate_id}/eligibility compares fingerprint
- Changes to candidate, opening, score, or config → re-evaluate
- Same fingerprint → return cached evaluation

---

### 8. Screening Questions

```
Recruiter → GET /screening/questions?role_id=DATA_ANALYST&language=en
    │
    ▼
load_dataset() → validates & caches data/screening/hr_screening_questions.json
    │
    ▼
Filters: role_id, category, language, mandatory, active_only
    │
    ▼
For each question:
    ├── Get translation for requested language
    ├── Skip if translation.status != "AVAILABLE"
    └── Replace question_text with translated text
    │
    ▼
Returns: filtered, translated question list
```

---

### 9. Screening Session & Transcript

```
Recruiter → POST /screening/sessions {candidate_id, opening_id, language, source}
    │
    ├── Validates: candidate belongs to opening
    │
    ▼
Creates: screening_sessions (CREATED status)
    │
    ▼
Recruiter → PATCH /screening/sessions/{session_id} {status: IN_PROGRESS}
    │
    ▼
Recruiter → POST /screening/sessions/{session_id}/segments [...]
    │
    ├── Validates: session IN_PROGRESS or INTERRUPTED
    ├── Validates: sequence numbers strictly increasing from 1
    ├── Validates: speaker enum, confidence 0-1, timezone-aware timestamps
    ├── Validates: question_id exists in dataset (if provided)
    │
    ▼
For each segment:
    ├── normalized_text = " ".join(raw_text.split())
    ├── Persist: transcript_segments
    │
    ▼
Recruiter → POST /screening/sessions/{session_id}/interactions {...}
    │
    ├── Validates: question_id exists
    ├── Validates: follow_up_to exists (if provided)
    ├── Validates: display_order unique per session
    │
    ▼
Persist: screening_interactions
    │
    ▼
Recruiter → PATCH /screening/sessions/{session_id} {status: COMPLETED}
    │
    ▼
GET /screening/sessions/{session_id}
    │
    ├── Returns: session, segments[], interactions[]
```

---

### 10. Screening Report (Day 25 Integration)

```
Recruiter → POST /candidates/{candidate_id}/screening-reports {answers[]}
    │
    ▼
For each answer:
    ├── AnswerUnderstandingEngine.understand()
    │   ├── detected_intent
    │   ├── answer_status
    │   └── extracted_information
    │
    ├── Build review_flags for non-valid status or intent mismatch
    │
    ▼
Persist: screening_reports
    │
    ▼
Returns: ScreeningReportResponse
    ├── human_review_required: true
    └── review_flags[]
```

---

## Data Invalidation Rules

| Trigger | Invalidated Data |
|---------|------------------|
| Resume upload/replace | candidate.score, candidate.score_evidence |
| Candidate skills update | candidate.score, candidate.score_evidence |
| Candidate name update | candidate.score, candidate.score_evidence |
| Opening required_skills update | All candidates' score, score_evidence for that opening |
| Opening preferred_skills update | All candidates' score, score_evidence for that opening |
| Opening minimum_years_experience update | All candidates' score, score_evidence for that opening |
| Opening minimum_education update | All candidates' score, score_evidence for that opening |

---

## Async Processing Model

**Current Implementation:** FastAPI BackgroundTasks
- Runs in same process
- No persistence across restarts (interrupted jobs marked FAILED on startup)
- Suitable for development/single-instance deployment

**Limitations:**
- No retry semantics
- No horizontal scaling
- No durability guarantees

**Future Migration Path:** Redis + Celery or similar durable queue

---

## Security Boundaries

1. **Authentication:** All ATS endpoints require valid recruiter session
2. **Authorization:** Candidate/job ownership validated on every operation
3. **File Upload:** Type validation, size limit, secure storage outside web root
4. **SQL Injection:** Parameterized queries via sqlite3
5. **Rate Limiting:** Login attempts limited per IP/username
6. **Session Security:** HttpOnly, Secure, SameSite=Strict cookies

---

## Integration with Day 1-15 Components

| Day | Component | Integration Point |
|-----|-----------|-------------------|
| 5 | Resume text extraction | `parse_resume()` in background job |
| 8 | Section segmentation | `extract_resume_data()` scopes extraction |
| 9 | Skill extraction | `skill_match_score()` in scoring |
| 10 | Experience parsing | `experience_relevance_score()` |
| 11 | Education parsing | `education_alignment_score()` |
| 12 | Semantic matching | Embeddings in `calculate_integrated_score()` |
| 13 | ATS scoring | `generate_score_breakdown()` |
| 14 | Candidate ranking | Shortlist endpoint sorting |
| 15 | Fairness | Semantic input masking, human_review_required |