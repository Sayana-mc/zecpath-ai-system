# Day 64 - Synthetic End-to-End Walkthrough

- Candidate: `CAND-001` (synthetic demo)
- Session: `DAY64-DEMO-001`
- Generated: 2026-10-28T14:26:14.835153+00:00
- Mode: `SYNTHETIC_LOCAL_INTEGRATION`

## Stage results

| Stage | Score / status | Latency (ms) |
|---|---:|---:|
| ATS | 44.86 | 5.175 |
| Screening | 91.75 | 4.053 |
| HR interview | 85.0 | 0.087 |
| Technical interview | 73.67 | 2.002 |
| Machine test | 80.25 | 1.153 |
| Aggregation | 76.31 (COMPLETE) | 0.157 |
| Decision | HOLD_REVIEW (advisory) | 0.116 |

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

- Total local runtime: 16.804 ms
- Single local synthetic run; not a load test and excludes network, storage, external models, and production services.
