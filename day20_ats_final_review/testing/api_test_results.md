# Day 20 – ATS REST API Verification & Test Results

**Target System:** `http://127.0.0.1:8000`  
**Execution Date:** November 2026  
**API Protocol:** REST / JSON over HTTP  
**Total Tested Endpoints:** 8  
**Pass Rate:** 8 / 8 (100%)

## Summary Table

| # | Test Scenario | HTTP Method & Route | Expected Status | Actual Status | Result |
|---|---|---|---|---|---|
| 1 | Health Check | `GET /api/v1/health` | 200 | 200 | **PASS** |
| 2 | Recruiter Login (Valid) | `POST /api/v1/auth/session` | 200 | 200 | **PASS** |
| 3 | Recruiter Login (Invalid Credentials) | `POST /api/v1/auth/session` | 401 | 401 | **PASS** |
| 4 | Job Description Parser | `POST /api/v1/openings/parse-description` | 200 | 200 | **PASS** |
| 5 | Create Job Opening | `POST /api/v1/openings` | 201 | 201 | **PASS** |
| 6 | Register Candidate | `POST /api/v1/candidates` | 201 | 201 | **PASS** |
| 7 | Generate ATS Score | `POST /api/v1/candidates/score` | 200 | 200 | **PASS** |
| 8 | Shortlist Candidates (Threshold 60%) | `POST /api/v1/openings/fe067aca-57b3-4d36-b7c8-ee34848975df/shortlist` | 200 | 200 | **PASS** |

---

## Granular Request & Response Logs

### 1. Health Check
- **Endpoint:** `GET /api/v1/health`
- **Result:** `PASS` (HTTP 200)
- **Response Body:**
```json
{
  "status": "healthy",
  "service": "ZecPath ATS API",
  "version": "1.0.0",
  "authentication_configured": true
}
```

### 2. Recruiter Login (Valid)
- **Endpoint:** `POST /api/v1/auth/session`
- **Result:** `PASS` (HTTP 200)
- **Request Body:**
```json
{
  "username": "recruiter-d41-52",
  "password": "Password123!LongEnough"
}
```
- **Response Body:**
```json
{
  "authenticated": true,
  "username": "recruiter-d41-52",
  "expires_at": 1794753024.8292441
}
```

### 3. Recruiter Login (Invalid Credentials)
- **Endpoint:** `POST /api/v1/auth/session`
- **Result:** `PASS` (HTTP 401)
- **Request Body:**
```json
{
  "username": "recruiter-d41-52",
  "password": "WrongPassword!"
}
```
- **Response Body:**
```json
{
  "detail": "Valid recruiter credentials are required."
}
```

### 4. Job Description Parser
- **Endpoint:** `POST /api/v1/openings/parse-description`
- **Result:** `PASS` (HTTP 200)
- **Request Body:**
```json
{
  "description": "Required skills: Python, FastAPI, SQL, PostgreSQL, Docker\nPreferred skills: Redis, Kubernetes\nExperience: 3+ years\nEducation: Bachelor's degree\nResponsibilities:\n- Design microservices\n- Optimize databases"
}
```
- **Response Body:**
```json
{
  "required_skills": [
    "Python",
    "FastAPI",
    "SQL",
    "PostgreSQL",
    "Docker"
  ],
  "preferred_skills": [
    "Redis",
    "Kubernetes"
  ],
  "minimum_education": "Bachelor's degree",
  "minimum_years_experience": 3.0,
  "evidence": {
    "required_skills": [
      "Python, FastAPI, SQL, PostgreSQL, Docker"
    ],
    "preferred_skills": [
      "Redis, Kubernetes"
    ],
    "education": [
      "Bachelor's degree"
    ],
    "experience": [
      "3+ years"
    ],
    "responsibilities": [
      "- Design microservices",
      "- Optimize databases"
    ]
  },
  "warnings": [],
  "method": "explicit_heading_rules_v1",
  "human_confirmation_required": true
}
```

