# Day 24–32 API Documentation

## Overview
The following REST API endpoints have been integrated into the root ZecPath application router (`src/api.py`), providing complete control over the AI voice screening pipeline.

---

### 1. Questions Endpoint
- **URL:** `GET /api/v1/screening/questions/{role_id}`
- **Description:** Returns curated screening questions for a specific role (e.g., `SOFTWARE_DEVELOPER`, `DATA_ANALYST`).
- **Response:** Array of `ScreeningQuestionResponse` objects.

---

### 2. Pipeline Session Creation
- **URL:** `POST /api/v1/screening/pipeline/sessions`
- **Status Code:** `201 Created`
- **Request Body:**
  ```json
  {
    "candidate_id": "string",
    "opening_id": "string",
    "language": "en"
  }
  ```
- **Response:** Session initialization payload with session metadata and initial questions.

---

### 3. Session Status
- **URL:** `GET /api/v1/screening/sessions/{session_id}/status`
- **Description:** Returns detailed progress status: total questions, answered count, remaining questions, question scores, and behavioral summary.

---

### 4. Start Conversation Flow
- **URL:** `POST /api/v1/screening/sessions/{session_id}/start`
- **Description:** Triggers conversational state machine from `START` to `ASKING` and yields the welcome greeting and first question.

---

### 5. Audio Upload
- **URL:** `POST /api/v1/screening/sessions/{session_id}/audio`
- **Status Code:** `202 Accepted`
- **Content-Type:** `multipart/form-data`
- **Form Fields:** `file` (WAV/MP3/M4A/OGG/FLAC, max 50MB), `question_id` (optional).
- **Response:**
  ```json
  {
    "audio_id": "string",
    "session_id": "string",
    "status": "PENDING",
    "message": "Audio uploaded successfully. Ready for transcription."
  }
  ```

---

### 6. Transcribe Audio
- **URL:** `POST /api/v1/screening/audio/{audio_id}/transcribe`
- **Description:** Runs STT and transcript cleaning, persists transcript record in SQLite.
- **Response:** `ScreeningTranscriptDetailResponse`.

---

### 7. Submit Text Response
- **URL:** `POST /api/v1/screening/sessions/{session_id}/answers/text`
- **Content-Type:** `application/json` or `application/x-www-form-urlencoded`
- **Parameters:** `question_id` (string), `answer_text` (string).
- **Response:** Pipeline result containing `transcript`, `answer` (with intent and extracted entities), `score`, `behavioral` signals, and `next_question`.

---

### 8. Complete Session
- **URL:** `POST /api/v1/screening/sessions/{session_id}/complete`
- **Description:** Concludes screening session, computes aggregate score, runs full behavioral analysis, and builds final report.

---

### 9. Retrieve Session Report
- **URL:** `GET /api/v1/screening/sessions/{session_id}/report`
- **Response:** `ScreeningReportFullResponse` containing `report_json` and `html_report`.

---

### 10. List Candidate Reports
- **URL:** `GET /api/v1/screening/candidates/{candidate_id}/reports`
- **Response:** Array of historical screening reports for the candidate.

