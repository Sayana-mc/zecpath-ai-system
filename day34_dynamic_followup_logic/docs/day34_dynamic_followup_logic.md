# DAY 34 – DYNAMIC FOLLOW-UP LOGIC
## Adaptive Questioning Framework, Completeness Evaluation & Repetition Guardrails

- **Project:** ZecPath – AI-Powered Resume Screening and Hiring Assistant
- **Stage:** Day 34 – Dynamic Follow-Up Engine
- **Module Path:** `src/hr_followup_engine.py` & `day34_dynamic_followup/`
- **Documentation File:** `day34_dynamic_followup/docs/day34_dynamic_followup_logic.md`
- **Verification Status:** VERIFIED

---

## 1. OBJECTIVE

The objective of Day 34 is to enable adaptive conversational probing based on real-time candidate verbal answers. Rather than treating an interview as a rigid static questionnaire, the Day 34 engine analyzes response completeness, detects vague or evasive statements, dynamically introduces deepening technical inquiries or concrete example prompts, strictly prevents repetitive questioning loops, and maintains uninterrupted interview context.

---

## 2. DETAILED TASKS COMPLETED

1. **Answer Completeness Detection:** Built multi-factor text analysis evaluating:
   - Word count thresholds (< 15 words evaluated as potentially incomplete).
   - Domain keyword density and substantive content indicators.
   - Transparent, explainable completeness scoring (0.0 - 1.0).
2. **Follow-Up Trigger Logic:** Implemented three distinct follow-up trigger categories:
   - **Clarification:** Triggered when an answer is brief, ambiguous, or lacks specific technical/operational parameters.
   - **Technical Deepening:** Triggered when an answer demonstrates substantive expertise, prompting exploration of architectural trade-offs, scalability limits, or edge cases.
   - **Example-Based Probing:** Triggered when a candidate makes abstract behavioral or soft-skill claims without concrete STAR (Situation, Task, Action, Result) evidence.
3. **Difficulty & Depth Adaptation:** Adapted probe difficulty to response quality:
   - High-depth answers lead to complex scenario questions.
   - Incomplete answers lead to guided clarifying questions before advancing.
4. **Repetition Prevention Guardrails:**
   - Enforced a strict maximum limit of **2 follow-ups per primary question**.
   - Tracked all previously asked questions and follow-ups within the session.
   - Evaluated semantic similarity against previously asked questions; if similarity > 0.80, the redundant follow-up is suppressed.
5. **Interview Context Preservation:** Linked every follow-up to its parent question in the database ledger, ensuring clean return to the primary interview flow.
6. **Deterministic Fallbacks:** When LLM or AI generation is slow, ambiguous, or unavailable, the system deterministically executes rule-based follow-up templates matching the category.

---

## 3. DECISION TREE LOGIC

```
                    [Candidate Ingested Answer]
                                 │
                                 ▼
                     [Completeness Evaluator]
                                 │
       ┌─────────────────────────┼─────────────────────────┐
       ▼                         ▼                         ▼
[Word Count < 15]        [Abstract Claim]       [Substantive Technical]
[Lacks Detail]           [Missing STAR Evidence] [High Keyword Density]
       │                         │                         │
       ▼                         ▼                         ▼
[Trigger: CLARIFICATION] [Trigger: EXAMPLE]    [Trigger: DEEPENING]
"Could you specify the   "Can you share a       "What unexpected trade-
frameworks & metrics?"   specific situation?"   offs did you encounter?"
       │                         │                         │
       └─────────────────────────┬─────────────────────────┘
                                 │
                                 ▼
                   [Repetition & Cap Guardrail]
           ┌─────────────────────┴─────────────────────┐
           ▼                                           ▼
[Follow-Up Count < 2]                      [Follow-Up Count >= 2]
[Deliver Follow-Up Question]               [Suppress Follow-Up & Return
[Increment Count; Maintain Tree]           to Main 4-Phase Interview Flow]
```

