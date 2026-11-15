# DAY 33 – HR INTERVIEW ENGINE DESIGN
## AI HR Interview Subsystem Architecture & Conversation State Machine

- **Project:** ZecPath – AI-Powered Resume Screening and Hiring Assistant
- **Stage:** Day 33 – Foundational HR Interview Engine
- **Module Path:** `src/hr_interview_engine.py` & `day33_hr_interview_engine/`
- **Documentation File:** `day33_hr_interview_engine/docs/day33_hr_interview_engine_design.md`
- **Verification Status:** VERIFIED

---

## 1. OBJECTIVE

The primary objective of Day 33 is to design, implement, and validate the foundational architecture of the ZecPath AI HR Interview system. The engine manages structured, role-specific conversational HR interviews, organizes question repositories across six standardized HR categories, supports distinct candidate maturity profiles (Fresher vs Experienced) and role disciplines (Technical vs Non-Technical), and enforces a deterministic 4-phase conversation state machine.

---

## 2. DETAILED TASKS COMPLETED

1. **Question Repository Organization:** Structured the HR interview question bank into the 6 mandatory categories:
   - Self-Introduction
   - Career Journey
   - Strengths and Weaknesses
   - Teamwork and Culture Fit
   - Career Goals
   - Availability and Commitment
2. **Role & Experience Adaptation:** Engineered role-specific filtering supporting:
   - Experience Levels: `FRESHER` (focus on academic foundations, projects, learning agility) vs `EXPERIENCED` (focus on enterprise architecture, leadership, operational resilience).
   - Role Disciplines: `TECHNICAL` (microservices, distributed systems, code quality) vs `NON_TECHNICAL` (stakeholder management, business KPIs, operational agility).
3. **Question Metadata Schema:** Defined granular metadata for every interview question:
   - `question_id`: Unique identifier (e.g. `HR_INTRO_01`, `HR_TECH_01`).
   - `category`: One of the 6 standardized HR categories.
   - `role_type`: Target discipline (`TECHNICAL`, `NON_TECHNICAL`, `ALL`).
   - `experience_level`: Target level (`FRESHER`, `EXPERIENCED`, `ALL`).
   - `question_text`: Standardized conversational prompt.
   - `expected_indicators`: Key evaluation points and competencies.
   - `followup_eligible`: Boolean flag enabling adaptive probing.
   - `difficulty`: Normalized float rating (1.0 - 3.0).
4. **Interview Session State Tracking:** Designed a persistent ledger tracking:
   - `interview_id`: Unique session UUID.
   - `candidate_id` & `opening_id`: Foreign key linkages.
   - `current_phase`: Current conversation phase.
   - `current_question_id`: Active question pointer.
   - `conversation_history`: Complete turn-by-turn question/response logs.
   - `status`: Lifecycle status (`CREATED`, `IN_PROGRESS`, `PAUSED`, `COMPLETED`).
5. **4-Phase Conversation State Machine:** Implemented deterministic FSM transitions:
   - `INTRODUCTION` → `CORE_HR` → `ROLE_BASED` → `CLOSING` → `COMPLETED`.
6. **Repetition Safeguards:** Verified that dynamic question selection prevents duplicates within the same interview session.
7. **Automated Testing:** Implemented comprehensive unit and integration tests verifying question generation, state progression, and invalid transitions.

---

## 3. SYSTEM ARCHITECTURE & LOGIC

```
[Candidate Ingestion] ────────► [Job Opening Requirements]
           │                                 │
           ▼                                 ▼
┌────────────────────────────────────────────────────────┐
│             HR Interview Engine (src/hr_interview_engine.py)             │
│  - Question Bank Validator (6 Categories)              │
│  - Role Filter (Technical / Non-Technical)            │
│  - Maturity Filter (Fresher / Experienced)             │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│        Conversation State Machine (FSM Controller)     │
│                                                        │
│  [INTRODUCTION] ──► [CORE_HR] ──► [ROLE_BASED] ──► [CLOSING]
│         │               │              │             │
│         └───────────────┴──────────────┴─────────────┘
│                                 │
│                                 ▼
│                    [COMPLETED SESSION LEDGER]           │
└────────────────────────────────────────────────────────┘
```

