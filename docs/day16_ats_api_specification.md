# Day 16 — ATS API Specification

## Overview

This document specifies the ATS API endpoints integrated into the root ZecPath application (`src/main.py`). The API is authenticated via recruiter session cookies and uses the existing FastAPI application.

## Base URL

All endpoints are prefixed with `/api/v1`.

## Authentication

All ATS endpoints (except `/auth/*` and `/health`) require a valid recruiter session cookie. See `src/auth.py` for session management.

## Endpoints

### 1. Health Check

**GET** `/api/v1/health`

Returns service health status.

**Response (200):**
```json
{
  "status": "healthy",
  "service": "ZecPath ATS API",
  "version": "1.0.0",
  "authentication_configured": true
}
```

**Response (503):** Database unavailable.

---

### 2. Recruiter Authentication

**POST** `/api/v1/auth/session`

Create a recruiter session.

**Request:**
```json
{
  "username": "recruiter@example.com",
  "password": "secure-password"
}
```

**Response (200):** Sets `zecpath_session` cookie.
```json
{
  "authenticated": true,
  "username": "recruiter@example.com",
  "expires_at": 1700000000.0
}
```

**GET** `/api/v1/auth/session`

Get current session status.

**DELETE** `/api/v1/auth/session`

Logout and revoke session.

---

### 3. Job Description Parsing

**POST** `/api/v1/openings/parse-description`

Parse a job description using explicit heading rules.

**Request:**
```json
{
  "description": "Required skills: Python, SQL\nPreferred skills: Tableau\nExperience: 3 years\nEducation: Bachelor's degree"
}
```

**Response (200):**
```json
{
  "required_skills": ["Python", "SQL"],
  "preferred_skills": ["Tableau"],
  "minimum_education": "Bachelor's degree",
  "minimum_years_experience": 3.0,
  "evidence": {
    "required_skills": ["Required skills: Python, SQL"],
    "preferred_skills": ["Preferred skills: Tableau"],
    "experience": ["Experience: 3 years"],
    "education": ["Education: Bachelor's degree"],
    "responsibilities": []
  },
  "warnings": [],
  "method": "explicit_heading_rules_v1",
  "human_confirmation_required": true
}
```

---

### 4. Job Openings CRUD

**POST** `/api/v1/openings` — Create opening (201)

**GET** `/api/v1/openings` — List openings (200)

**GET** `/api/v1/openings/{opening_id}` — Get opening (200)

**PATCH** `/api/v1/openings/{opening_id}` — Update opening (200)

**DELETE** `/api/v1/openings/{opening_id}` — Delete opening (204)

---

### 5. Candidate CRUD

**POST** `/api/v1/candidates` — Create candidate application (201)

**GET** `/api/v1/candidates` — List candidates (200)

**GET** `/api/v1/candidates/{candidate_id}` — Get candidate (200)

**PATCH** `/api/v1/candidates/{candidate_id}` — Update candidate (200)

**DELETE** `/api/v1/candidates/{candidate_id}` — Delete candidate (204)

---

### 6. Resume Upload

**POST** `/api/v1/resumes/upload`

Upload a resume file for processing.

**Request:** `multipart/form-data`
- `file`: Resume file (PDF, DOCX, TXT, max 5 MiB)
- `candidate_id` (optional): Associate with existing candidate

**Response (202):**
```json
{
  "job_id": "uuid",
  "filename": "resume.pdf",
  "candidate_id": "uuid",
  "status": "QUEUED",
  "message": "Resume accepted for processing."
}
```

**Errors:**
- 400: Unsupported format, empty file, type mismatch
- 413: File exceeds 5 MiB
- 404: Candidate not found

---

### 7. Resume Processing Status

**GET** `/api/v1/jobs/{job_id}`

Get processing job status.

**Response (200):**
```json
{
  "job_id": "uuid",
  "status": "COMPLETED|PROCESSING|FAILED|QUEUED",
  "result": {
    "candidate_id": "uuid",
    "parsed_text": "...",
    "resume_data": {...}
  },
  "error": null
}
```

---

### 8. Resume Parse Result

**POST** `/api/v1/resumes/parse`

Retrieve parsed resume text and extracted data.

**Request:**
```json
{
  "job_id": "uuid"
}
```

