# ZecPath AI Screening Subsystem – API Documentation (Day 32)

**System Base URL:** `http://127.0.0.1:8000/api/v1`  
**Interactive API Documentation:** `http://127.0.0.1:8000/docs`  
**Subsystem Scope:** AI-Powered Candidate Screening (Days 22–32)  
**Authentication:** Cookie-based session (`zecpath_session`) with CSRF Origin validation (`Origin: http://127.0.0.1:8000` or `http://testserver`).

---

## 1. Investigation of Proposed Reference Endpoints

Prior to documenting the production routes, an empirical audit was conducted to verify whether proposed reference routes from earlier planning documents were implemented as bare root paths:

| Proposed Reference Path | HTTP Method | Implementation Status | Actual System Equivalent Route |
|---|---|---|---|
| `/screening/start` | POST | **NOT IMPLEMENTED** (Returns 404) | `POST /api/v1/screening/sessions/{session_id}/start` or `POST /api/v1/screening/pipeline/sessions` |
| `/screening/answer` | POST | **NOT IMPLEMENTED** (Returns 404) | `POST /api/v1/screening/sessions/{session_id}/answers/text` |
| `/screening/{candidate_id}` | GET | **NOT IMPLEMENTED** (Returns 404) | `GET /api/v1/candidates/{candidate_id}` or `GET /api/v1/screening/sessions/{session_id}` |
| `/screening/{candidate_id}/report` | GET | **NOT IMPLEMENTED** (Returns 404) | `GET /api/v1/screening/candidates/{candidate_id}/reports` |

---

## 2. Verified Active Production Screening Endpoints

### 2.1 List Screening Questions
* **Path:** `GET /api/v1/screening/questions`
* **Purpose:** Retrieves standardized screening questions from the HR question repository.
* **Query Parameters:**
  * `role_id` (string, optional): Specific role filter (e.g. `SOFTWARE_DEVELOPER`, `DATA_ANALYST`).
  * `language` (string, optional, default: `"en"`): Target language code.
* **Request Body:** None.
* **Response Status:** `200 OK`
* **Response Body Example:**
```json
[
  {
    "question_id": "HR001",
    "role": "Data Analyst",
    "category": "Introduction",
    "question_text": "Please introduce yourself and briefly describe your background.",
    "mandatory": true,
    "scoring_importance": "high",
    "language": "en"
  }
]
```
* **Validation & Errors:** Returns `422 Unprocessable Entity` if an unsupported role format is provided.

---

### 2.2 Create Screening Session
* **Path:** `POST /api/v1/screening/sessions`
* **Purpose:** Initializes a screening record for a candidate linked to an active job opening.
* **Request Headers:**
  * `Content-Type: application/json`
  * `Cookie: zecpath_session=<session_token>`
* **Request Body Example:**
```json
{
  "candidate_id": "b3e34b97-bb30-4e12-b5df-6a3f4e15091a",
  "opening_id": "63de7bae-703c-411a-85eb-956c3fa73f8a",
  "language": "en"
}
```
* **Response Status:** `201 Created`
* **Response Body Example:**
```json
{
  "session_id": "81f18579-3739-4412-a169-d4cbfef765ce",
  "candidate_id": "b3e34b97-bb30-4e12-b5df-6a3f4e15091a",
  "opening_id": "63de7bae-703c-411a-85eb-956c3fa73f8a",
  "status": "CREATED",
  "language": "en",
  "created_at": "2026-11-15T13:10:39.265667"
}
```
* **Validation & Errors:** Returns `404 Not Found` if candidate or opening does not exist. Returns `400 Bad Request` if candidate does not match opening.

---

### 2.3 Create & Initialize Pipeline Session
* **Path:** `POST /api/v1/screening/pipeline/sessions`
* **Purpose:** Creates session, loads role-specific questions, and initializes state machine to `ASKING` with the first question.
* **Request Body:**
```json
{
  "candidate_id": "b3e34b97-bb30-4e12-b5df-6a3f4e15091a",
  "opening_id": "63de7bae-703c-411a-85eb-956c3fa73f8a",
  "language": "en"
}
```
* **Response Status:** `201 Created`
* **Response Body Example:**
```json
{
  "session": {
    "session_id": "81f18579-3739-4412-a169-d4cbfef765ce",
    "status": "CREATED"
  },
  "questions": [ ... ],
  "next_question": {
    "question_id": "Q001",
    "category": "skills",
    "question_text": "What technical skills do you have?"
  }
}
```

---

### 2.4 Start Screening Session
* **Path:** `POST /api/v1/screening/sessions/{session_id}/start`
* **Purpose:** Transitions session status to active conversation flow.
* **Path Parameters:** `session_id` (UUID).
* **Response Status:** `200 OK`
* **Response Body Example:**
```json
{
  "session_id": "81f18579-3739-4412-a169-d4cbfef765ce",
  "status": "IN_PROGRESS",
  "current_question_id": "HR001"
}
```
* **Validation & Errors:** `404 Not Found` if session does not exist.

---

### 2.5 Submit Text Answer
* **Path:** `POST /api/v1/screening/sessions/{session_id}/answers/text`
* **Purpose:** Ingests candidate's response to an HR question, executes transcript cleaning, intent classification, entity extraction, answer validation, 4-factor scoring, and behavioral analysis.
* **Request Headers:**
  * `Content-Type: application/x-www-form-urlencoded`
