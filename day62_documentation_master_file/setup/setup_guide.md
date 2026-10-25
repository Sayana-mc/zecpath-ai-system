# Local Setup Guide

## Prerequisites
- Windows PowerShell.
- Git if cloning.
- Python 3.10+ for Day 60/61 prototype utilities.
- Dependencies specified by the current repository manifest.

## Navigate and inspect
```powershell
Set-Location "$HOME\Documents\zecpath-ai-system"
git status
git branch --show-current
python --version
Get-ChildItem
Get-ChildItem -Recurse -File -Include requirements.txt,pyproject.toml,package.json,README.md
```

## Optional Python virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```
Install dependencies only from the actual `requirements.txt` or `pyproject.toml`; do not guess package names.

## Secrets
Use the project's documented environment-variable names. Keep `.env` out of version control. Never place API keys, candidate files, or production logs in documentation.

## Run Day 61 demo if extracted
```powershell
python -m day61_ai_monitoring_observability.src.main
python -m unittest discover -s .\day61_ai_monitoring_observability\tests -v
```

Use the actual repository README and manifests to start the main application; its exact run commands are not asserted here.

## Before commit
Run tests, inspect `git diff`, ensure secrets and candidate data are not staged, and update docs for any changed route/schema/score.
