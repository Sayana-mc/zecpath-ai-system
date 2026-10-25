# Day 61 — AI Monitoring & Observability

## Objective
Design and demonstrate structured logging, monitoring metrics, alert rules, dashboard summaries, and decision audit trails for an AI hiring system.

## Run (Python 3.10+, standard library only)
From the repository root:
```powershell
python --version
python -m day61_ai_monitoring_observability.src.main
python -m unittest discover -s .\day61_ai_monitoring_observability\tests -v
```

The local demo writes API/model/error JSONL logs, decision audit events, dashboard_summary.json, and alerts.json under `output/`.

## Scope and limitations
This is a synthetic local prototype, not connected to live services, a real model, a monitoring server, or a production alert channel. Accuracy cannot be inferred from HTTP success or model confidence; it must be measured against reviewed ground-truth labels. Do not log raw resumes, interview transcripts, secrets, or unnecessary personal data.

## Deliverables
- `docs/ai_observability_plan.md`
- `docs/logging_structure.md`
- `docs/monitoring_dashboard_design.md`
- `docs/alert_rules.md`
- Working sample code and unit tests.
