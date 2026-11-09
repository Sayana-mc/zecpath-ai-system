# Day 17 — ATS Mismatch Analysis

## Status: NOT PERFORMED

**Reason:** No human-reviewed ground truth labels exist. Mismatch analysis requires comparing ATS output against human reviewer decisions.

## Mismatch Categories (For Future Analysis)

When labeled data becomes available, mismatches should be categorized as follows:

### 1. Skill Extraction Mismatches

| Sub-type | Description | Example |
|----------|-------------|---------|
| False Positive | Skill extracted but not present | "Power BI" extracted from "PowerPoint" |
| False Negative | Skill present but not extracted | "Python" in resume but not found |
| Synonym Miss | Canonical skill not recognized | "PySpark" not mapped to "Spark" |
| Version Confusion | Version treated as separate skill | "Python 3.9" vs "Python" |
| Context Error | Skill mentioned in wrong context | "Learning Python" extracted as proficiency |

### 2. Experience Extraction Mismatches

| Sub-type | Description | Example |
|----------|-------------|---------|
| Duration Error | Incorrect years calculated | "2020-2023" → 2 years instead of 3 |
| Overlap Miss | Overlapping roles double-counted | Two concurrent jobs counted sequentially |
| Gap Handling | Employment gaps misinterpreted | 6-month gap treated as experience |
| Relevance Miss | Irrelevant experience included | Retail experience for Data Analyst role |
| Seniority Mismatch | Level not captured | "Lead" vs "Senior" not distinguished |

### 3. Education Extraction Mismatches

| Sub-type | Description | Example |
|----------|-------------|---------|
| Degree Miss | Degree not extracted | "B.Tech" not recognized |
| Major Miss | Field of study not captured | "Computer Science" missing |
| Institution Miss | University not extracted | "IIT Bombay" missing |
| Equivalence Error | Non-standard degrees misclassified | "Diploma" vs "Bachelor's" |

### 4. Semantic Matching Mismatches

| Sub-type | Description | Example |
|----------|-------------|---------|
| False Match | Unrelated resume scores high | Generic resume matches specific JD |
| Missed Match | Relevant resume scores low | Strong candidate, low semantic score |
| Keyword Overweight | Keywords dominate meaning | "Python" mentioned once scores high |
| Context Loss | Section context ignored | Skills in "Learning" section weighted same |

### 5. Score Weighting Mismatches

| Sub-type | Description | Example |
|----------|-------------|---------|
| Component Imbalance | One component dominates | Skills 90% of score, experience ignored |
| Missing Data Penalty | Zero for missing component | No education → 0 education score |
| Threshold Sensitivity | Small score change flips decision | 64.9 vs 65.1 changes category |

### 6. Ranking Mismatches

| Sub-type | Description | Example |
|----------|-------------|---------|
| Inversion | Better candidate ranked lower | Candidate A > B by human, B > A by ATS |
| Tie Handling | Equal scores, arbitrary order | Same score, different human ranking |
| Cluster Miss | Similar candidates separated | 3 similar candidates not adjacent |

### 7. Shortlisting Mismatches

| Sub-type | Description | Example |
|----------|-------------|---------|
| False Shortlist | Unqualified candidate shortlisted | Missing mandatory skill, high score |
| False Reject | Qualified candidate rejected | Low score but has all requirements |
| Boundary Error | Near-threshold inconsistency | 59.9 REVIEW, 60.1 SHORTLISTED |

## Analysis Template

For each mismatch found during evaluation:

```markdown
### Mismatch ID: MM-XXX

**Input:**
- Resume: [anonymized excerpt]
- Job Description: [anonymized excerpt]

**Expected (Human):** [Decision + reasoning]

**Actual (ATS):** [Score, decision, evidence]

**Category:** [From taxonomy above]

**Root Cause:** [Technical explanation]

**Proposed Fix:** [Code/config change]

**Verification:** [Test case to add]
```

## Current State

No mismatches have been documented because no evaluation has been run.

## Blockers

1. No labeled evaluation dataset
2. No defined "correct" behavior for edge cases
3. No reviewer pool established

## Related Files

- `src/ats_evaluation.py` — `find_mismatches()` helper (requires labeled data)
- `tests/test_day16_day23.py` — Integration tests (synthetic only)