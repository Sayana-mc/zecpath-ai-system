# Day 41–52 REST API Documentation

This document describes all REST API endpoints added and integrated as part of Days 41–52. All endpoints are mounted on `/api/v1` and require recruiter authentication via HTTP Bearer token or cookie session.

---

## 1. Technical Interview Subsystem

### `POST /api/v1/technical-interviews`
Creates a new technical interview session.
- **Request Body (`TechnicalInterviewCreateRequest`):**
  ```json
  {
    "candidate_id": "cand_uuid",
    "opening_id": "job_uuid",
    "target_role": "Backend Engineer",
    "experience_level": "mid"
  }
  ```
- **Response (201 Created, `TechnicalInterviewSessionResponse`):**
  ```json
  {
    "session_id": "TECH_SESSION_ID",
    "candidate_id": "cand_uuid",
    "opening_id": "job_uuid",
    "target_role": "Backend Engineer",
    "experience_level": "mid",
    "status": "CREATED",
    "created_at": "ISO_TIMESTAMP",
    "updated_at": "ISO_TIMESTAMP"
  }
  ```

### `POST /api/v1/technical-interviews/{session_id}/start`
Transitions session status to `IN_PROGRESS` and seeds technical questions.

### `GET /api/v1/technical-interviews/{session_id}/questions`
Returns all assigned technical interview questions for the session.

### `POST /api/v1/technical-interviews/{session_id}/answers`
Evaluates a candidate's answer against the 5-dimension rubric and depth classification.
- **Request Body (`TechnicalAnswerSubmitRequest`):**
  ```json
  {
    "question_id": "Q_UUID",
    "answer_text": "Detailed architectural answer text..."
  }
  ```
- **Response (200 OK, `TechnicalAnswerEvaluationResponse`):**
  ```json
  {
    "response_id": "TRSP_UUID",
    "session_id": "TECH_SESSION_ID",
    "question_id": "Q_UUID",
    "score": 88.5,
    "depth_level": "deep",
    "parameter_scores": {
      "accuracy": 4.5,
      "depth": 4.5,
      "logical_reasoning": 4.2,
      "real_world_applicability": 4.0
    },
    "feedback": "Evaluated as deep response with score 88.5/100."
  }
  ```

### `POST /api/v1/technical-interviews/{session_id}/complete`
Finalizes the technical interview session, aggregates response scores, and marks status `COMPLETED`.

---

## 2. Machine Test Subsystem

### `POST /api/v1/machine-tests/assignments`
Assigns a machine test to a candidate.
- **Request Body (`MachineTestAssignmentRequest`):**
  ```json
  {
    "candidate_id": "cand_uuid",
    "opening_id": "job_uuid",
    "task_type": "coding",
    "time_limit_minutes": 60
  }
  ```
- **Response (201 Created, `MachineTestAssignmentResponse`)**

### `POST /api/v1/machine-tests/{test_id}/submit`
Submits solution code and executes evaluation rubric.
- **Request Body (`MachineTestSubmissionRequest`):**
  ```json
  {
    "code_content": "def solution(): ...",
    "elapsed_time_minutes": 25.0
  }
  ```
- **Response (200 OK, `MachineTestSubmissionResponse`):**
  ```json
  {
    "submission_id": "sub_uuid",
    "test_id": "test_uuid",
    "candidate_id": "cand_uuid",
    "total_score": 86.5,
    "rubric_scores": {
      "correctness": 88.0,
      "efficiency": 85.0,
      "code_quality": 88.0,
      "problem_solving": 90.0,
      "time_management": 85.0
    },
    "evaluation_summary": "Scored 86.5/100. Status: STRONG"
  }
  ```

---

## 3. Compliance, Integrity & Behavioral Subsystems

### `POST /api/v1/candidates/{candidate_id}/integrity-records`
Records consented session integrity events (tab switch, window blur, external audio).
- Automatically computes risk level (`LOW`, `MODERATE`, `HIGH`).
- Enforces strict zero automatic rejection rule.

### `POST /api/v1/candidates/{candidate_id}/behavioral-records`
Records consented communicative observations and computes signal consistency index.
- Includes mandatory assistive non-binding disclaimer.

---

## 4. Cross-Round Unified Fit & Final Recommendation

### `POST /api/v1/candidates/{candidate_id}/cross-round-evaluation`
Calculates 5-round unified fit percentage using role weights and `exclude_and_renormalize` policy.
- Identifies anomalies and discrepancies.

### `POST /api/v1/candidates/{candidate_id}/final-recommendation`
Generates an explainable final recommendation (`SELECTED`, `HOLD_REVIEW`, `REJECTED`) with evidence completeness confidence and auditable reasons.

### `POST /api/v1/final-recommendations/{recommendation_id}/decision`
Allows authorized recruiter to approve, override, or reject the AI recommendation with justification notes.

