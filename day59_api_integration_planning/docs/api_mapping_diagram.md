# API Mapping Diagram

```text
Candidate / Recruiter UI
          |
          v
Backend API Gateway
(Auth, permissions, validation, rate limits, correlation ID)
          |
          +-- POST /v1/resume-jobs [ASYNC / HTTP 202]
          |             |
          |             v
          |        Queue / Worker -> Resume Parsing AI
          |                              |
          |                        Validate extraction
          |                              v
          |                         Application DB
          |
          +-- POST /v1/ats/score ------> ATS Scoring AI
          |                              |
          |                              v
          |                         Application DB
          |
          +-- POST /v1/screening/evaluate -> Screening AI
          |                                  |
          |                                  v
          |                             Application DB
          |
          +-- POST /v1/interviews/score [SYNC + timeout]
          |                              |
          |                              v
          |                         Application DB
          |
          +-- POST /v1/decisions/recommend -> Decision AI
                                             |
                                             v
                                      Human reviewer + DB
```

Database writes: request/job metadata, status, validated profile, score/evidence, rubric/model version, recommendation, audit events. Avoid unnecessary raw media copies and never store secrets in ordinary application records.
