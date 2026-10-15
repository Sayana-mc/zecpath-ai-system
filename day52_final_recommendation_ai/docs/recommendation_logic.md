

\# Day 52 - Recommendation Logic



\## 1. Objective



Generate an explainable hiring recommendation using the Day 51 unified

candidate score, evaluation completeness, confidence, and evidence-backed

risk indicators.



\## 2. Decision categories



\- SELECTED: score meets the configured selection threshold and required

&#x20; evidence is complete, confidence is sufficient, and no configured

&#x20; review condition is unresolved.

\- HOLD\_REVIEW: a candidate requires additional assessment or human review.

\- REJECTED: the score is below the configured review threshold when

&#x20; sufficient evidence is available and no unresolved review condition exists.



\## 3. Hybrid logic



The engine combines numerical score thresholds with deterministic rules.



1\. Validate assessment fields and score ranges.

2\. Calculate evidence confidence.

3\. Check integrity and job-related behavior flags.

4\. Check assessment status and completed-round coverage.

5\. Apply the score thresholds only when no review condition overrides them.

6\. Return the recommendation and its reasons.



\## 4. Decision table



| Condition | Recommendation |

|---|---|

| Risk flag or incomplete evidence | HOLD\_REVIEW |

| Confidence below selection threshold | HOLD\_REVIEW |

| Complete evidence and score >= 80 | SELECTED |

| Score >= 60 and < 80 | HOLD\_REVIEW |

| Complete evidence and score < 60 | REJECTED |



\## 5. Safeguards



Risk flags trigger verification; they do not automatically reject candidates.

Missing evidence is not treated as a zero score. The output is advisory and

requires human review before an employment action.



Thresholds are prototype configuration values and require validation before

any real-world use.



