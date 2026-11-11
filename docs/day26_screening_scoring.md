# Day 26 — Screening Scoring Engine Architecture

## 1. Overview
The Day 26 scoring engine evaluates candidate answers objectively across standardized multi-factor evaluation parameters, providing explainable scores and transparent candidate assessment.

## 2. Parameter Breakdown & Weights
Each screening question response is evaluated across four core dimensions:
1. **Clarity (20% Weight):**
   - Measures sentence structure, coherence, and answer length.
   - Penalizes incoherent fragments or excessively terse responses.
2. **Relevance (35% Weight):**
   - Assesses alignment between candidate response and the expected question intent.
   - Rewarded for relevant topical keywords; penalized for off-topic deviations.
3. **Completeness (25% Weight):**
   - Measures whether the candidate provided comprehensive details (e.g. skills mentioned, experience quantified).
4. **Consistency (20% Weight):**
   - Checks for internal contradictions against previously stated facts (e.g. conflicting years of experience or availability).

## 3. Scoring Scale & Normalization
- Each parameter is scored on a discrete scale of `0 to 5`.
- **Weighted Score:**
  $$\text{Weighted Score} = (0.20 \times \text{Clarity}) + (0.35 \times \text{Relevance}) + (0.25 \times \text{Completeness}) + (0.20 \times \text{Consistency})$$
- **Normalized Score:** Scaled to 0–100 for recruiter dashboard clarity:
  $$\text{Normalized Score} = \left(\frac{\text{Weighted Score}}{5}\right) \times 100$$

## 4. Aggregate Candidate Screening Score
- For a screening session with $N$ evaluated questions:
  $$\text{Overall Screening Score} = \frac{1}{N} \sum_{i=1}^{N} \text{Normalized Score}_i$$
- Scores below threshold (e.g., < 50) or responses with detected contradictions are flagged with `human_review_required = True`.
- Persisted in `screening_question_scores` and `screening_aggregate_scores` database tables.

