# Day 17 — ATS Testing Report

## Overview

This report documents the ATS system testing methodology, results, and findings for the ZecPath AI Hiring System. Testing was performed using the root application's integrated ATS workflow.

## Testing Approach

### Test Dataset

**Source:** Synthetic test data only. No real candidate data was used.

**Composition:**
- Technical roles: Data Analyst, Software Developer
- Experience levels: Fresher (0-1 yr), Junior (1-3 yr), Mid (3-5 yr), Senior (5+ yr)
- Resume formats: TXT (primary), PDF, DOCX tested via upload endpoints

**Size:** 10 synthetic candidate profiles across 2 job openings

### Manual Review Ground Truth

**Status:** NOT AVAILABLE

A review template was created at `data/evaluation/day17_ats_review_template.csv` with columns:
- job_id, job_title, candidate_name, ai_score, ai_decision, ai_rank
- manual_decision (SHORTLISTED/REVIEW/REJECTED)
- profile_category
- review_notes

**No human reviewers have completed this template.** All accuracy metrics below are from synthetic test arithmetic verification only, not from actual human-labeled data.

### Test Execution

Tests executed via pytest:
```bash
python -m pytest tests/test_day16_day23.py -v
python -m pytest tests/test_api.py -v
```

## Test Results Summary

### Integration Tests (9 tests) — ALL PASSED

| Test | Description | Status |
|------|-------------|--------|
| `test_eligibility_uses_current_ats_score_and_re_evaluates_after_change` | Eligibility fingerprint re-evaluation | ✅ PASSED |
| `test_eligibility_rejects_only_explicit_failed_threshold_and_checks_ownership` | Explicit threshold rejection, ownership check | ✅ PASSED |
| `test_eligibility_configuration_validation_and_authentication` | Config validation, auth required | ✅ PASSED |
| `test_screening_question_bank_filters_and_pending_translations` | Question filtering, language handling | ✅ PASSED |
| `test_transcript_session_lifecycle_and_persistence` | Session create, segments, interactions, status flow | ✅ PASSED |
| `test_transcript_validation_and_candidate_job_binding` | Validation, cross-job rejection | ✅ PASSED |
| `test_job_description_parser_requires_explicit_sections` | JD parser explicit heading behavior | ✅ PASSED |
| `test_ats_metrics_only_accept_aligned_reviewed_examples` | Metric helpers arithmetic verification | ✅ PASSED |
| `test_root_day16_to_day23_workflow_with_synthetic_resume` | Full end-to-end synthetic workflow | ✅ PASSED |

### API Tests (27 tests) — ALL PASSED

Core API functionality verified:
- Authentication & session management
- Job opening CRUD
- Candidate CRUD
- Resume upload/processing (TXT, PDF, DOCX)
- Resume parsing
- ATS scoring with evidence
- Score invalidation on input changes
- Persisted shortlisting
- Screening reports
- Rate limiting & security

### Schema Validation Tests — ALL PASSED

- Screening question dataset validation: 17 questions, 13 roles, 7 categories ✅
- JSON Schema validation for transcripts ✅

## Accuracy Metrics

**NOT MEASURED — NO HUMAN-REVIEWED LABELS EXIST**

The following metrics require human-labeled ground truth:
- Precision, Recall, F1 Score
- Confusion Matrix
- Ranking metrics (Precision@K, NDCG)
- Score correlation with human judgment

**Placeholder Test Only:** `tests/test_day16_day23.py::test_ats_metrics_only_accept_aligned_reviewed_examples` verifies the arithmetic of `binary_metrics()` helper function using synthetic boolean arrays. This is NOT an ATS evaluation.

## Mismatch Analysis

**NOT PERFORMED — NO GROUND TRUTH LABELS**

Without human-reviewed labels, mismatch categories cannot be identified:
- Skill extraction mismatches
- Experience calculation errors
- Semantic matching false positives/negatives
- Score weighting disagreements
- Ranking inversions
- Shortlisting decision differences

## Component-Level Test Coverage

| Component | Test Coverage | Notes |
|-----------|---------------|-------|
| Job Description Parser | ✅ Explicit headings, warnings, unstructured fallback | Conservative parser |
| Resume Upload | ✅ TXT, PDF, DOCX, size limits, type validation | Background processing |
| Resume Parsing | ✅ Text extraction, section data | Day 5-11 pipeline |
| Skill Extraction | ✅ Via scoring evidence | Day 9 |
| Experience Parsing | ✅ Via scoring evidence | Day 10 |
| Education Parsing | ✅ Via scoring evidence | Day 11 |
| Semantic Matching | ✅ Mocked embeddings in tests | Day 12 requires model |
| ATS Scoring | ✅ Weighted formula, evidence persistence | Day 13 |
| Ranking | ✅ Score-based sort, rank assignment | Day 14 |
| Shortlisting | ✅ Threshold filter, human review flag | Day 14 |
| Eligibility Engine | ✅ All rule types, fingerprint re-eval | Day 21 |
| Screening Questions | ✅ Filters, translations, pending handling | Day 22 |
| Transcript Storage | ✅ Segments, interactions, validation | Day 23 |

## Known Test Gaps

1. **No human-labeled evaluation dataset** — Cannot report accuracy
2. **No fairness/subgroup testing** — No authorized demographic data
3. **No load/performance testing** — Day 18 baseline not established
4. **No browser/UI regression testing** — Dashboard not exercised
5. **No real PDF/DOCX parsing validation** — Tests use mocked/simple files
6. **No semantic model availability testing** — Mocked in CI
7. **No concurrent request testing** — Background tasks not stress-tested

## Recommendations

1. **Priority 1:** Collect permissioned, double-reviewed candidate/job pairs with human decisions
2. **Priority 2:** Define evaluation slices (role, experience, format) before labeling
3. **Priority 3:** Establish performance baseline with realistic fixtures
4. **Priority 4:** Add browser automation for dashboard workflows
5. **Priority 5:** Test with production-scale resume volumes and formats

## Test Artifacts

| Artifact | Location |
|----------|----------|
| Review template (empty) | `data/evaluation/day17_ats_review_template.csv` |
| Integration tests | `tests/test_day16_day23.py` |
| API tests | `tests/test_api.py` |
| Schema tests | `tests/test_schemas.py` |
| Metric helpers | `src/ats_evaluation.py` |
| Dataset validator | `src/validate_screening_dataset.py` |