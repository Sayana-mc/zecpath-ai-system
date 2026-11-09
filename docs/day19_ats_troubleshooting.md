# Day 19 — ATS Troubleshooting Guide

## Quick Diagnosis

| Symptom | Likely Cause | First Check |
|---------|--------------|-------------|
| 500 on `/candidates/score` | Semantic model not loaded | Check logs for `ScoringModelUnavailableError` |
| 409 on score: "Candidate not in opening" | Wrong job_id in request | Verify `candidate.opening_id == job_id` |
| 409 on eligibility: "Configure eligibility first" | No config for opening | PUT `/openings/{id}/eligibility-config` |
| 422 on upload: "Unsupported format" | Wrong file extension | Use .pdf, .docx, .txt only |
| 413 on upload: "Exceeds 5 MiB" | File too large | Compress or split resume |
| 409 on parse: "Not completed" | Background job still running | Poll `/jobs/{job_id}` until COMPLETED |
| 401 on any ATS endpoint | Session expired/missing | Re-login via `/auth/session` |
| Score not updating after resume change | Not invalidated | Check `resume_data` updated, score cleared |
| Transcript 409: "Sequence must resume at N" | Gap in sequence numbers | Start at 1, increment by 1 |
| Questions empty for language | Translations PENDING | Only en/ml/hi with AVAILABLE status served |

## Detailed Issues

### Resume Upload & Processing

#### "Resume upload failed" (500)
**Logs:** Check `logs/ats_api.log` for `logger.exception("Could not store uploaded resume")`
**Causes:**
- Disk full / permissions on `uploads/`
- `UPLOAD_DIR` not writable
- Candidate deleted between upload and background task start

**Fix:** Verify `uploads/` directory exists and is writable. Check candidate exists before background task.

#### "Resume processing failed due to an internal error" (job FAILED)
**Logs:** `logger.exception("Resume processing failed: %s", job_id)`
**Causes:**
- `pymupdf` / `python-docx` exception on corrupt file
- `extract_resume_data()` exception
- Candidate deleted during processing

**Fix:** 
- Test file with `python -c "import fitz; fitz.open('file.pdf')"`
- Check `processing_jobs.error` column for details
- Ensure candidate exists throughout processing

#### "Extracted resume text is no longer available" (410)
**Cause:** Job COMPLETED but `result.parsed_text` is empty/null
**Fix:** Check `processing_jobs.result` JSON. Background task may have failed silently.

#### Upload stuck in QUEUED/PROCESSING
**Cause:** Server restarted during processing
**Fix:** On startup, `fail_interrupted_processing_jobs()` marks them FAILED. Re-upload.

### ATS Scoring

#### "Day 12 semantic scoring is unavailable" (503)
**Cause:** `sentence-transformers` not installed or model not cached
**Fix:**
```bash
pip install sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```
**Verify:** Model downloads to `~/.cache/torch/sentence_transformers/`

#### Score seems wrong / missing skills
**Check evidence:**
```json
POST /candidates/score → evidence {
  "extracted_skills": [...],
  "matching_required_skills": [...],
  "missing_required_skills": [...],
  "components": {
    "skill_match": {"score": ..., "matched": [...], "missing": [...]},
    "semantic_similarity": {"score": ..., "reason": "..."}
  }
}
```

**Common causes:**
- Resume not processed (score uses `candidate.skills` only)
- Skill normalizer doesn't map synonym (check `day9_skill_extraction`)
- Semantic similarity low (resume text filtered for PII)

#### Score not recalculated after changes
**Expected behavior:** These invalidate score automatically:
- Resume upload/replace → `save_candidate_resume()` clears score
- Candidate skills PATCH → `update_candidate()` clears score
- Candidate name PATCH → clears score
- Opening required_skills/preferred_skills/min_years/min_education update → clears all scores for opening

**Debug:** Check `candidate.score` and `candidate.score_evidence` in DB. Should be NULL after invalidation.

#### Ranking incorrect
**Check:** 
- All candidates have scores? `candidate.score IS NOT NULL`
- Scores persisted? `candidate.score_evidence` has `scored_at`
- Sort: `ORDER BY score DESC, name ASC`

### Eligibility Evaluation

#### "Configure eligibility rules before evaluating" (409)
**Cause:** No `eligibility_configurations` record for opening
**Fix:** PUT `/api/v1/openings/{opening_id}/eligibility-config` first

#### Always returns REVIEW
**Check evaluation result:**
```json
{
  "missing_information": ["A current ATS score is unavailable.", "Mandatory skill evidence is not present for: Python"],
  "review_reasons": ["Mandatory-skill evidence requires recruiter review."],
  "rules": {
    "minimum_ats_score": {"status": "REVIEW", "reason": "A current, timestamped ATS result is required."},
    "mandatory_skills": {"status": "REVIEW", "missing": ["Python"]}
  }
}
```

**Causes:**
- No ATS score → run scoring first
- Score not current → `score_evidence.scored_at` missing
- Skills only in `candidate.skills` not `resume_data.skills` → both checked
- Skill normalizer mismatch → check canonical form

#### REJECTED unexpectedly
**Check:** `explicit_failures` in evaluation logic
- `minimum_ats_score` FAIL: score < configured minimum
- `experience` FAIL: `experience_years < minimum_experience_years`
- These are the ONLY explicit failures; everything else → REVIEW

