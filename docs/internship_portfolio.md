# Internship portfolio: Zecpath AI Hiring System

## Project summary

Zecpath is a repository of staged ATS and hiring-workflow learning modules,
plus a small runnable local recruiter application. The root app demonstrates
how candidate/job records, resume extraction, deterministic skill matching,
review suggestions, and screening notes can be connected. The broader
interview, transcript, fairness, and recommendation modules remain separate
prototypes unless explicitly identified as integrated.

This portfolio describes repository evidence. It does not infer an internship
employer, supervisor, dates, stakeholder approval, or real-world hiring impact.

## Objectives

- Build a local recruiter workflow around jobs and candidate applications.
- Parse supported resume files without inventing absent information.
- Present transparent exact-skill evidence for human review.
- Preserve application and processing data in SQLite.
- Explore additional ATS, screening, interview, fairness, governance, and
  observability approaches in isolated stage modules.
- Keep claims honest by distinguishing runnable functionality from plans and
  synthetic simulations.

## Architecture

The root application is FastAPI (`src.main:app`) serving an inline HTML/CSS/JS
dashboard from `static/index.html`. API routes in `src/api.py` validate
requests with Pydantic schemas, invoke parsing/scoring services, and persist
records through `src/database.py` in SQLite. Resume parsing supports TXT,
DOCX, and text-based PDF; a background task records processing state. Exact
required-skill matching returns matched/missing skills and source snippets.
The dashboard shortlist is advisory and does not change candidate status.

See the [verified architecture](architecture/ATS_Architecture.md) and [Day 68
integration matrix](../day68_release_readiness/day68_integration_report.md).

## Modules and technologies

**Root application:** Python 3.12, FastAPI, Pydantic, Uvicorn, SQLite,
python-docx, pypdf, python-multipart, HTML, CSS, JavaScript, pytest, and HTTPX.

**Historical stage themes:** extraction/parsing and ATS scoring; eligibility
and screening; transcript and speech-to-text; HR/technical interviews;
behavioral and integrity research; aggregation/recommendation; governance;
performance and observability; synthetic data and internal review.

**AI status:** The root app does not use a remote LLM. Its skills score and
screening interpretation use deterministic matching/regex rules. Day 24 has a
separate Faster-Whisper wrapper, but root API integration and real audio
validation were not performed.

## Development progress and evidence

- The repository contains numbered stages spanning Days 3–65, plus Day 68
  release-readiness reports.
- The root recruiter API supports jobs, candidates, resume extraction, scoring,
  saved-score shortlist suggestions, screening notes, and session
  authentication.
- A first recruiter can be initialized with salted PBKDF2-HMAC password
  storage; browser sessions are persisted in SQLite and expire after eight
  hours.
- The final recorded full pytest run passed **476 tests**. A real synthetic
  browser workflow verified login, job/candidate creation, resume extraction,
  scoring/evidence, shortlist, screening notes, status persistence, reload,
  backend restart recovery, logout, and unauthenticated denial.
- Day 60 and Day 64 performance/evaluation outputs are synthetic local
  demonstrations, not production benchmarks or external assessments.

Detailed evidence: [test report](../day68_release_readiness/day68_test_report.md),
[final validation](../day68_release_readiness/day68_final_validation.md), and
[daily report index](daily_reports.md).

## Challenges and limitations

- Historical folders have their own implementations and repeated package
  names; their existence does not guarantee integration.
- Exact keyword overlap is transparent but incomplete and is not semantic
  understanding or a validated hiring model.
- The root screening note does not integrate the transcript, Day 26 score, or
  Day 28 full report.
- SQLite and resume text are unencrypted; candidate listing is unpaginated;
  there are no production migrations, automated backup/recovery, multi-tenant
  isolation, RBAC, or formal retention workflows.
- Scanned-PDF OCR, external LLM integration, voice calls, production
  deployment, dependency scanning, load testing, and independent fairness
  evaluation are not evidenced.
- Scores must never be the sole basis for a consequential employment action.

## Outcomes and future scope

The demonstrated outcome is a functional local synthetic-data recruiter
prototype with tested persistence and an auditable deterministic match
explanation. The next steps are the [AI roadmap](ai_roadmap.md): data
contracts/provenance, recruiter correction workflow, verified API integration,
privacy/security controls, representative validation, and only then
provider-backed AI if approved and tested.

## Demo commands

```powershell
.\.venv\Scripts\python.exe -m src.create_recruiter
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
.\.venv\Scripts\python.exe -m pytest -q
```

Use fictional data and consult the [root README](../README.md) for the full
setup, environment, API, and security instructions.
