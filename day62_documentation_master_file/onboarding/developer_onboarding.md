# Developer Onboarding Guide

## First-day checklist
1. Get repository access and read the README.
2. Check active branch and clean working tree.
3. Inspect runtime versions and dependency manifests.
4. Read architecture, APIs, scoring, and data-model documentation.
5. Learn test and local-run commands from the repository.
6. Confirm which components are implemented versus planned.
7. Review security and candidate-data handling rules.

## Core concepts
- Resume parsing extracts structured fields from supported documents.
- AI inference runs configured model tasks.
- Screening compares evidence with role criteria.
- Validation checks model output and required fields.
- Decision service records recommendation/workflow state.
- Human review supports consequential decisions.
- Observability tracks operational behaviour.
- Audit trail records provenance and review activity.

## Explore the repository
```powershell
Set-Location "$HOME\Documents\zecpath-ai-system"
Get-ChildItem
Get-ChildItem -Recurse -File -Include README.md,requirements.txt,pyproject.toml,package.json
git status
git branch --show-current
```

## Safe change workflow
Create focused branch → read implementation/tests → make a small change → add tests → run checks → review `git diff` → update docs → commit and request review.

## AI-specific expectations
Validate structured output; record model/config versions; evaluate on reviewed labels; preserve evidence references; do not treat confidence as accuracy; do not bypass required human review or auto-reject based solely on an unverified score.

## Data security
Use synthetic/approved anonymized data; never commit `.env`, API keys, candidate resumes, recordings, or production logs. Use opaque references in telemetry and least-privilege access.

## Pull-request checklist
Tests pass, no unrelated changes, schemas/docs match implementation, errors handled, logs redacted, no sensitive data in screenshots, and test instructions included.
