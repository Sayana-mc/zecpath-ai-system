# Day 20 – Complete ATS Swagger UI Live API Testing Report

**Execution Platform:** Interactive FastAPI Swagger UI (`http://127.0.0.1:8000/docs`)  
**Testing Method:** Live Playwright Browser Automation with "Try it out" and "Execute"  
**Execution Date:** November 2026  
**Total Tested Scenarios:** 15 (Positive and Negative Input Vectors)  
**Pass Rate:** **15 / 15 (100% Pass Rate)**  

---

## 1. Executive Test Matrix

| # | Endpoint | HTTP Method | Scenario / Purpose | Expected Status | Actual Status | Result | Screenshot Reference |
|---|---|---|---|---|---|---|---|
| **1** | `/api/v1/auth/session` | POST | Recruiter login with invalid credentials | HTTP 401 | **401 Unauthorized** | **PASS** | `swagger_02_login_invalid.png` |
| **2** | `/api/v1/auth/session` | POST | Recruiter login with valid credentials | HTTP 200 | **200 OK** | **PASS** | `swagger_01_login_success.png` |
| **3** | `/api/v1/openings` | POST | Create opening with missing required `title` field | HTTP 422 | **422 Unprocessable** | **PASS** | `swagger_04_create_opening_invalid.png` |
| **4** | `/api/v1/openings` | POST | Create valid Senior Python Developer opening | HTTP 201 | **201 Created** | **PASS** | `swagger_03_create_opening_success.png` |
| **5** | `/api/v1/resumes/upload` | POST | Upload unsupported file format (`.exe`) | HTTP 400 | **400 Bad Request** | **PASS** | `swagger_06_resume_upload_invalid.png` |
| **6** | `/api/v1/resumes/upload` | POST | Upload valid `.txt` resume for candidate | HTTP 202 | **202 Accepted** | **PASS** | `swagger_05_resume_upload_success.png` |
| **7** | `/api/v1/resumes/parse` | POST | Parse resume with nonexistent `job_id` | HTTP 404 | **404 Not Found** | **PASS** | `swagger_08_resume_parse_invalid.png` |
| **8** | `/api/v1/resumes/parse` | POST | Retrieve parsed resume data for completed job | HTTP 200 | **200 OK** | **PASS** | `swagger_07_resume_parse_success.png` |
| **9** | `/api/v1/candidates/score` | POST | Generate ATS score for nonexistent candidate | HTTP 404 | **404 Not Found** | **PASS** | `swagger_10_ats_score_invalid.png` |
| **10** | `/api/v1/candidates/score` | POST | Compute 4-factor ATS score for Alex Mercer | HTTP 200 | **200 OK** | **PASS** | `swagger_09_ats_score_success.png` |
| **11** | `/api/v1/candidates/score` | POST | Verify candidate ranking attribute (`ranking: 1`) | HTTP 200 | **200 OK** | **PASS** | `swagger_11_candidate_ranking.png` |
| **12** | `/api/v1/openings/{id}/shortlist` | POST | Shortlist with negative threshold (`-15.0`) | HTTP 422 | **422 Unprocessable** | **PASS** | `swagger_13_shortlist_invalid.png` |
| **13** | `/api/v1/openings/{id}/shortlist` | POST | Generate ranked shortlist meeting 60% threshold | HTTP 200 | **200 OK** | **PASS** | `swagger_12_shortlist_success.png` |
| **14** | `/api/v1/openings/parse-description` | POST | Parse job description with empty payload | HTTP 422 | **422 Unprocessable** | **PASS** | `swagger_15_job_description_parse_invalid.png` |
| **15** | `/api/v1/openings/parse-description` | POST | Extract structured requirements from raw JD text | HTTP 200 | **200 OK** | **PASS** | `swagger_14_job_description_parse_success.png` |

---

## 2. Granular Execution Logs & Swagger Payloads

### 1. `POST /api/v1/auth/session` (Invalid Credentials)
- **Purpose:** Enforce authentication boundary on bad credentials.
- **Expected Status:** `HTTP 401` | **Actual Status:** `HTTP 401 Unauthorized` | **Result:** **PASS**
- **Request Body:**
```json
{
  "username": "recruiter-d41-52",
  "password": "WrongPassword!"
}
```
- **Swagger Response Body:**
```json
{
  "detail": "Valid recruiter credentials are required."
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_02_login_invalid.png`

---

### 2. `POST /api/v1/auth/session` (Valid Credentials)
- **Purpose:** Issue authenticated session cookie.
- **Expected Status:** `HTTP 200` | **Actual Status:** `HTTP 200 OK` | **Result:** **PASS**
- **Request Body:**
```json
{
  "username": "recruiter-d41-52",
  "password": "Password123!LongEnough"
}
```
- **Swagger Response Body:**
```json
{
  "authenticated": true,
  "username": "recruiter-d41-52",
  "expires_at": 1794754928.813307
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_01_login_success.png`

---