#### Re-evaluation not triggering
**Mechanism:** Fingerprint includes:
- `candidate_id`, `candidate.updated_at`
- `candidate.score`, `candidate.score_evidence`
- `opening_id`, `opening.updated_at`
- `configuration.version`

**Debug:** Compare fingerprint in `eligibility_evaluations.input_fingerprint` vs current computed.

### Screening Questions

#### Questions missing for language
**Cause:** Translation `status: "PENDING"` → excluded
**Fix:** Update `data/screening/hr_screening_questions.json` translations to `"status": "AVAILABLE"`

#### Category filter returns empty
**Cause:** Category case mismatch
**Fix:** Use uppercase with underscores: `INTRODUCTION`, `SKILLS`, `NOTICE_PERIOD`

#### "Unsupported screening role" (422)
**Cause:** Role not in `dataset.roles`
**Fix:** Add role to `hr_screening_questions.json` roles registry

### Transcript & Sessions

#### "Cannot change CREATED session to COMPLETED" (409)
**Valid transitions:**
- CREATED → IN_PROGRESS, CANCELLED
- IN_PROGRESS → INTERRUPTED, COMPLETED, CANCELLED
- INTERRUPTED → IN_PROGRESS, COMPLETED, CANCELLED

**Fix:** Follow state machine: CREATED → IN_PROGRESS → COMPLETED

#### "Transcript sequence must resume at N" (409)
**Cause:** Gap or duplicate sequence_number
**Fix:** 
- First segment: `sequence_number: 1`
- Subsequent: `sequence_number: previous + 1`
- Batch segments in order

#### "Unknown screening question ID" (422)
**Cause:** `question_id` not in `dataset.questions`
**Fix:** Use valid IDs from `GET /screening/questions`

#### "Start or resume session before adding segments" (409)
**Cause:** Session status not IN_PROGRESS or INTERRUPTED
**Fix:** PATCH session to IN_PROGRESS first

#### Timestamp validation fails (422)
**Cause:** Naive datetime (no timezone)
**Fix:** Include timezone: `"2026-01-01T10:00:00+00:00"` or `"2026-01-01T10:00:00Z"`

#### Confidence validation fails (422)
**Cause:** Value outside [0, 1]
**Fix:** Ensure `0.0 <= confidence <= 1.0` or omit (null)

### Authentication

#### "Recruiter authentication is not configured" (503)
**Cause:** No `recruiter_accounts` in database
**Fix:** Run `python -m src.create_recruiter <username> <password>`

#### "Too many sign-in attempts" (429)
**Cause:** 5 failed attempts in 15 minutes
**Fix:** Wait 15 minutes, or clear `recruiter_login_attempts` table

#### Session not persisting
**Cause:** Cookie not sent/accepted
**Checks:**
- Cookie name: `zecpath_session`
- Path: `/api/v1`
- Secure: only on HTTPS
- SameSite: Strict (blocks cross-site)
- HttpOnly: true (no JS access)

**Fix:** For local dev, use `http://localhost` (not `127.0.0.1`), ensure cookie sent with `credentials: include`

### Database

#### "Database is locked" (sqlite3.OperationalError)
**Cause:** Concurrent connections, long transaction
**Fix:**
- Use single worker (`--workers 1`)
- Connection timeout: 10s (configured)
- Check for unclosed connections in code

#### Migration not applied
**Cause:** Additive migrations run on connection in `database.py::_connection()`
**Fix:** Restart application to trigger migration

#### Unique constraint: "Candidate with email already applied"
**Cause:** `(opening_id, email)` unique index
**Fix:** Use different email, or update existing candidate

### Performance

#### Slow scoring (>10s)
**Likely:** First semantic model load (cold start)
**Fix:** Pre-load model on startup or accept first-request latency

#### High memory usage
**Check:** Large resume files, embedding arrays
**Fix:** 
- Enforce 5 MiB upload limit
- Monitor `memory_profiler` output
- Consider streaming extraction for large PDFs

## Log Locations

| Log | Location |
|-----|----------|
| Application | `logs/ats_api.log` (configured in `logging_config.py`) |
| Uvicorn | Console (stdout/stderr) |
| SQLite errors | Application log |

## Debug Commands

```bash
# Check database integrity
sqlite3 data/zecpath.sqlite3 "PRAGMA integrity_check;"

# View recent processing jobs
sqlite3 data/zecpath.sqlite3 "SELECT job_id, status, error, created_at FROM processing_jobs ORDER BY created_at DESC LIMIT 10;"

# View candidates with scores
sqlite3 data/zecpath.sqlite3 "SELECT candidate_id, name, score, scored_at FROM candidates WHERE score IS NOT NULL;"

# View eligibility evaluations
sqlite3 data/zecpath.sqlite3 "SELECT evaluation_id, candidate_id, status, evaluated_at FROM eligibility_evaluations ORDER BY evaluated_at DESC LIMIT 10;"

# Validate screening dataset
python -m src.validate_screening_dataset
```

## Escalation

If issue persists:
1. Check `docs/day16_day23_known_limitations.md` — may be documented limitation
2. Search existing tests for similar scenario
3. Create minimal reproduction case
4. File issue with: endpoint, request, response, logs, environment