* **Form Parameters:**
  * `question_id` (string, required): e.g. `"HR001"` or `"Q001"`
  * `answer_text` (string, required): Raw text response
* **Response Status:** `200 OK`
* **Response Body Example:**
```json
{
  "transcript": {
    "transcript_id": "4e78b1cf-7128-40b5-9014-cb9ef7ba5791",
    "raw_text": "I have experience with Python, SQL, Excel and Power BI.",
    "cleaned_text": "I have experience with Python, SQL, Excel and Power BI."
  },
  "answer": {
    "answer_id": "ANS-Q001",
    "intent": "skills",
    "extracted_information": {
      "skills": ["Python", "SQL", "Excel", "Power BI"]
    },
    "validation": {
      "missing": false,
      "vague": false,
      "off_topic": false,
      "status": "valid"
    }
  },
  "score": {
    "clarity": 4,
    "relevance": 5,
    "completeness": 5,
    "consistency": 5,
    "normalized_score": 95.0,
    "explanation": [
      "The answer is clearly expressed.",
      "The answer is relevant to the expected topic."
    ]
  },
  "behavioral": {
    "sentiment": "NEUTRAL",
    "confidence_score": 60,
    "hesitation_count": 0,
    "uncertainty_count": 0
  },
  "next_question": {
    "question_id": "Q002",
    "question": "Tell me about your experience."
  }
}
```
* **Validation & Errors:** `400 Bad Request` if `answer_text` is empty. `404 Not Found` if `session_id` or `question_id` is invalid.

---

### 2.6 Upload Audio Response
* **Path:** `POST /api/v1/screening/sessions/{session_id}/audio`
* **Purpose:** Upload candidate voice recording (`.wav`, `.mp3`, `.m4a`, `.ogg`, `.flac`).
* **Request Headers:**
  * `Content-Type: multipart/form-data`
* **Form Data:**
  * `file`: Binary audio stream (Max: 50 MiB)
  * `question_id`: Target screening question ID
* **Response Status:** `202 Accepted`
* **Response Body Example:**
```json
{
  "audio_id": "93f3cbb0-2e45-424a-9b4f-8f8aaebf1a30",
  "session_id": "81f18579-3739-4412-a169-d4cbfef765ce",
  "question_id": "HR001",
  "status": "PENDING",
  "message": "Audio uploaded successfully. Ready for transcription."
}
```
* **Validation & Errors:** Returns `400 Bad Request` for unsupported formats or empty file. Returns `413 Payload Too Large` for files > 50 MiB.

---

### 2.7 Transcribe Uploaded Audio
* **Path:** `POST /api/v1/screening/audio/{audio_id}/transcribe`
* **Purpose:** Runs STT Whisper engine, removes fillers, and saves normalized transcript.
* **Response Status:** `200 OK`
* **Response Body Example:**
```json
{
  "transcript_id": "bc2990aa-9351-4043-a60d-4589d816f164",
  "audio_id": "93f3cbb0-2e45-424a-9b4f-8f8aaebf1a30",
  "raw_text": "This is candidate audio response for HR001.",
  "cleaned_text": "This is candidate audio response for HR001.",
  "language": "en",
  "language_probability": 0.95,
  "segment_count": 1
}
```

---

### 2.8 Complete Screening Session
* **Path:** `POST /api/v1/screening/sessions/{session_id}/complete`
* **Purpose:** Finalizes screening session, computes aggregate weighted score, creates report record, and updates session status to `COMPLETED`.
* **Response Status:** `200 OK`
* **Response Body Example:**
```json
{
  "session_id": "81f18579-3739-4412-a169-d4cbfef765ce",
  "status": "COMPLETED",
  "overall_score": 83.0,
  "report_id": "rep-screening-81f18579"
}
```

---

### 2.9 Get Screening Report
* **Path:** `GET /api/v1/screening/sessions/{session_id}/report`
* **Purpose:** Retrieves the recruiter-ready screening report including key answers, strengths, and risk flags.
* **Response Status:** `200 OK`
* **Response Body Example:**
```json
{
  "report_id": "rep-screening-81f18579",
  "session_id": "81f18579-3739-4412-a169-d4cbfef765ce",
  "candidate_id": "b3e34b97-bb30-4e12-b5df-6a3f4e15091a",
  "opening_id": "63de7bae-703c-411a-85eb-956c3fa73f8a",
  "report_json": {
    "overall_score": 83.0,
    "recommendation": "SHORTLIST",
    "strengths": [
      "Candidate confirmed technical skills: Python, SQL, Excel, Power BI",
      "Candidate reported 1 year(s) of experience."
    ],
    "risks": []
  },
  "created_at": "2026-11-15T13:10:39.265667"
}
```

---

### 2.10 List Candidate Screening Reports
* **Path:** `GET /api/v1/screening/candidates/{candidate_id}/reports`
* **Purpose:** Retrieves full history of screening evaluations conducted for a candidate.
* **Response Status:** `200 OK`
* **Response Body Example:** `[ { ... ScreeningReportFullResponse ... } ]`