### 5. Create Job Opening
- **Endpoint:** `POST /api/v1/openings`
- **Result:** `PASS` (HTTP 201)
- **Request Body:**
```json
{
  "title": "Senior Python Developer (API Test)",
  "description": "Build backend APIs and microservices with FastAPI and Docker.",
  "required_skills": [
    "Python",
    "FastAPI",
    "SQL",
    "PostgreSQL",
    "Docker"
  ],
  "preferred_skills": [
    "Redis",
    "Kubernetes"
  ],
  "minimum_education": "Bachelor's Degree",
  "minimum_years_experience": 3.0
}
```
- **Response Body:**
```json
{
  "opening_id": "fe067aca-57b3-4d36-b7c8-ee34848975df",
  "title": "Senior Python Developer (API Test)",
  "description": "Build backend APIs and microservices with FastAPI and Docker.",
  "required_skills": [
    "Python",
    "FastAPI",
    "SQL",
    "PostgreSQL",
    "Docker"
  ],
  "preferred_skills": [
    "Redis",
    "Kubernetes"
  ],
  "minimum_education": "Bachelor's Degree",
  "minimum_years_experience": 3.0,
  "status": "OPEN",
  "created_at": "2026-11-15T06:30:25.348354+00:00",
  "updated_at": "2026-11-15T06:30:25.348354+00:00"
}
```

### 6. Register Candidate
- **Endpoint:** `POST /api/v1/candidates`
- **Result:** `PASS` (HTTP 201)
- **Request Body:**
```json
{
  "opening_id": "fe067aca-57b3-4d36-b7c8-ee34848975df",
  "name": "Alex Mercer (API Test)",
  "email": "alex.api@example.test",
  "skills": [
    "Python",
    "FastAPI",
    "SQL",
    "PostgreSQL",
    "Docker",
    "Redis"
  ],
  "experience_years": 4.5
}
```
- **Response Body:**
```json
{
  "candidate_id": "a2d8f959-43c6-4469-b0f1-41afcbe2d002",
  "name": "Alex Mercer (API Test)",
  "email": "alex.api@example.test",
  "opening_id": "fe067aca-57b3-4d36-b7c8-ee34848975df",
  "skills": [
    "Python",
    "FastAPI",
    "SQL",
    "PostgreSQL",
    "Docker",
    "Redis"
  ],
  "resume_text": "",
  "resume_data": {},
  "resume_filename": null,
  "application_status": "APPLIED",
  "score": null,
  "score_evidence": null,
  "location": null,
  "relocation_willingness": null,
  "work_mode_preference": null,
  "availability_date": null,
  "created_at": "2026-11-15T06:30:25.395241+00:00",
  "updated_at": "2026-11-15T06:30:25.395241+00:00"
}
```