**Response (200):**
```json
{
  "job_id": "uuid",
  "status": "COMPLETED",
  "parsed_text": "extracted text...",
  "extracted_data": {
    "skills": ["Python", "SQL"],
    "experience_years": 3.0,
    "experience": [...],
    "education": [...]
  },
  "message": "Resume text extracted successfully."
}
```

**Errors:**
- 404: Job not found
- 409: Processing not completed
- 410: Extracted text no longer available

---

### 9. ATS Scoring

**POST** `/api/v1/candidates/score`

Calculate ATS score for a candidate against a job opening.

**Request:**
```json
{
  "job_id": "uuid",
  "candidate_id": "uuid"
}
```

**Response (200):**
```json
{
  "job_id": "uuid",
  "candidate_id": "uuid",
  "score": 78.5,
  "evidence": {
    "method": "day9_12_13_configured_weighted_score",
    "job_id": "uuid",
    "candidate_id": "uuid",
    "job_title": "Data Analyst",
    "candidate_name": "John Doe",
    "extracted_skills": ["Python", "SQL", "Tableau"],
    "scoring_skills": ["Python", "SQL", "Tableau"],
    "matching_required_skills": ["Python", "SQL"],
    "matched_required_skills": ["Python", "SQL"],
    "missing_required_skills": [],
    "matching_preferred_skills": ["Tableau"],
    "education_details": [...],
    "experience_details": {"years": 3.0, "roles": [...]},
    "components": {...},
    "weights": {...},
    "breakdown": {...},
    "classification": "STRONG_MATCH",
    "formula": "sum(component_score_0_to_100 * configured_role_weight)",
    "scoring_explanation": "...",
    "fairness_safeguards": {...},
    "human_review_required": true,
    "scored_at": "2026-01-01T00:00:00+00:00",
    "scoring_version": "day9-12-13-v1"
  },
  "job_title": "Data Analyst",
  "candidate_name": "John Doe",
  "extracted_skills": ["Python", "SQL", "Tableau"],
  "matching_required_skills": ["Python", "SQL"],
  "missing_required_skills": [],
  "education_details": [...],
  "experience_details": {...},
  "components": {...},
  "ranking": 1,
  "human_review_required": true,
  "status": "SCORED",
  "message": "Day 9-13 ATS score calculated from available evidence; human review is required."
}
```

**Errors:**
- 404: Candidate or job not found
- 409: Candidate does not belong to job
- 422: Missing evidence (e.g., no resume)
- 503: Semantic model unavailable

---

### 10. Shortlisting

**POST** `/api/v1/openings/{opening_id}/shortlist`

Generate ranked shortlist from saved candidate scores.

**Request:**
```json
{
  "minimum_score": 60.0
}
```

**Response (200):**
```json
{
  "job_id": "uuid",
  "status": "REVIEW_SUGGESTIONS_READY",
  "shortlisted_count": 5,
  "candidates": [
    {"candidate_id": "uuid", "score": 85.0, "rank": 1},
    {"candidate_id": "uuid", "score": 72.0, "rank": 2}
  ],
  "human_review_required": true,
  "simulation_only": false,
  "message": "Ranked from saved candidate scores. Confirm every decision through human review."
}
```

**POST** `/api/v1/candidates/shortlist` — Demo endpoint (simulation only)

---

### 11. Eligibility Configuration

**PUT** `/api/v1/openings/{opening_id}/eligibility-config`

Save or update eligibility rules for a job opening.

**Request:**
```json
{
  "minimum_ats_score": 65,
  "mandatory_skills": ["Python", "SQL"],
  "minimum_experience_years": 1,
  "maximum_experience_years": 5,
  "location_rules": {
    "allowed_locations": ["Bangalore", "Remote"],
    "work_mode": "HYBRID",
    "remote_allowed": true,
    "relocation_required": false,
    "latest_start_date": "2026-06-01"
  },
  "decision_policy": {
    "manual_review_on_missing_data": true
  }
}
```

**GET** `/api/v1/openings/{opening_id}/eligibility-config`

Retrieve eligibility configuration.

---

### 12. Eligibility Evaluation

**POST** `/api/v1/candidates/{candidate_id}/eligibility/evaluate`

