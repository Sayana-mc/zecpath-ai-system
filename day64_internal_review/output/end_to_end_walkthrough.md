# Day 64 - Synthetic End-to-End Walkthrough

- Candidate: `CAND-001` (synthetic demo)
- Session: `DAY64-DEMO-001`
- Generated: 2026-10-28T14:15:17.525924+00:00
- Mode: `SYNTHETIC_LOCAL_INTEGRATION`

## Stage results

| Stage | Score / status | Latency (ms) |
|---|---:|---:|
| ATS | 44.86 | 2.198 |
| Screening | 91.75 | 42.132 |
| HR interview | 85.0 | 0.046 |
| Technical interview | 73.67 | 35.004 |
| Machine test | 80.25 | 16.504 |
| Aggregation | 76.31 (COMPLETE) | 0.127 |
| Decision | HOLD_REVIEW (advisory) | 0.067 |

## Review safeguards

- Human review required: **True**
- Human disposition: **PENDING**
- Automatic employment action: **False**

## Limitations

- All inputs in this walkthrough are synthetic demonstration data.
- ATS semantic_similarity is a lexical-overlap proxy, not an embedding model.
- Screening scores use heuristic rules and are not validated measures.
- HR parameter scores and technical rubric scores are supplied demo ratings, not reviewer feedback.
- Machine-test execution results and rubric metrics are supplied; submitted code is not executed by the prototype.
- No external ATS, voice, database, authentication, or deployed service is integrated.
- The recommendation is advisory only; no human disposition or employment action is made.

## Performance scope

- Total local runtime: 142.081 ms
- Single local synthetic run; not a load test and excludes network, storage, external models, and production services.
