# ZecPath Scoring & Decision Logic

1. **4-Factor ATS Score (`src/ats_scoring_engine.py`):**
   `ATS = 0.40 * Skills + 0.25 * Semantic + 0.20 * Experience + 0.15 * Education` (bounded `0–100`, whole-word skill matching + snippet evidence).
2. **Eligibility (`src/eligibility.py`):**
   Evaluates mandatory skills, minimum experience, and education (`ELIGIBLE`, `REVIEW_REQUIRED`, `REJECTED`).
3. **Screening / HR / Technical / Machine Test:**
   - Screening: 4-factor rubric (Clarity, Relevance, Completeness, Consistency).
   - HR: Fluency, filler/hesitation, aptitude.
   - Technical: 5-dimension rubric + depth (`shallow`, `moderate`, `deep`).
   - Machine Test: AST & static code quality checks (`src/machine_test_engine.py`).
4. **Cross-Round Aggregation (`src/cross_round_scoring_engine.py`):**
   Role-weighted mean over completed stages; missing stages use `exclude_and_renormalize` (never silent `0`).
5. **Final Recommendation (`src/final_recommendation_engine.py`):**
   `SELECTED`, `HOLD_REVIEW`, or `REJECTED` with mandatory eligibility override and `Confidence = 0.50 * Coverage + 0.30 * Evidence + 0.20 * Consistency`.
