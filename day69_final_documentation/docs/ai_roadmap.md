# ZecPath AI Hiring System — AI & Engineering Roadmap

## 1. Implemented Features (Verified)
- Async resume upload (`TXT`, `DOCX`, `PDF` <= 5 MiB) and section/skill/experience/education extraction.
- 4-factor ATS scoring (`0.40*Skills + 0.25*Semantic + 0.20*Experience + 0.15*Education`) with snippet evidence.
- Mandatory eligibility evaluation (`ELIGIBLE`, `REVIEW_REQUIRED`, `REJECTED`).
- API-driven Screening, HR Interview, Technical Interview, and AST-based Machine Test engines.
- Cross-round aggregation with role weights and `exclude_and_renormalize` policy.
- Explainable final recommendations with mandatory human review (`APPROVE`/`OVERRIDE`/`REJECT`).
- 14-section Hiring Intelligence Reports (JSON, HTML, Markdown, PDF 1.4).
- PBKDF2-SHA256 auth, 4 RBAC roles, SHA-256 hash-chained `audit_events`, and live observability metrics.

## 2. Partially Implemented Features
- **Candidate-Facing Portal:** Assessment stages work via `/api/v1/*` APIs, while `static/index.html` covers recruiter workflows only.
- **Machine-Test Sandbox:** Uses Python AST/static analysis rather than isolated OS/container execution.
- **Speech-to-Text:** Audio upload and transcript cleaning work locally; GPU Whisper inference depends on external model weights.

## 3. Planned Enhancements & Production Requirements
- **Short-Term:** Candidate-facing interactive screening/interview UI; background worker queue for batch resumes.
- **Medium-Term (Production):** PostgreSQL connection pooling, Redis cache/queue, micro-VM code execution sandbox (Firecracker/Docker), external SSO/MFA, TLS termination.
- **Research Opportunities:** Real-world calibration & bias auditing on historical hiring outcomes (replacing the 12-case synthetic benchmark), calibrated confidence intervals, and multilingual semantic embeddings.