Evaluate candidate eligibility against job rules.

**Request:**
```json
{
  "opening_id": "uuid"
}
```

**Response (201):**
```json
{
  "evaluation_id": "uuid",
  "candidate_id": "uuid",
  "opening_id": "uuid",
  "status": "ELIGIBLE|REVIEW|REJECTED",
  "ats_score": 78.5,
  "rules": {
    "minimum_ats_score": {"status": "PASS", "reason": "...", "value": 78.5, "required": 65},
    "mandatory_skills": {"status": "PASS", "reason": "...", "matched": ["Python", "SQL"], "missing": [], "evidence_sources": {...}},
    "experience": {"status": "PASS", "reason": "...", "years": 3.0, "minimum_years": 1, "maximum_years": 5},
    "location": {"status": "PASS", "reason": "...", "candidate_location": "Bangalore", "candidate_preference": "HYBRID"},
    "availability": {"status": "NOT_CONFIGURED"}
  },
  "mandatory_skills_matched": ["Python", "SQL"],
  "mandatory_skills_missing": [],
  "experience_result": {...},
  "location_result": {...},
  "availability_result": {...},
  "missing_information": [],
  "review_reasons": [],
  "decision_explanation": "Configured rules were met using available evidence. Recruiter review is still required.",
  "configuration_version": 1,
  "evaluated_at": "2026-01-01T00:00:00+00:00",
  "human_review_required": true
}
```

**GET** `/api/v1/candidates/{candidate_id}/eligibility`

Retrieve latest eligibility evaluation (re-evaluates if inputs changed).

---

### 13. Screening Questions

**GET** `/api/v1/screening/questions`

List screening questions with filters.

**Query Parameters:**
- `role_id` (optional): Filter by role (e.g., `DATA_ANALYST`)
- `category` (optional): Filter by category (e.g., `skills`)
- `language` (optional): `en`, `ml`, `hi` (default: `en`)
- `mandatory` (optional): `true` or `false`
- `active_only` (optional): `true` (default)

**Response (200):** Array of question objects.

---

### 14. Screening Sessions

**POST** `/api/v1/screening/sessions` — Create session (201)

**GET** `/api/v1/screening/sessions/{session_id}` — Get transcript (200)

**PATCH** `/api/v1/screening/sessions/{session_id}` — Update status (200)

Status transitions:
- `CREATED` → `IN_PROGRESS`, `CANCELLED`
- `IN_PROGRESS` → `INTERRUPTED`, `COMPLETED`, `CANCELLED`
- `INTERRUPTED` → `IN_PROGRESS`, `COMPLETED`, `CANCELLED`

---

### 15. Transcript Segments

**POST** `/api/v1/screening/sessions/{session_id}/segments` — Add segments (201)

**Request:** Array of segment objects (1-500)
```json
[
  {
    "segment_id": "optional-uuid",
    "question_id": "HR001",
    "speaker": "CANDIDATE",
    "text": "I use Python for analysis.",
    "start_time": "2026-01-01T10:00:00+00:00",
    "end_time": "2026-01-01T10:01:00+00:00",
    "confidence": 0.95,
    "language": "en",
    "source": "MANUAL",
    "sequence_number": 1
  }
]
```

**Validation:**
- Sequence numbers must be strictly increasing
- Speaker must be valid enum
- Timestamps must include timezone
- Confidence must be 0-1
- Question ID must exist in dataset

---

### 16. Screening Interactions

**POST** `/api/v1/screening/sessions/{session_id}/interactions` — Add interaction (201)

**GET** `/api/v1/screening/sessions/{session_id}/interactions` — List interactions (200)

---

## Error Response Format

All errors follow RFC 7807 Problem Details where applicable:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable description",
  "details": {}
}
```

Common HTTP status codes:
- 400: Invalid request
- 401: Unauthorized (session required)
- 404: Not found
- 409: Conflict (ownership mismatch, invalid state transition)
- 413: Payload too large
- 422: Validation error
- 500: Internal error
- 503: Service unavailable (model not loaded)

---

## Rate Limiting

Recruiter login attempts are rate-limited (5 attempts per 15 minutes per IP/username).

---

## Versioning

API version is in URL path (`/api/v1/`). Breaking changes will use `/api/v2/`.