# DAY 38 – APTITUDE LOGIC DESIGN
## Cognitive Reasoning, Situational Judgment Scenarios & Multi-Dimensional Rubric

- **Project:** ZecPath – AI-Powered Resume Screening and Hiring Assistant
- **Stage:** Day 38 – Aptitude Logic Design
- **Module Path:** `src/hr_aptitude_engine.py` & `day38_aptitude_logic/`
- **Documentation File:** `day38_aptitude_logic/docs/day38_aptitude_logic_design.md`
- **Verification Status:** VERIFIED

---

## 1. OBJECTIVE

The objective of Day 38 is to incorporate cognitive reasoning and situational judgment scenarios into the HR interview process. The module provides structured problem-solving scenarios, evaluates candidate analytical trade-offs using transparent multi-dimensional rubrics, clearly separates factual correctness from explanation quality, and prevents answer leakage from question repositories into candidate-facing interfaces.

---

## 2. DETAILED TASKS COMPLETED

1. **Reasoning-Based Question Bank:** Designed structured reasoning and situational scenarios:
   - High-severity incident triage (e.g. database pool exhaustion during flash sales).
   - Sprint deadline conflict vs payment architecture redesign.
   - Microservices vs modular monolith architectural trade-offs.
   - Resource-constrained stakeholder prioritization.
2. **Multi-Dimensional Rubric Scoring:** Built evaluation criteria assessing 4 dimensions (25% weight each):
   - **Problem Decomposition:** Identifying root trade-offs and constraints.
   - **Technical Feasibility:** Sound understanding of technical risks.
   - **Stakeholder Awareness:** Navigating cross-functional dynamics.
   - **Compromise Formulation:** Proposing actionable, win-win alternatives (e.g. phased rollouts with feature flags).
3. **Separation of Explanation Quality vs Correctness:**
   - Differentiated candidates who propose a valid direction but explain it poorly from those who articulate structured decision-making methodologies.
4. **Answer Leakage Prevention:** Sanitized candidate-facing schemas, ensuring ideal answers, rubrics, and evaluation keys remain server-side.
5. **Score Normalization:** Normalized situational judgment scores to a 0.0 to 100.0 scale for downstream aggregation.

---

## 3. RUBRIC EVALUATION MATRIX

| Dimension | Weight | Criteria Evaluated | Jane Doe Score |
|---|---|---|---|
| **Problem Decomposition** | 25.0% | Core trade-off identification (Speed vs Stability) | 92.0 / 100 |
| **Technical Feasibility** | 25.0% | Recognition of payment regression hazards | 90.0 / 100 |
| **Stakeholder Awareness** | 25.0% | Collaborative communication without team friction | 94.0 / 100 |
| **Compromise Formulation** | 25.0% | Actionable feature flag compromise | 95.0 / 100 |
| **Overall Aptitude Score** | **100%** | **Weighted Arithmetic Average** | **92.8 / 100** |

---

## 4. API SPECIFICATION & LIVE EXECUTION

### Aptitude Evaluation Response
- **Route:** `GET /api/v1/hr-interviews/{interview_id}/evaluation`
- **Tags:** `HR Interview Scoring & Reports`
- **Response Section:**
```json
{
  "aptitude": [
    {
      "question_id": "APT_SIT_01",
      "scenario_category": "SITUATIONAL_JUDGMENT",
      "overall_aptitude_score": 92.8,
      "rating": "EXCEPTIONAL",
      "rubric_breakdown": {
        "problem_decomposition": 92.0,
        "technical_feasibility": 90.0,
        "stakeholder_awareness": 94.0,
        "compromise_formulation": 95.0
      },
      "feedback": "Candidate identified payment regression hazards and proposed an effective phased rollout using feature flags."
    }
  ]
}
```

---

## 5. AUTOMATED TEST EVIDENCE

All 8 unit tests in `day38_aptitude_logic_design/tests/test_day38.py` passed with 100% success rate:
- `test_aptitude_question_bank_loading` -> **PASSED**
- `test_situational_scenario_rubric_schema` -> **PASSED**
- `test_problem_decomposition_evaluation` -> **PASSED**
- `test_technical_feasibility_scoring` -> **PASSED**
- `test_stakeholder_awareness_scoring` -> **PASSED**
- `test_compromise_formulation_scoring` -> **PASSED**
- `test_answer_leakage_prevention_sanitization` -> **PASSED**
- `test_separation_of_correctness_and_clarity` -> **PASSED**

---

## 6. SCREENSHOT EVIDENCE

All 6 screenshots were captured live:

1. **Aptitude & Situational Judgment Question Repository:**  
   `day38_aptitude_logic/screenshots/01_reasoning_question_bank.png`  
   *Displays 6 standardized reasoning questions and metadata.*

2. **Situational Judgment Question Presentation:**  
   `day38_aptitude_logic/screenshots/02_situational_judgment_question.png`  
   *Presents the sprint deadline conflict scenario prompt.*

3. **Ingested Candidate Structured Aptitude Answer:**  
   `day38_aptitude_logic/screenshots/03_candidate_aptitude_answer.png`  
   *Shows candidate response outlining 2x2 matrix and feature flag strategy.*

4. **Multi-Dimensional Aptitude Rubric Criteria:**  
   `day38_aptitude_logic/screenshots/04_aptitude_evaluation_rubric.png`  
   *Breaks down the 4 evaluation dimensions and point allocations.*

5. **Calculated Reasoning & Situational Judgment Score:**  
   `day38_aptitude_logic/screenshots/05_reasoning_score_output.png`  
   *Final calculated aptitude score (92.8 / 100) and feedback.*

6. **Aptitude Evaluation Result Card:**  
   `day38_aptitude_logic/screenshots/06_aptitude_api_output.png`  
   *UI card view of dimension scores and technical risk mitigations.*

---

## 7. DELIVERABLES & LIMITATIONS

### Deliverables
- `src/hr_aptitude_engine.py`: Aptitude and situational judgment engine.
- `day38_aptitude_logic/docs/day38_aptitude_logic_design.md`: Documentation.
- `day38_aptitude_logic/screenshots/`: 6 verified screenshots.
- `day38_aptitude_logic/tests/test_day38.py`: Test suite.

### Safeguards
- Aptitude exercises measure situational problem decomposition for specific workplace contexts; they do not claim to measure general human intelligence.
