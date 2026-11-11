# Day 41–52 Architecture & Data Flow Design

## System Architecture Overview

The Day 41–52 subsystem forms the multi-round evaluation and decisioning layer of the ZecPath AI Hiring System. It unifies disparate evaluation modalities into an explainable, auditable hiring pipeline governed by human recruiter authority.

```
+-----------------------------------------------------------------------------------+
|                                 CANDIDATE JOURNEY                                 |
+-----------------------------------------------------------------------------------+
       |                    |                    |                   |
       v                    v                    v                   v
+--------------+   +----------------+   +-----------------+   +---------------+
|   Round 1    |   |    Round 2     |   |     Round 3     |   |   Round 4 & 5 |
|     ATS      |   |  HR Screening  |   |  HR Interview   |   |  Tech & Code  |
| (Resume NLP) |   | (Voice/Speech) |   | (Aptitude/Comm) |   | (Depth/Tasks) |
+--------------+   +----------------+   +-----------------+   +---------------+
       |                    |                    |                   |
       +--------------------+--------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 |    Cross-Round Scoring Engine         |
                 |  (Role Weights & Renormalization)     |
                 +---------------------------------------+
                                     |
                     +---------------+---------------+
                     |                               |
                     v                               v
         +-----------------------+       +-----------------------+
         | Integrity & Behavior  |       | Discrepancy & Anomaly |
         |   Advisory Signals    |       |       Detection       |
         | (Non-punitive alerts) |       |  (Cross-round checks) |
         +-----------------------+       +-----------------------+
                     |                               |
                     +---------------+---------------+
                                     |
                                     v
                 +---------------------------------------+
                 |     Final Recommendation AI           |
                 |  - Confidence (Evidence Completeness) |
                 |  - Classification (Select/Hold/Reject)|
                 |  - Traceable Reasoning & Risk Audit   |
                 +---------------------------------------+
                                     |
                                     v
                 +---------------------------------------+
                 |     Recruiter Decision Workflow       |
                 |  [Approve]   [Override]   [Reject]    |
                 +---------------------------------------+
```

---

## Core Principles & Design Decisions

### 1. Separation of Confidence and Success Probability
As demonstrated in Day 52, `confidence` measures **evidence completeness** (i.e., whether all expected rounds were conducted with sufficient data quality), NOT a predictive likelihood of post-hire job success. The API and UI explicitly expose the `confidence_interpretation`: `"Evidence completeness indicator; not a probability of job success."`

### 2. Fair Handling of Incomplete Assessment Funnels
When a candidate does not participate in all 5 evaluation rounds (e.g., in earlier screening stages or specialized roles), the engine applies `exclude_and_renormalize`. Remaining completed round weights are proportionally scaled so the candidate is evaluated on a true 0–100 scale without penalizing unadministered rounds.

### 3. Non-Punitive Auxiliary Monitoring
Integrity and behavioral observation signals are governed by strict consent:
- Absence of consent halts signal capture without penalty.
- High risk or inconsistency never triggers automatic disqualification; it produces a `HOLD_REVIEW` recommendation with clear review alerts for human recruiters.

### 4. Human-in-the-Loop Supremacy
AI recommendations (`SELECTED`, `HOLD_REVIEW`, `REJECTED`) are strictly advisory. Final hiring status transitions remain locked behind authorized recruiter actions (`APPROVED`, `OVERRIDDEN`, `REJECTED`) with required audit justification notes.

