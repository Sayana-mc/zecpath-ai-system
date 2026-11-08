# Day 16 — root API integration

The root recruiter API remains the only application surface. Existing
authenticated job and candidate routes, resume extraction, score calculation,
and persisted shortlist suggestions are retained. The standalone Day 16 demo
is not mounted and its in-memory records are not reused.

The root adds `POST /api/v1/openings/parse-description`, a conservative
explicit-heading parser that returns evidence and warnings. It does not write
to an opening; a recruiter must confirm values in the dashboard. Resume upload,
processing status, parse, score, and persisted shortlist remain the existing
root endpoints.

The full route contracts and limits are in [API documentation](api_documentation.md).
Root integration is covered by the synthetic flow in
[the phase test report](day16_day23_test_report.md). Upload work still runs as
FastAPI background tasks; it is not a durable distributed job queue.
