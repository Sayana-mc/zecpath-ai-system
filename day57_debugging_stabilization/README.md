# Day 57 — Debugging & Stabilization

## Purpose
This module refines the Day 56 synthetic hiring-pipeline simulation. It adds strict input/configuration validation, safer keyword matching, candidate-scoped error reporting, stable report fields, atomic JSON output, and edge-case tests.

**Important:** This is a local simulation. It does not establish production readiness and does not call external AI APIs or databases. All candidate data is synthetic.

## Requirements
- Python 3.10+
- No third-party packages required

## Run from project root
```powershell
python -m day57_debugging_stabilization.src.main
python -m unittest discover -s .\day57_debugging_stabilization\tests -v
```

## Outputs
- `output/debugging_report.json`
- `output/debugging_report.md`
- `output/system_stability_summary.json`
- `output/improvement_recommendations.md`

## Safety guarantees in this simulation
- Human review remains required.
- Automatic rejection is disabled and configuration validation enforces it.
- Missing/invalid scores are errors, not silently converted to zero.
- Candidate IDs must be unique.
- Resume filenames cannot contain directory traversal paths.
- Advisory outcomes never directly trigger a hiring action.

## Screenshot evidence
Save real screenshots from your own run in `screenshots/`. Do not fabricate evidence.