### 7. Generate ATS Score
- **Endpoint:** `POST /api/v1/candidates/score`
- **Result:** `PASS` (HTTP 200)
- **Request Body:**
```json
{
  "job_id": "fe067aca-57b3-4d36-b7c8-ee34848975df",
  "candidate_id": "a2d8f959-43c6-4469-b0f1-41afcbe2d002"
}
```
- **Response Body:**
```json
{
  "job_id": "fe067aca-57b3-4d36-b7c8-ee34848975df",
  "candidate_id": "a2d8f959-43c6-4469-b0f1-41afcbe2d002",
  "score": 35.0,
  "evidence": {
    "method": "day13_profile_skill_weighted_score",
    "job_id": "fe067aca-57b3-4d36-b7c8-ee34848975df",
    "candidate_id": "a2d8f959-43c6-4469-b0f1-41afcbe2d002",
    "job_title": "Senior Python Developer (API Test)",
    "candidate_name": "Alex Mercer (API Test)",
    "extracted_skills": [],
    "scoring_skills": [
      "Python",
      "FastAPI",
      "SQL",
      "PostgreSQL",
      "Docker",
      "Redis"
    ],
    "matching_required_skills": [
      "Python",
      "FastAPI",
      "SQL",
      "PostgreSQL",
      "Docker"
    ],
    "matched_required_skills": [
      "Python",
      "FastAPI",
      "SQL",
      "PostgreSQL",
      "Docker"
    ],
    "missing_required_skills": [],
    "matching_preferred_skills": [
      "Redis"
    ],
    "education_details": [],
    "experience_details": {
      "years": null,
      "roles": []
    },
    "components": {
      "skill_match": {
        "score": 1.0,
        "reason": "Score is matched required skills divided by total required skills.",
        "matched_skills": [
          "docker",
          "fastapi",
          "postgresql",
          "python",
          "sql"
        ],
        "missing_skills": []
      },
      "experience_relevance": {
        "score": null,
        "reason": "Resume years_of_experience is missing."
      },
      "education_alignment": {
        "score": null,
        "reason": "Resume education is missing."
      },
      "semantic_similarity": {
        "score": null,
        "reason": "A readable resume is required for Day 12 semantic scoring.",
        "personal_data_masking": "Contact details and labeled personal attributes are excluded from matching input."
      }
    },
    "weights": {
      "skill_match": 0.35,
      "experience_relevance": 0.2,
      "education_alignment": 0.15,
      "semantic_similarity": 0.3
    },
    "breakdown": {
      "skill_match": {
        "score": 100.0,
        "weight": 0.35,
        "weighted_contribution": 35.0
      },
      "experience_relevance": {
        "score": 0.0,
        "weight": 0.2,
        "weighted_contribution": 0.0
      },
      "education_alignment": {
        "score": 0.0,
        "weight": 0.15,
        "weighted_contribution": 0.0
      },
      "semantic_similarity": {
        "score": 0.0,
        "weight": 0.3,
        "weighted_contribution": 0.0
      }
    },
    "classification": "LOW",
    "formula": "sum(component_score_0_to_100 * configured_role_weight)",
    "scoring_explanation": "Day 9-11 extract skills, dated work history, and education; Day 8 section segmentation scopes extraction when recognized sections exist. Day 12 compares a resume representation with the job title, description, required/preferred skills, and specified education/experience requirements using sentence-embedding cosine similarity; Day 13 applies its configured, role-specific weighted formula. Missing experience or education inputs are represented as unavailable by their component helper and contribute zero under Day 13's existing score normalization. Contact details and labeled personal attributes are excluded from semantic matching.",
    "fairness_safeguards": {
      "personal_attributes_used_for_scoring": false,
      "semantic_input_masking": true,
      "human_review_required": true
    },
    "human_review_required": true,
    "required_skills": [
      "Python",
      "FastAPI",
      "SQL",
      "PostgreSQL",
      "Docker"
    ],
    "profile_skills": [
      "Python",
      "FastAPI",
      "SQL",
      "PostgreSQL",
      "Docker",
      "Redis"
    ],
    "resume_evidence_skills": [],
    "resume_evidence": [],
    "scored_at": "2026-11-15T06:30:25.463209+00:00",
    "scoring_version": "day9-12-13-v1"
  },
  "job_title": "Senior Python Developer (API Test)",
  "candidate_name": "Alex Mercer (API Test)",
  "extracted_skills": [],
  "matching_required_skills": [
    "Python",
    "FastAPI",
    "SQL",
    "PostgreSQL",
    "Docker"
  ],
  "missing_required_skills": [],
  "education_details": [],
  "experience_details": {
    "years": null,
    "roles": []
  },
  "components": {
    "skill_match": {
      "score": 1.0,
      "reason": "Score is matched required skills divided by total required skills.",
      "matched_skills": [
        "docker",
        "fastapi",
        "postgresql",
        "python",
        "sql"
      ],
      "missing_skills": []
    },
    "experience_relevance": {
      "score": null,
      "reason": "Resume years_of_experience is missing."
    },
    "education_alignment": {
      "score": null,
      "reason": "Resume education is missing."
    },
    "semantic_similarity": {
      "score": null,
      "reason": "A readable resume is required for Day 12 semantic scoring.",
      "personal_data_masking": "Contact details and labeled personal attributes are excluded from matching input."
    }
  },
  "ranking": 1,
  "human_review_required": true,
  "status": "SCORED",
  "message": "Day 9-13 ATS score calculated from available evidence; human review is required."
}
```

### 8. Shortlist Candidates (Threshold 60%)
- **Endpoint:** `POST /api/v1/openings/fe067aca-57b3-4d36-b7c8-ee34848975df/shortlist`
- **Result:** `PASS` (HTTP 200)
- **Request Body:**
```json
{
  "minimum_score": 60.0
}
```
- **Response Body:**
```json
{
  "job_id": "fe067aca-57b3-4d36-b7c8-ee34848975df",
  "status": "REVIEW_SUGGESTIONS_READY",
  "shortlisted_count": 0,
  "candidates": [],
  "human_review_required": true,
  "simulation_only": false,
  "message": "Ranked from saved candidate scores. Confirm every decision through human review."
}
```