---

## 4. API SPECIFICATION & LIVE EXECUTION

### Dynamic Follow-Up Submission Endpoint
- **Route:** `POST /api/v1/hr-interviews/{interview_id}/follow-ups`
- **Tags:** `HR Dynamic Follow-Up`
- **Request Payload:**
```json
{
  "parent_question_id": "HR_EXP_01",
  "followup_type": "deepening",
  "followup_question": "What unexpected trade-offs arose during Kafka implementation?",
  "candidate_response": "We managed schema versioning tightly using Confluent schema registry and dead letter queues."
}
```
- **Response Status:** `201 Created`
- **Response Body:**
```json
{
  "followup_id": "fu_9a8c12b4",
  "interview_id": "hr_session_d34_01",
  "parent_question_id": "HR_EXP_01",
  "followup_type": "deepening",
  "followup_question": "What unexpected trade-offs arose during Kafka implementation?",
  "candidate_response": "We managed schema versioning tightly using Confluent schema registry...",
  "created_at": "2026-11-15T15:46:12Z"
}
```

---

## 5. AUTOMATED TEST EVIDENCE

All 8 unit tests in `day34_dynamic_followup_logic/tests/test_day34.py` passed with 100% success rate:
- `test_completeness_evaluation_incomplete` -> **PASSED**
- `test_completeness_evaluation_detailed` -> **PASSED**
- `test_trigger_clarification_on_vague_answer` -> **PASSED**
- `test_trigger_deepening_on_technical_answer` -> **PASSED**
- `test_trigger_example_on_abstract_claim` -> **PASSED**
- `test_repetition_prevention_blocks_duplicate` -> **PASSED**
- `test_max_followup_cap_enforced` -> **PASSED**
- `test_context_preservation_and_tree_integrity` -> **PASSED**

---

## 6. SCREENSHOT EVIDENCE

All 6 screenshots were captured live:

1. **Incomplete Answer & Clarification Follow-up Trigger:**  
   `day34_dynamic_followup/screenshots/01_incomplete_answer_clarification.png`  
   *Demonstrates vague answer ("I worked on databases") triggering clarification.*

2. **Detailed Answer & Technical Deepening Follow-up:**  
   `day34_dynamic_followup/screenshots/02_detailed_answer_deepening.png`  
   *Shows substantive microservices response triggering Kafka trade-off deepening question.*

3. **Abstract Behavioral Claim & Example-Based Follow-up:**  
   `day34_dynamic_followup/screenshots/03_example_based_followup.png`  
   *Illustrates soft-skill claim prompting a concrete real-world situational example.*

4. **Repetition Prevention & Follow-up Threshold Enforcement:**  
   `day34_dynamic_followup/screenshots/04_repetition_prevention.png`  
   *Shows blocking of duplicate inquiries and enforcement of the max 2 follow-up cap.*

5. **Conversation State Tree Before and After Follow-up:**  
   `day34_dynamic_followup/screenshots/05_conversation_state_followup.png`  
   *Visualizes tree progression, parent-child question linkage, and smooth return to main flow.*

6. **Live Swagger API Follow-Up Execution:**  
   `day34_dynamic_followup/screenshots/06_followup_api_execution.png`  
   *Live Swagger UI execution of `POST /api/v1/hr-interviews/{id}/follow-ups` returning HTTP 201.*

---

## 7. DELIVERABLES & LIMITATIONS

### Deliverables
- `src/hr_followup_engine.py`: Dynamic follow-up decision engine.
- `day34_dynamic_followup/docs/day34_dynamic_followup_logic.md`: Technical documentation.
- `day34_dynamic_followup/screenshots/`: 6 verified screenshots.
- `day34_dynamic_followup/tests/test_day34.py`: Automated test suite.

### Limitations & Ethical Safeguards
- Follow-ups never alter the candidate's core question count unfairly.
- Answer length alone is never used as an evaluation metric; density and semantic relevance govern triggers.
