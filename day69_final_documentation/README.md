# ZecPath AI Hiring System — Final Submission Documentation (Day 69)

## Overview
ZecPath is a local-first, FastAPI + SQLite + Vanilla JS AI-assisted recruitment decision-support system built across 70 structured engineering milestones.

## Implemented Capabilities
- **Recruiter Workspace (`static/index.html`):** Login/logout, job openings, candidate registration, async resume upload (`TXT`, `DOCX`, `PDF`), ATS scoring, cross-round aggregation, final recommendations, Hiring Intelligence Reports, synthetic threshold optimization, governance/RBAC/audit verification, and live observability.
- **REST API (`src/api.py`, `src/main.py`):** 125 `/api/v1/*` endpoints with OpenAPI/Swagger at `/docs`.
- **Persistence (`src/database.py`):** SQLite (`data/zecpath.sqlite3`, overridable via `ZECPATH_DB_PATH`) with SHA-256 hash-chained `audit_events`.
- **Demo Dataset (`demo_data/`):** 4 job openings, 8 synthetic candidate profiles, 8 resumes, and screening/interview responses (`python -m src.init_demo_data`).

## Quick Start
```powershell
pip install -r requirements.txt
python -m src.create_recruiter
python -m src.init_demo_data
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

## Documentation Index
- [Technical Handbook](docs/technical_handbook.md)
- [System Architecture](docs/system_architecture.md)
- [API Documentation](docs/api_documentation.md)
- [Data Models](docs/data_models.md)
- [Scoring Logic](docs/scoring_logic.md)
- [Module Reference](docs/module_reference.md)
- [Setup Guide](docs/setup_guide.md)
- [Deployment Guide](docs/deployment_guide.md)
- [AI Roadmap](docs/ai_roadmap.md)
- [Final Project Summary](docs/final_project_summary.md)
- [Portfolio Summary](portfolio/portfolio_summary.md)

## Security & Limitations
- Never commit `.env` secrets or recruiter credentials.
- Human review is mandatory (`APPROVE` / `OVERRIDE` / `REJECT`); automated rejection is disabled.
- Prototype limitations: SQLite single-node persistence, AST-only machine test checks (no OS container sandbox), synthetic-only validation benchmark.
