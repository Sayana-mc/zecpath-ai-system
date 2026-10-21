# Request/Response Schema Definitions

## 1. Resume Parsing — `POST /v1/resume-jobs` (async)
Request:
```json
{"candidate_id":"CAND-001","document_uri":"https://private-storage.example/resumes/CAND-001.pdf","document_type":"pdf","idempotency_key":"resume-CAND-001-v1","consent_reference":"CONSENT-REF-001"}
```
Response HTTP 202:
```json
{"request_id":"req-1001","job_id":"job-2001","status":"queued","status_url":"https://api.example.test/v1/resume-jobs/job-2001"}
```
Status endpoint: `GET /v1/resume-jobs/{job_id}`; states queued, processing, completed, failed.

## 2. ATS Scoring — `POST /v1/ats/score`
Request:
```json
{"candidate_id":"CAND-001","job_id":"JOB-101","resume_profile":{"skills":["Python","SQL","Excel"]},"required_skills":["Python","SQL","Power BI"],"rubric_version":"ats-rubric-v1"}
```
Response:
```json
{"request_id":"req-1002","candidate_id":"CAND-001","job_id":"JOB-101","score":75,"matched_skills":["Python","SQL"],"missing_skills":["Power BI"],"model_version":"ats-model-v1"}
```
Scores are examples only; production scoring must have a documented and validated rubric.

## 3. Screening AI — `POST /v1/screening/evaluate`
Request:
```json
{"candidate_id":"CAND-001","job_id":"JOB-101","resume_profile":{"skills":["Python","SQL"],"experience_years":0},"screening_rubric_version":"screening-rubric-v1"}
```
Response:
```json
{"request_id":"req-1003","candidate_id":"CAND-001","job_id":"JOB-101","status":"needs_review","evidence":[{"criterion":"Required skills","observation":"Python and SQL are listed"}],"review_required":true}
```

## 4. Interview AI — `POST /v1/interviews/score` (sync)
Request:
```json
{"candidate_id":"CAND-001","interview_id":"INT-101","question_id":"Q-03","transcript_text":"I would use SQL joins to combine customer and order tables.","rubric_version":"interview-rubric-v1"}
```
Response:
```json
{"request_id":"req-1004","candidate_id":"CAND-001","interview_id":"INT-101","question_id":"Q-03","score":80,"evidence":["Explains joining related tables"],"review_required":true}
```
Example timeout: 8 seconds. Timeout must produce a controlled error, never an invented score.

## 5. Decision AI — `POST /v1/decisions/recommend`
Request:
```json
{"candidate_id":"CAND-001","job_id":"JOB-101","stage_results":[{"stage":"ats","status":"complete","score":75},{"stage":"screening","status":"needs_review","score":null},{"stage":"interview","status":"complete","score":80}],"policy_version":"decision-policy-v1"}
```
Response:
```json
{"request_id":"req-1005","candidate_id":"CAND-001","job_id":"JOB-101","recommendation":"hold_for_review","human_review_required":true,"automatic_rejection":false,"reason_codes":["SCREENING_REQUIRES_REVIEW"]}
```

## JSON Schema files
The `schemas` directory contains versioned JSON Schema files for core request and response objects. Keep schemas synchronized with actual backend implementation and validate both incoming requests and AI responses.
