# Day 17 — ATS Accuracy Metrics

## Status: NOT MEASURED

**Reason:** No human-reviewed ground truth labels exist in the repository.

## Required Data for Metrics

To calculate meaningful accuracy metrics, the following are required:

| Data | Status |
|------|--------|
| Permissioned candidate resumes | ❌ Not available |
| Job descriptions with recruiter-verified requirements | ❌ Not available |
| Double-reviewed match decisions (SHORTLISTED/REVIEW/REJECTED) | ❌ Not available |
| Reviewer agreement metrics (Cohen's kappa) | ❌ Not available |
| Held-out test set (separate from development) | ❌ Not available |
| Defined evaluation slices (role, experience, format) | ❌ Not defined |

## Metric Definitions (For Future Use)

### Binary Classification Metrics

For the decision categories SHORTLISTED/REVIEW vs REJECTED:

```python
def binary_metrics(y_true: list[bool], y_pred: list[bool]) -> dict:
    """
    Returns:
        - sample_count
        - precision = TP / (TP + FP)
        - recall = TP / (TP + FN)
        - f1 = 2 * precision * recall / (precision + recall)
        - accuracy = (TP + TN) / total
        - confusion_matrix: {true_positive, true_negative, false_positive, false_negative}
    """
```

**Implemented in:** `src/ats_evaluation.py`

### Ranking Metrics

For candidate ranking quality:

| Metric | Formula | Purpose |
|--------|---------|---------|
| Precision@K | Relevant@K / K | Top-K shortlist quality |
| Recall@K | Relevant@K / Total Relevant | Coverage of good candidates |
| NDCG@K | DCG@K / IDCG@K | Rank-aware quality |
| MRR | 1 / rank of first relevant | First hit quality |

### Extraction Metrics

For skill/experience/education extraction:

| Metric | Definition |
|--------|------------|
| Skill Precision | Correct extracted skills / Total extracted skills |
| Skill Recall | Correct extracted skills / Total actual skills |
| Experience MAE | Mean absolute error in years |
| Education Accuracy | Exact degree match rate |

### Score Calibration

| Metric | Definition |
|--------|------------|
| Brier Score | Mean squared error of predicted probabilities |
| Reliability Diagram | Observed vs predicted score bins |
| ECE | Expected Calibration Error |

## Current Test Verification

Only arithmetic verification of metric functions performed:

```python
# tests/test_day16_day23.py
binary_metrics(
    [True, False, True, False],
    [True, True, False, False]
) == {
    "sample_count": 4,
    "precision": 0.5,
    "recall": 0.5,
    "f1": 0.5,
    "accuracy": 0.5,
    "confusion_matrix": {"true_positive": 1, "false_positive": 1, "false_negative": 1, "true_negative": 1}
}
```

This verifies the helper function, NOT the ATS system.

## Blockers

1. **No evaluation dataset** — Cannot proceed without labeled data
2. **Policy decisions needed** — What constitutes a "correct" match?
3. **Resource requirement** — Requires qualified recruiter reviewers
4. **Legal/privacy** — Real candidate data requires consent and governance

## Next Steps

1. Define evaluation protocol and label definitions
2. Obtain organizational approval for data collection
3. Recruit qualified reviewers (2+ per example for agreement)
4. Build labeled dataset (minimum 100+ examples per slice)
5. Run evaluation and report with confidence intervals
6. Document limitations and slice-specific performance

## Related Files

- `src/ats_evaluation.py` — Metric calculation helpers
- `data/evaluation/day17_ats_review_template.csv` — Empty review template
- `tests/test_day16_day23.py::test_ats_metrics_only_accept_aligned_reviewed_examples` — Arithmetic test