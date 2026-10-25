# Alert Rules and Response Guide

| Rule | Threshold | Severity | Initial response |
|---|---|---|---|
| API p95 latency | >= 1000 ms | Warning | Inspect route, DB, queue, and provider latency |
| API p95 latency | >= 3000 ms | Critical | Notify owner; inspect traces and recent releases |
| API failure rate | >= 5%, minimum 10 requests | Warning | Group failures by route and status |
| API failure rate | >= 10%, minimum 10 requests | Critical | Notify owner; consider rollback if release-related |
| Model timeout spike | Baseline-based | Warning/Critical | Check provider, quota, timeout and retries |
| Queue backlog | Baseline-based | Warning/Critical | Inspect worker capacity and job age |
| Reviewed-set accuracy below target | Approved threshold | Warning/Critical | Pause promotion and investigate labels/drift |
| Audit record missing fields | Sustained or critical gaps | Critical | Preserve evidence and repair audit path |

The demo implements only API failure-rate and p95-latency rules. Production needs alert deduplication, cooldowns, ownership, delivery testing, and runbooks.
