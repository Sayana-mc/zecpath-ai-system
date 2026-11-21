# ZecPath Technical Handbook

1. **Architecture:** FastAPI (`src/main.py`) serves `static/index.html` at `/`, Swagger UI at `/docs`, and 125 `/api/v1/*` routes from `src/api.py`.
2. **Authentication & RBAC:** `src/auth.py` uses PBKDF2-SHA256 password hashes, HTTP-only session cookies (8h expiry), HTTP Basic auth for API clients, login attempt throttling, and 4 RBAC roles with tenant isolation (`src/security_governance.py`).
3. **Observability:** `ObservabilityASGIMiddleware` (`src/observability.py`) records request latency (P50/P95), error rates, alerts, and JSONL logs under `logs/`.
4. **Pipeline:** Resume Upload (`202` async job) -> Parsing -> 4-Factor ATS -> Eligibility -> Screening -> HR Interview -> Technical Interview -> Machine Test -> Cross-Round Aggregation -> Final Recommendation -> Human Review -> 14-Section Hiring Intelligence Report (JSON, HTML, Markdown, PDF 1.4).
