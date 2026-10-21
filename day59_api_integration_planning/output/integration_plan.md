# Day 59 — AI Integration Plan

Project: Zecpath AI Hiring System

| Service | Method | Endpoint | Mode | Success |
|---|---|---|---|---|
| Resume Parsing API | POST | `/v1/resume-jobs` | async | 202 |
| ATS Scoring API | POST | `/v1/ats/score` | sync | 200 |
| Screening AI API | POST | `/v1/screening/evaluate` | sync | 200 |
| Interview AI API | POST | `/v1/interviews/score` | sync | 200 |
| Decision AI API | POST | `/v1/decisions/recommend` | sync | 200 |

## Safeguards
- Human review required: Yes
- Automatic rejection: Disabled

## Retry policy
```json
{
  "max_attempts": 3,
  "initial_backoff_seconds": 1,
  "max_backoff_seconds": 8,
  "jitter": true
}
```

Planning prototype only; no live AI API or production database is connected.
