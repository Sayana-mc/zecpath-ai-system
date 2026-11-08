# Day 19 — root technical documentation

Current root behavior is documented across the
[API reference](api_documentation.md), [SQLite schema](database_schema.md),
[Day 16–23 audit](day16_day23_implementation_audit.md),
[implementation report](day16_day23_implementation_report.md), and
[limitations](day16_day23_known_limitations.md). Runtime code and tests, not
historical stage documents, determine the integration status.

The root service is `src.main:app`; `src.api` contains protected routes,
`src.schemas` defines request/response contracts, `src.database` persists
records, and `static/index.html` is the same-origin dashboard. Refer to the
source and focused tests for the exact contract; no separate Day 19 service
has been added.