---

## 4. API SPECIFICATION & LIVE EXECUTION

### Session Creation Endpoint
- **Route:** `POST /api/v1/hr-interviews`
- **Tags:** `HR Interview Engine`
- **Request Payload:**
```json
{
  "candidate_id": "cand_0b8dad2d",
  "opening_id": "job_fb5b1b8c",
  "experience_level": "EXPERIENCED",
  "role_type": "TECHNICAL"
}
```
- **Response Status:** `201 Created`
- **Response Body:**
```json
{
  "interview_id": "hr_session_d33_e2a1b0",
  "candidate_id": "cand_0b8dad2d",
  "opening_id": "job_fb5b1b8c",
  "experience_level": "EXPERIENCED",
  "role_type": "TECHNICAL",
  "current_phase": "CREATED",
  "status": "CREATED",
  "created_at": "2026-11-15T15:45:00Z"
}
```

### Questions Retrieval Endpoint
- **Route:** `GET /api/v1/hr-interviews/{interview_id}/questions`
- **Response Status:** `200 OK` (Returns ordered list of 6 role-tailored questions).

---

## 5. AUTOMATED TEST EVIDENCE

All 5 day-specific unit tests passed with 100% success rate:
- `tests/test_day33.py::test_question_bank_categories` -> **PASSED**
- `tests/test_day33.py::test_role_based_question_selection` -> **PASSED**
- `tests/test_day33.py::test_fresher_vs_experienced_filtering` -> **PASSED**
- `tests/test_day33.py::test_fsm_valid_phase_transitions` -> **PASSED**
- `tests/test_day33.py::test_fsm_invalid_transition_rejection` -> **PASSED**

---

## 6. SCREENSHOT EVIDENCE

All 6 screenshots were captured live from actual terminal and Swagger UI executions:

1. **Question Bank 6 Categories & Metadata Architecture:**  
   `day33_hr_interview_engine/screenshots/01_question_bank_categories.png`  
   *Displays the 6 structured categories, difficulty indicators, and metadata validation.*

2. **Role-Based Question Selection (Technical vs Non-Technical):**  
   `day33_hr_interview_engine/screenshots/02_role_based_question_selection.png`  
   *Shows role-based question filtering separating technical system architecture from non-technical business strategy.*

3. **Fresher vs Experienced Question Allocation Matrix:**  
   `day33_hr_interview_engine/screenshots/03_fresher_vs_experienced_selection.png`  
   *Comparative matrix displaying foundational academic questions for Freshers vs senior distributed systems questions for Experienced.*

4. **Interview Session State & Response Tracking:**  
   `day33_hr_interview_engine/screenshots/04_interview_state_structure.png`  
   *JSON ledger showing live session state, current question pointer, and conversation history.*

5. **4-Phase Conversation State Machine Lifecycle:**  
   `day33_hr_interview_engine/screenshots/05_conversation_phase_flow.png`  
   *FSM execution trace demonstrating transition across Introduction, Core HR, Role-Based, and Closing phases.*

6. **Live Swagger API Interview Creation:**  
   `day33_hr_interview_engine/screenshots/06_hr_interview_creation_api.png`  
   *Live Swagger UI execution of `POST /api/v1/hr-interviews` returning HTTP 201 Created and session schema.*

---

## 7. DELIVERABLES & LIMITATIONS

### Deliverables
- `src/hr_interview_engine.py`: Engine implementation and `InterviewFlowStateMachine`.
- `day33_hr_interview_engine/docs/day33_hr_interview_engine_design.md`: Technical report.
- `day33_hr_interview_engine/screenshots/`: 6 verified screenshots.
- `day33_hr_interview_engine/tests/test_day33.py`: Automated test suite.

### Limitations & Safeguards
- Question selection operates deterministically on role metadata; dynamic follow-up questioning is delegated to Day 34.
- State transitions are strictly sequential; skipping phases without completing required core questions is rejected.

