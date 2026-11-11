# Day 61: AI Monitoring & Observability — ZecPath AI Hiring System

## Executive Summary

Day 61 implements a production-ready, privacy-guarded observability, metrics, alerting, and decision audit logging subsystem for the ZecPath AI Hiring System. The implementation is housed centrally in [`src/observability.py`](file:///c:/Users/sayan/Documents/zecpath-ai-system/src/observability.py) and integrated into the FastAPI backend [`src/main.py`](file:///c:/Users/sayan/Documents/zecpath-ai-system/src/main.py) and [`src/api.py`](file:///c:/Users/sayan/Documents/zecpath-ai-system/src/api.py), as well as the recruiter frontend [`static/index.html`](file:///c:/Users/sayan/Documents/zecpath-ai-system/static/index.html).

---

## 1. Centralized Structured Logging (Privacy-Guarded)

All operational and inference logs are serialized into structured JSON Lines (`.jsonl`) files stored under `logs/`:
- `logs/api_logs.jsonl`: Captures HTTP method, endpoint, response status code, execution duration in milliseconds, success flag, and correlation IDs. Sensitive request bodies, passwords, session cookies, and candidate PII are never logged.
- `logs/model_logs.jsonl`: Records AI model invocations (model name, version tag, task name, latency ms, success flag, and internal candidate/job reference IDs). Raw resume text, candidate answers, and personal details are strictly excluded.
- `logs/error_logs.jsonl`: Captures sanitized system error messages and component names with length caps to prevent leaking stack traces or internal secrets.
- `logs/decision_audit.jsonl`: Immutably logs hiring decisions (`SHORTLIST`, `SELECTED`, `REJECTED`, `HOLD_REVIEW`, `OVERRIDDEN`), rationale, authenticated actor, model version, and human review verification.

---

## 2. Operational & AI Quality Metrics Tracking

The in-memory rolling buffer tracks key metrics with percentile calculations:
- **API Performance:** Total request counts, failure counts, failure rate percentage, P50 latency (ms), and P95 latency (ms).
- **Processing Stage Timings:** Average resume parsing duration (ms), average ATS scoring duration (ms), and database error counters.
- **AI Model Performance:** Total model inferences, failure counts, failure rate %, and inference latency percentiles.
- **Decision Auditing:** Total decisions logged, human-reviewed percentage, and decision distribution breakdown.

> **AI Quality vs. Operational Metrics Distinction:**
> The system explicitly distinguishes operational metrics (completion rates, throughput, latency) from AI accuracy metrics. The dashboard and reports explicitly advise that operational completion rates do not measure algorithmic accuracy; accuracy evaluation requires human-verified ground-truth evaluation datasets.

---

## 3. Threshold-Based Alerting Rules

Configurable alerting rules evaluate real-time system health:
- `api_failure_rate`: Triggers `WARNING` at 5% and `CRITICAL` at 15% failure rate (evaluated when sample size exceeds 5 requests).
- `api_p95_latency`: Triggers `WARNING` at 1000ms and `CRITICAL` at 3000ms P95 latency.
- `ai_model_failure_rate`: Triggers `CRITICAL` when model run failure rate reaches 10%.
- `database_error_count`: Triggers `HIGH` alert upon any detected database connectivity or execution errors.

---

## 4. API Endpoints Reference

| Endpoint | Method | Role | Description |
|---|---|---|---|
| `/api/v1/monitoring/dashboard` | `GET` | Recruiter | Returns aggregated operational metrics, model metrics, decision audit summary, and recent errors. |
| `/api/v1/monitoring/alerts` | `GET` | Recruiter | Returns active alert violations based on current metrics. |
| `/api/v1/monitoring/decision-audit` | `GET` | Recruiter | Returns recent decision audit logs with pagination support. |
| `/api/v1/monitoring/log-event` | `POST` | Recruiter | Allows logging custom observability events for audit tracking. |

---

## 5. Recruiter Dashboard UI Integration

The recruiter dashboard (`static/index.html`) includes a live "System Observability & AI Monitoring" panel presenting real-time KPI cards:
- **API Requests & Failure Rate %**
- **P95 Latency & P50 Latency (ms)**
- **AI Model Inferences & Failure Count**
- **Decision Audit Count & Human Review %**
- **Active Alert Banner** highlighting any system health warnings.

