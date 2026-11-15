# DAY 37 – HR INTERVIEW SCORING ENGINE
## Explainable 4-Factor Scoring Engine, Configurable Weights & Recruiter Auditability

- **Project:** ZecPath – AI-Powered Resume Screening and Hiring Assistant
- **Stage:** Day 37 – HR Interview Scoring Engine
- **Module Path:** `src/hr_scoring_engine.py` & `day37_hr_interview_scoring/`
- **Documentation File:** `day37_hr_interview_scoring/docs/day37_hr_interview_scoring_engine.md`
- **Verification Status:** VERIFIED

---

## 1. OBJECTIVE

The objective of Day 37 is to synthesize all candidate interview responses, linguistic evaluations, behavioral signals, and consistency metrics into an explainable, normalized 0 to 100 overall HR Interview Score. The scoring engine utilizes a transparent, configurable weight matrix, normalizes variations in interview duration, provides recruiter-readable mathematical breakdowns, and ensures confidence indicators never become arbitrary automatic disqualifiers.

---

## 2. DETAILED TASKS COMPLETED

1. **Scoring Parameter Definition:** Integrated 4 core evaluation factors:
   - **Answer Relevance:** Factual alignment of responses with question intent and job requirements.
   - **Communication Score:** Multi-factor linguistic fluency, vocabulary, grammar, and STAR answer structure.
   - **Cross-Turn Consistency:** Factual coherence across questions and absence of contradictions.
   - **Confidence Indicators:** Controlled observable speech stability and low hesitation density.
2. **Configurable Weight Matrix:** Established strict weight distributions summing to exactly 1.00 (100.0%):
   - Relevance: $W_1 = 0.40$ (40%)
   - Communication: $W_2 = 0.25$ (25%)
   - Consistency: $W_3 = 0.20$ (20%)
   - Confidence: $W_4 = 0.15$ (15%)
3. **Score Normalization:** Handled variable numbers of questions (4 to 8 turns) and normalized scores to a standard 0.0 to 100.0 scale.
4. **Missing Value Transparency:** Prevented silent zero-imputations; missing audio signals default to a neutral benchmark (75.0) accompanied by an explicit missing-data audit flag.
5. **Recruiter Explanation Generation:** Produced natural-language mathematical explanations detailing the exact weighted contribution of each sub-score.
6. **Candidate Score Card:** Formatted structured score output with progress meters, qualitative rating badges, and actionable hiring recommendations.

---

## 3. MATHEMATICAL FORMULATION & WORKED EXAMPLE

### Mathematical Formula
$$\text{Overall HR Score} = (\text{Relevance} \times 0.40) + (\text{Communication} \times 0.25) + (\text{Consistency} \times 0.20) + (\text{Confidence} \times 0.15)$$

### Worked Example (Jane Doe - Candidate `cand_0b8dad2d`)
- $\text{Relevance} = 88.0 \implies 88.0 \times 0.40 = 35.20\text{ pts}$
- $\text{Communication} = 88.4 \implies 88.4 \times 0.25 = 22.10\text{ pts}$
- $\text{Consistency} = 95.0 \implies 95.0 \times 0.20 = 19.00\text{ pts}$
- $\text{Confidence} = 82.5 \implies 82.5 \times 0.15 = 12.38\text{ pts}$
- **Total Weighted Sum:** $35.20 + 22.10 + 19.00 + 12.38 = 88.68 \approx \mathbf{88.7 / 100}$
- **Classification:** `STRONG CANDIDATE`
- **Recommended Action:** `PROCEED_TO_FINAL_ROUND`

---

## 4. API SPECIFICATION & LIVE EXECUTION

### Evaluation Score Endpoint
- **Route:** `GET /api/v1/hr-interviews/{interview_id}/evaluation`
- **Tags:** `HR Interview Scoring & Reports`
- **Response Section:**
```json
{
  "score": {
    "interview_id": "hr_session_d37_demo",
    "overall_hr_score": 88.7,
    "score_status": "STRONG",
    "weights_used": {
      "relevance": 0.40,
      "communication": 0.25,
      "consistency": 0.20,
      "confidence": 0.15
    },
    "component_breakdown": {
      "relevance_score": 88.0,
      "communication_score": 88.4,
      "consistency_score": 95.0,
      "confidence_score": 82.5
    },
    "score_explanation": "Overall score of 88.7/100 driven by high relevance (35.2 pts) and exceptional consistency (19.0 pts)."
  }
}
```

---

## 5. AUTOMATED TEST EVIDENCE

All 5 unit tests in `day37_hr_interview_scoring_engine/tests/test_day37.py` passed with 100% success rate:
- `test_weight_sum_strictly_100_percent` -> **PASSED**
- `test_score_calculation_normalization_0_to_100` -> **PASSED**
- `test_component_contribution_arithmetic` -> **PASSED**
- `test_missing_component_fallback_safeguard` -> **PASSED**
- `test_score_explanation_generation` -> **PASSED**

---

## 6. SCREENSHOT EVIDENCE

All 6 screenshots were captured live:

1. **Configurable Scoring Weights Configuration:**  
   `day37_hr_interview_scoring/screenshots/01_weight_configuration.png`  
   *Displays JSON configuration validating weights sum to 1.00.*

2. **4-Factor Weighted Score Breakdown Calculation:**  
   `day37_hr_interview_scoring/screenshots/02_component_scores_breakdown.png`  
   *Step-by-step arithmetic breakdown showing point contributions.*

3. **Final HR Score & Explainable Factor Contribution:**  
   `day37_hr_interview_scoring/screenshots/03_final_hr_score.png`  
   *Final overall score (88.7 / 100) and qualitative status.*

4. **Recruiter Score Explanation & Audit Trace:**  
   `day37_hr_interview_scoring/screenshots/04_score_explanation_details.png`  
   *Clear verbal rationale explaining the math to recruiters.*

5. **Candidate HR Score Card UI View:**  
   `day37_hr_interview_scoring/screenshots/05_candidate_hr_score_report.png`  
   *Card view with sub-score progress bars and proceed recommendation.*

6. **Live Swagger API Evaluation Scoring Response:**  
   `day37_hr_interview_scoring/screenshots/06_scoring_api_response.png`  
   *Live Swagger UI execution displaying complete score model.*

---

## 7. DELIVERABLES & LIMITATIONS

### Deliverables
- `src/hr_scoring_engine.py`: Scoring engine and explainability generator.
- `day37_hr_interview_scoring/config/scoring_parameters.json`: Configuration.
- `day37_hr_interview_scoring/docs/day37_hr_interview_scoring_engine.md`: Technical report.
- `day37_hr_interview_scoring/screenshots/`: 6 verified screenshots.
- `day37_hr_interview_scoring/tests/test_day37.py`: Test suite.

### Safeguards
- Rejection cannot be triggered by a single low behavioral metric.
- All scoring parameters are fully auditable; zero black-box heuristics.
