# Day 18 — ATS Stability Report

## Status: STABILITY TESTS PASS FOR ROOT APPLICATION

The root application's ATS workflow has been verified for basic stability through integration tests. No dedicated stability/stress testing has been performed beyond the pytest suite.

## Test Results

### Integration Test Suite (47 tests) — ALL PASSED

```bash
python -m pytest tests/ -v
# 47 passed in 57.09s
```

### Focused ATS Tests (9 tests) — ALL PASSED

```bash
python -m pytest tests/test_day16_day23.py -v
# 9 passed in 11.93s
```

### Tested Stability Scenarios

| Scenario | Test Coverage | Result |
|----------|---------------|--------|
| Resume upload → processing → parse | `test_resume_upload_extracts_text_and_links_candidate` | ✅ |
| PDF upload extraction | `test_pdf_upload_extracts_document_text` | ✅ |
| DOCX upload extraction | `test_docx_upload_extracts_document_text` | ✅ |
| Invalid PDF handling | `test_invalid_resume_upload_and_unreadable_pdf_are_reported` | ✅ |
| Upload size limit (5 MiB) | `test_upload_limit_and_interrupted_job_recovery` | ✅ |
| Interrupted job recovery | `test_upload_limit_and_interrupted_job_recovery` | ✅ |
| Score invalidation on resume change | `test_score_is_invalidated_when_its_inputs_change` | ✅ |
| Score invalidation on job change | `test_score_is_invalidated_when_scoring_evidence_changes` | ✅ |
| Score invalidation on candidate skills change | `test_score_is_invalidated_when_its_inputs_change` | ✅ |
| Candidate deletion redacts jobs | `test_deleting_candidate_redacts_saved_resume_processing_results` | ✅ |
| Opening deletion redacts jobs | `test_deleting_opening_redacts_linked_resume_processing_results` | ✅ |
| Candidate deletion during processing | `test_candidate_deletion_during_resume_processing_does_not_restore_resume_text` | ✅ |
| Duplicate email rejection | `test_validation_duplicate_email_and_missing_records` | ✅ |
| Ownership validation (candidate/job) | `test_score_rejects_missing_evidence_and_wrong_job` | ✅ |
| Semantic model unavailable handling | `test_score_returns_service_unavailable_when_local_model_is_missing` | ✅ |
| Eligibility fingerprint re-evaluation | `test_eligibility_uses_current_ats_score_and_re_evaluates_after_change` | ✅ |
| Eligibility cross-job rejection | `test_eligibility_rejects_only_explicit_failed_threshold_and_checks_ownership` | ✅ |
| Transcript segment ordering | `test_transcript_session_lifecycle_and_persistence` | ✅ |
| Transcript validation (speaker, timestamp, question) | `test_transcript_validation_and_candidate_job_binding` | ✅ |
| Screening question translation filtering | `test_screening_question_bank_filters_and_pending_translations` | ✅ |

## Stability Characteristics Verified

### 1. Error Handling
- Invalid file types rejected (400)
- Empty files rejected (400)
- Oversized files rejected (413)
- Missing records return 404
- Ownership mismatches return 409
- Invalid state transitions return 409
- Validation errors return 422
- Model unavailability returns 503

### 2. Data Integrity
- Candidate deletion redacts processing job results
- Opening deletion redacts processing job results
- Candidate deletion during processing → job fails cleanly
- Score invalidation on input changes (resume, job, candidate skills)
- Eligibility fingerprint detects stale evaluations
- Database foreign keys enforce referential integrity

### 3. Concurrency Safety (Single-Process)
- SQLite WAL mode with 10s timeout
- Background tasks run in same process
- Session-based authentication with expiry
- Login rate limiting per IP/username

### 4. Resource Cleanup
- Temporary upload files deleted after processing
- Failed jobs cleaned up on startup (`fail_interrupted_processing_jobs`)
- Expired sessions purged on login

## NOT TESTED / NOT VERIFIED

| Area | Status | Risk |
|------|--------|------|
| Multi-worker deployment | ❌ Not tested | Background tasks, in-memory cache not safe |
| High concurrency (>10 parallel) | ❌ Not tested | SQLite contention, background task queue |
| Large file processing (>50MB) | ❌ Not tested | Memory pressure, timeout |
| Long-running scoring batches | ❌ Not tested | Request timeout, memory accumulation |
| Model reload / version change | ❌ Not tested | Cache invalidation, embedding drift |
| Database migration rollback | ❌ Not tested | Additive-only migrations |
| Network partition / DB lock | ❌ Not tested | Timeout handling |
| Graceful shutdown | ❌ Not tested | Background task interruption |

## Day 18 Standalone Stability Tests

The `day18_ats_optimization/tests/test_stability.py` contains 7 tests for standalone modules:
- Cache hit/miss behavior
- Memory monitoring
- Noisy resume handling
- Entity detection consistency
- Prompt optimization output

**These test isolated modules, not the root application.**

## Recommendations

1. **Add stress testing** — Use `locust` or similar for concurrent load
2. **Test multi-worker** — Verify background task coordination (Redis/Celery needed)
3. **Add chaos testing** — DB locks, model unavailability, disk full
4. **Monitor production metrics** — Latency distributions, error rates, queue depths
5. **Define SLIs/SLOs** — e.g., "99% of resume uploads complete in <30s"

## Related Files

- `tests/test_api.py` — Core API stability tests
- `tests/test_day16_day23.py` — Day 16-23 integration tests
- `day18_ats_optimization/tests/test_stability.py` — Module stability tests
- `src/database.py::fail_interrupted_processing_jobs` — Startup recovery