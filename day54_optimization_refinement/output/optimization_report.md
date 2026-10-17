# Day 54 — Optimization & Refinement Report

## 1. Objective

Evaluate scoring errors, compare thresholds, refine intent matching,
check round consistency and benchmark local processing time.

## 2. Dataset and limitations

- Labelled examples: 12
- Dataset type: SYNTHETIC_LABELLED_EXAMPLES
- Interpretation: Metrics measure agreement with the supplied demo labels only. They are not evidence of real-world hiring accuracy.

## 3. Baseline error analysis

- Threshold: 80
- True positives: 4
- False positives: 0
- True negatives: 5
- False negatives: 3
- Accuracy: 75.00%
- Precision: 100.00%
- Recall: 57.14%
- Specificity: 100.00%
- F1 score: 0.7273
- False-positive IDs: []
- False-negative IDs: ['E04', 'E05', 'E06']

## 4. Threshold comparison

| Threshold | Accuracy | Precision | Recall | F1 | FP | FN |
|---:|---:|---:|---:|---:|---:|---:|
| 50 | 66.67% | 63.64% | 100.00% | 0.7778 | 4 | 0 |
| 55 | 75.00% | 70.00% | 100.00% | 0.8235 | 3 | 0 |
| 60 | 83.33% | 77.78% | 100.00% | 0.8750 | 2 | 0 |
| 65 | 91.67% | 87.50% | 100.00% | 0.9333 | 1 | 0 |
| 70 | 83.33% | 85.71% | 85.71% | 0.8571 | 1 | 1 |
| 75 | 75.00% | 83.33% | 71.43% | 0.7692 | 1 | 2 |
| 80 | 75.00% | 100.00% | 57.14% | 0.7273 | 0 | 3 |
| 85 | 66.67% | 100.00% | 42.86% | 0.6000 | 0 | 4 |
| 90 | 50.00% | 100.00% | 14.29% | 0.2500 | 0 | 6 |

### Best sample threshold

- Threshold with highest sample F1: 65
- Sample F1: 0.9333
- Deployment approval: NOT APPROVED
- Reason: Do not deploy a new threshold based on this small synthetic sample. Validate on representative, independently labelled data and review false positives and false negatives first.

## 5. Intent detection test

- Input: Explain this candidate's role fit
- Detected intent: explain_role_fit
- Status: MATCHED_RULE

## 6. Refined scoring example

- Advisory band: STRONG_FIT_FOR_REVIEW
- Status: ADVISORY_RESULT_REQUIRES_HUMAN_DECISION
- Round average: 82.0
- Round score gap: 15.0
- Review reasons: []
- Human review required: YES

## 7. Processing benchmark

- Iterations per operation: 1000
- Scoring average (ms): 0.010618
- Intent average (ms): 0.015165
- Note: Local microbenchmark of in-process Python functions. It excludes database, network, model inference, file I/O and end-to-end application latency.

## 8. Optimization actions

1. Evaluate false positives and false negatives against labelled outcomes.
2. Compare candidate thresholds using precision, recall and F1.
3. Keep threshold changes disabled until independently validated.
4. Send unknown or ambiguous intents for clarification.
5. Flag incomplete rounds and large score gaps for human review.
6. Benchmark against a recorded baseline before claiming speed improvements.

## 9. Conclusion

This run demonstrates an optimization and measurement workflow. The synthetic dataset cannot establish improved real-world hiring accuracy. Final employment decisions must remain under qualified human review.
