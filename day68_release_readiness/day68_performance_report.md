# Day 68 Performance Report

## Measurements performed

| Measurement | Result | Interpretation |
|---|---|---|
| Baseline full repository pytest suite | 473 passed in 70.15 s. | Includes many stage-specific tests; not an API throughput benchmark. |
| Final full repository pytest suite | 476 passed in 26.17 s. | Runtime depends on machine/cache and includes all historical tests. It is not comparable as a controlled performance experiment. |
| Root API test suite | 25 passed in 12.90 s. | Includes database-backed API and password-hashing regression tests. Not an HTTP latency SLA. |
| Browser scenario | Job, candidate, extraction, scoring, shortlist, and screening workflow completed; no latency percentiles were collected. | Functional validation only. |

## Observed performance constraints

- Candidate list reads are unpaginated and return full resume text, so response
  size and browser rendering scale with the complete matching dataset.
- Resume extraction is run as a synchronous task on the FastAPI background
  task mechanism. It is not an independent durable worker and can compete with
  API workers for CPU.
- Each database connection creates/checks schema objects and uses SQLite;
  no production database concurrency behavior was measured.
- Login throttling and sessions use the same SQLite database.
- Uploads are capped at 5 MiB. No large-file, concurrent-upload, or DOCX
  decompression stress test was run.

## Conclusion

No application performance optimization is claimed. The only measured values
are test-suite wall times. Before staging/production, benchmark realistic
candidate counts, response size, resume parsing time, concurrent uploads,
database contention, and p50/p95/p99 API latency on the intended deployment
hardware. Add pagination and a durable worker only when measurements and
deployment requirements justify them.
