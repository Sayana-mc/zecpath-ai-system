# Days 33–40: AI HR Interview REST API Reference

All endpoints are mounted under `/api/v1` and served by `src/api.py`.

---

## 1. Interview Session Management

### `POST /api/v1/hr-interviews`
Creates a new HR interview session and seeds tailored questions.
- **Request Body:**
  ```json
  {
    "candidate_id": "cand_123",
    "opening_id": "job_456",
    "experience_level": "EXPERIENCED", // "FRESHER" | "EXPERIENCED"
    "role_type": "TECHNICAL",         // "TECHNICAL" | "NON_TECHNICAL"
    "recruiter_id": "rec_001"
  }
  ```
- **Response (201 Created):** `HRInterviewSessionResponse`

### `GET /api/v1/hr-interviews`
Lists sessions with optional filters `candidate_id` and `status`.

### `GET /api/v1/hr-interviews/{interview_id}`
Returns interview session metadata and current FSM phase.

### `GET /api/v1/hr-interviews/{interview_id}/status`
Returns high-level session status, question counts, and completion flags.

### `POST /api/v1/hr-interviews/{interview_id}/start`
Advances session to `IN_PROGRESS` and sets the first question.

### `POST /api/v1/hr-interviews/{interview_id}/pause`
Pauses an active session (`status: PAUSED`).

### `POST /api/v1/hr-interviews/{interview_id}/resume`
Resumes a paused session (`status: IN_PROGRESS`).

---

## 2. Questions & Answer Submission

### `GET /api/v1/hr-interviews/{interview_id}/questions`
Returns all assigned questions for the session.

### `POST /api/v1/hr-interviews/{interview_id}/answers`
Submits candidate answer for a question. Runs communication evaluation, behavioral signal analysis, and checks follow-up necessity.
- **Request Body:**
  ```json
  {
    "question_id": "HRQ_123",
    "answer_text": "In my previous project, we adopted a microservices architecture..."
  }
  ```
- **Response:**
  ```json
  {
    "response": { "response_id": "HRRSP_...", "quality": "complete" },
    "communication_evaluation": { "total_communication_score": 88.0 },
    "behavioral_signals": { "hesitation_count": 0, "sentiment": "POSITIVE" },
    "followup_decision": { "needed": false },
    "next_question": { "question_id": "HRQ_124" }
  }
  ```

### `POST /api/v1/hr-interviews/{interview_id}/follow-ups`
Submits candidate reply to an adaptive follow-up.

---

## 3. Evaluation & Reporting

### `POST /api/v1/hr-interviews/{interview_id}/complete`
Concludes interview, executes overall scoring, and persists the 11-section executive dossier.

### `GET /api/v1/hr-interviews/{interview_id}/evaluation`
Returns full evaluation scores: communication, behavioral signals, aptitude, and composite score.

### `GET /api/v1/hr-interviews/{interview_id}/report`
- Default query `?format=json`: Returns structured 11-section JSON report.
- Query `?format=html`: Returns styled, print-ready HTML page.

### `GET /api/v1/hr-interviews/candidates/{candidate_id}/reports`
Lists all generated HR interview reports for a candidate.

### `POST /api/v1/hr-interviews/{interview_id}/decision`
Records recruiter hiring decision (`PROCEED`, `HOLD`, `REJECT`, `MANUAL_REVIEW`) and review notes.

