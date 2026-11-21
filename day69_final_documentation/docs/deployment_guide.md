# ZecPath Deployment Guide (Current Prototype vs. Production Target)

## Current Local Deployment
- **Server:** Single-process Uvicorn (`python -m uvicorn src.main:app --host 127.0.0.1 --port 8000`).
- **Database:** Local SQLite file (`data/zecpath.sqlite3`, overridable via `ZECPATH_DB_PATH`).
- **Static UI:** Served directly by FastAPI from `static/index.html`.
- **Logs & Uploads:** Stored locally in `logs/` and `uploads/`.

## Production Deployment Requirements (Not Yet Implemented)
1. Replace SQLite with PostgreSQL + connection pooling + automated backups.
2. Put FastAPI behind a reverse proxy (Nginx/Envoy) with HTTPS/TLS and secure cookie flags.
3. Isolate machine-test code execution inside ephemeral containers/micro-VMs (never run untrusted code on host).
4. Move async `processing_jobs` to a persistent distributed worker queue (Redis + Celery/RQ).
5. Integrate external secret management, SSO/MFA, and centralized log aggregation.
