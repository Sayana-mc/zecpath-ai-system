# Days 16–23 implementation audit

## Scope and evidence

This audit covers the root recruiter app (`src.main:app`), its authenticated
routes in `src/api.py`, contracts in `src/schemas.py`, SQLite persistence in
`src/database.py`, the same-origin dashboard, and focused tests. Numbered
`day*` modules are not considered integrated unless exercised through the
root application. All candidate and resume content used for new tests is
synthetic.

The previous Day 1–15 phase was explicitly partial. Its audit, implementation
report, test report, and known-limitations report remain the authority for
earlier work and unresolved gaps. The earlier 487-test result predates this
phase and is not evidence for the changes below.

## Day-by-day status

| Day | Status | Root-app evidence | Important boundary |
|---|---|---|---|
| 16 — ATS API integration | PARTIAL | Existing authenticated resume upload/extraction, scoring, persisted shortlist routes; added explicit-heading JD parse route. | Root uses its existing API and Day 9–13 scorer; the standalone Day 16 demo and its in-memory data are not mounted. |
| 17 — ATS evaluation | BLOCKED / tooling only | Added binary metrics helper and an empty human-review CSV template. | No recruiter-reviewed reference labels exist; accuracy, precision, recall, and fairness performance are not measured. |
| 18 — performance | NOT COMPLETE | No optimization or performance claim is made. | A controlled baseline and repeated benchmark have not been established for the current root workflow. |
| 19 — documentation | PARTIAL | API, schema, integration, audit, test, and limitation documents describe observed root behavior. | Documentation does not establish operational readiness; older standalone docs may describe prototypes. |
| 20 — scoring | PARTIAL | The root score route persists Day 9–13 evidence, score timestamp, and `day9-12-13-v1` version. | No separate Day 20 scorer exists in the repository; the heuristic is not validated for employment decisions. |
| 21 — eligibility | PARTIAL | Protected configuration/evaluation/retrieval routes and persistence; missing/uncertain evidence is review-required. | No tenant model exists. Results are decision support, never an automatic hiring action. |
| 22 — screening dataset | PARTIAL | Root JSON question bank, filtering API, translations/status metadata, and dataset validator. | Dataset has 17 questions across two populated roles; translations are available only for HR001 and HR006 in English, Malayalam, and Hindi. |
| 23 — transcript architecture | PARTIAL | Protected persisted manual/import transcript sessions, ordered segments, and question interactions. | No audio capture, speech recognition, voice AI, or automated transcript generation is integrated. |

No day is marked complete solely because a stage folder, schema, or
documentation exists.

## Integration boundary

The root application continues to use its existing recruiter authentication,
candidate/opening records, scoring, and dashboard. Schema changes are additive.
Current API routes include:

- `POST /api/v1/openings/parse-description`
- existing `POST /api/v1/resumes/upload`, `GET /api/v1/jobs/{job_id}`,
  `POST /api/v1/resumes/parse`, `POST /api/v1/candidates/score`, and
  `POST /api/v1/openings/{opening_id}/shortlist`
- `GET/PUT /api/v1/openings/{opening_id}/eligibility-config`
- `POST /api/v1/candidates/{candidate_id}/eligibility/evaluate` and
  `GET /api/v1/candidates/{candidate_id}/eligibility`
- `GET /api/v1/screening/questions`
- `POST /api/v1/screening/sessions`, session GET/PATCH, and nested transcript
  segment and interaction routes.

SQLite adds optional candidate location/work-mode/relocation/availability
fields and tables for eligibility configurations/evaluations, screening
sessions, transcript segments, and screening interactions. Existing account
and application records are preserved by additive startup migrations.

## Verification gates

The focused route tests use the root FastAPI app, log in through the existing
recruiter authentication flow, and use a temporary SQLite database. A
synthetic end-to-end test covers JD parse and confirmation, opening and
candidate creation, TXT upload/extraction, score, shortlist, eligibility,
question retrieval, and transcript persistence/schema validation.

The latest confirmed focused run is recorded in
[the test report](day16_day23_test_report.md). A full repository suite,
browser interaction pass, controlled performance benchmark, labeled-model
evaluation, and subgroup fairness analysis remain separate gates.