### 3. `POST /api/v1/openings` (Invalid Opening Payload)
- **Purpose:** Validate Pydantic schema validation when mandatory `title` is missing.
- **Expected Status:** `HTTP 422` | **Actual Status:** `HTTP 422 Unprocessable Entity` | **Result:** **PASS**
- **Request Body:**
```json
{
  "description": "Missing title",
  "required_skills": ["Python"]
}
```
- **Swagger Response Body:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {
        "description": "Missing title",
        "required_skills": ["Python"]
      }
    }
  ]
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_04_create_opening_invalid.png`

---

### 4. `POST /api/v1/openings` (Valid Opening Creation)
- **Purpose:** Persist a new job opening with requirements.
- **Expected Status:** `HTTP 201` | **Actual Status:** `HTTP 201 Created` | **Result:** **PASS**
- **Request Body:**
```json
{
  "title": "Senior Python Developer (Swagger Test)",
  "description": "Building high-performance data pipelines and microservices with FastAPI and Docker.",
  "required_skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker"],
  "preferred_skills": ["Redis", "Kubernetes"],
  "minimum_education": "Bachelor's Degree",
  "minimum_years_experience": 3.0
}
```
- **Swagger Response Body:**
```json
{
  "opening_id": "63de7bae-aa69-420c-a1f5-8ec79bc42fb2",
  "title": "Senior Python Developer (Swagger Test)",
  "description": "Building high-performance data pipelines and microservices with FastAPI and Docker.",
  "required_skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker"],
  "preferred_skills": ["Redis", "Kubernetes"],
  "minimum_education": "Bachelor's Degree",
  "minimum_years_experience": 3.0,
  "status": "OPEN",
  "created_at": "2026-11-15T07:03:52.418291+00:00"
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_03_create_opening_success.png`

---

### 5. `POST /api/v1/resumes/upload` (Invalid File Type)
- **Purpose:** Reject unsupported file formats.
- **Expected Status:** `HTTP 400` | **Actual Status:** `HTTP 400 Bad Request` | **Result:** **PASS**
- **Request Form Data:** `file: malicious.exe`
- **Swagger Response Body:**
```json
{
  "detail": "Unsupported resume format. Use PDF, DOCX, or TXT."
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_06_resume_upload_invalid.png`

---

### 6. `POST /api/v1/resumes/upload` (Valid Text Resume)
- **Purpose:** Ingest valid candidate resume into asynchronous processing queue.
- **Expected Status:** `HTTP 202` | **Actual Status:** `HTTP 202 Accepted` | **Result:** **PASS**
- **Request Form Data:** `file: alex_mercer_resume.txt`, `candidate_id: 9ddad3cf-3e79-475c-86d4-f4a31d58d16a`
- **Swagger Response Body:**
```json
{
  "job_id": "3088745c-21af-41f5-9a8e-358fb77e69d8",
  "status": "QUEUED",
  "filename": "alex_mercer_resume.txt",
  "created_at": "2026-11-15T07:04:04.182918+00:00"
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_05_resume_upload_success.png`

---

### 7. `POST /api/v1/resumes/parse` (Nonexistent Job ID)
- **Purpose:** Verify 404 response on unknown job query.
- **Expected Status:** `HTTP 404` | **Actual Status:** `HTTP 404 Not Found` | **Result:** **PASS**
- **Request Body:**
```json
{
  "job_id": "nonexistent_job_uuid_9999"
}
```
- **Swagger Response Body:**
```json
{
  "detail": {
    "error": "JOB_NOT_FOUND",
    "message": "Resume processing job 'nonexistent_job_uuid_9999' was not found."
  }
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_08_resume_parse_invalid.png`

---

### 8. `POST /api/v1/resumes/parse` (Valid Completed Job)
- **Purpose:** Retrieve structured parsed resume details.
- **Expected Status:** `HTTP 200` | **Actual Status:** `HTTP 200 OK` | **Result:** **PASS**
- **Request Body:**
```json
{
  "job_id": "3088745c-21af-41f5-9a8e-358fb77e69d8"
}
```
- **Swagger Response Body:**
```json
{
  "job_id": "3088745c-21af-41f5-9a8e-358fb77e69d8",
  "candidate_id": "9ddad3cf-3e79-475c-86d4-f4a31d58d16a",
  "parsed_text": "Alex Mercer\nEmail: alex.mercer@example.test...",
  "skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker", "Redis", "Git", "Linux"],
  "experience_years": 4.5,
  "education": [
    {
      "degree_name": "Bachelor of Science in Computer Science",
      "institution": "State University of Technology",
      "year": 2020
    }
  ],
  "status": "COMPLETED"
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_07_resume_parse_success.png`

---

### 9. `POST /api/v1/candidates/score` (Nonexistent Candidate)
- **Purpose:** Verify 404 response when candidate does not exist.
- **Expected Status:** `HTTP 404` | **Actual Status:** `HTTP 404 Not Found` | **Result:** **PASS**
- **Request Body:**
```json
{
  "job_id": "63de7bae-aa69-420c-a1f5-8ec79bc42fb2",
  "candidate_id": "nonexistent_cand_1234"
}
```
- **Swagger Response Body:**
```json
{
  "detail": "Candidate 'nonexistent_cand_1234' was not found."
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_10_ats_score_invalid.png`

---

### 10. `POST /api/v1/candidates/score` (Valid Candidate Scoring)
- **Purpose:** Compute 4-factor explainable ATS score for Alex Mercer.
- **Expected Status:** `HTTP 200` | **Actual Status:** `HTTP 200 OK` | **Result:** **PASS**
- **Request Body:**
```json
{
  "job_id": "63de7bae-aa69-420c-a1f5-8ec79bc42fb2",
  "candidate_id": "9ddad3cf-3e79-475c-86d4-f4a31d58d16a"
}
```
- **Swagger Response Body:**
```json
{
  "score": 88.52,
  "ranking": 1,
  "job_id": "63de7bae-aa69-420c-a1f5-8ec79bc42fb2",
  "candidate_id": "9ddad3cf-3e79-475c-86d4-f4a31d58d16a",
  "job_title": "Senior Python Developer (Swagger Test)",
  "candidate_name": "Alex Mercer (Swagger Suite)",
  "matching_required_skills": [
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
  "breakdown": {
    "skill_match": {
      "score": 100.0,
      "weight": 0.4,
      "weighted_contribution": 40.0
    },
    "semantic_similarity": {
      "score": 68.4,
      "weight": 0.3,
      "weighted_contribution": 20.52
    },
    "experience_relevance": {
      "score": 100.0,
      "weight": 0.2,
      "weighted_contribution": 20.0
    },
    "education_alignment": {
      "score": 100.0,
      "weight": 0.1,
      "weighted_contribution": 10.0
    }
  },
  "classification": "EXCELLENT",
  "human_review_required": true
}
```
- **Screenshots:** `swagger_09_ats_score_success.png` and `11_ats_score_api.png`

---

### 11. Candidate Ranking
- **Purpose:** Verify assigned ranking attribute from scored candidate batch.
- **Expected Status:** `HTTP 200` | **Actual Status:** `HTTP 200 OK` | **Result:** **PASS**
- **Verification:** Alex Mercer scored $88.52\%$ and was assigned `ranking: 1`.
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_11_candidate_ranking.png`

---

### 12. `POST /api/v1/openings/{opening_id}/shortlist` (Negative Threshold)
- **Purpose:** Enforce input range validation ($0.0 \le \text{minimum\_score} \le 100.0$).
- **Expected Status:** `HTTP 422` | **Actual Status:** `HTTP 422 Unprocessable Entity` | **Result:** **PASS**
- **Request Body:**
```json
{
  "minimum_score": -15.0
}
```
- **Swagger Response Body:**
```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["body", "minimum_score"],
      "msg": "Input should be greater than or equal to 0",
      "input": -15.0,
      "ctx": {
        "ge": 0.0
      }
    }
  ]
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_13_shortlist_invalid.png`

---

### 13. `POST /api/v1/openings/{opening_id}/shortlist` (Valid 60% Threshold)
- **Purpose:** Generate ranked shortlist meeting threshold.
- **Expected Status:** `HTTP 200` | **Actual Status:** `HTTP 200 OK` | **Result:** **PASS**
- **Request Body:**
```json
{
  "minimum_score": 60.0
}
```
- **Swagger Response Body:**
```json
{
  "opening_id": "63de7bae-aa69-420c-a1f5-8ec79bc42fb2",
  "threshold": 60.0,
  "shortlisted_count": 1,
  "candidates": [
    {
      "rank": 1,
      "candidate_id": "9ddad3cf-3e79-475c-86d4-f4a31d58d16a",
      "score": 88.52,
      "status": "SHORTLISTED"
    }
  ]
}
```
- **Screenshots:** `swagger_12_shortlist_success.png` and `12_shortlist_api.png`

---

### 14. `POST /api/v1/openings/parse-description` (Empty Body)
- **Purpose:** Enforce mandatory description body validation.
- **Expected Status:** `HTTP 422` | **Actual Status:** `HTTP 422 Unprocessable Entity` | **Result:** **PASS**
- **Request Body:** `{}`
- **Swagger Response Body:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "description"],
      "msg": "Field required"
    }
  ]
}
```
- **Screenshot:** `day20_ats_final_review/screenshots/swagger_15_job_description_parse_invalid.png`

---

### 15. `POST /api/v1/openings/parse-description` (Valid Parsing)
- **Purpose:** Extract requirements from raw job description text.
- **Expected Status:** `HTTP 200` | **Actual Status:** `HTTP 200 OK` | **Result:** **PASS**
- **Request Body:**
```json
{
  "description": "Required skills: Python, FastAPI, SQL, PostgreSQL, Docker\nPreferred skills: Redis, Kubernetes\nExperience: 3+ years\nEducation: Bachelor's degree\nResponsibilities:\n- Build microservices\n- Optimize SQL schemas"
}
```
- **Swagger Response Body:**
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
  "warnings": [],
  "human_confirmation_required": true
}
```
- **Screenshots:** `swagger_14_job_description_parse_success.png` and `13_parsing_api.png`
