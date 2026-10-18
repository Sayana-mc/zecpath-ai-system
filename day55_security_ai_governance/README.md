# Day 55 — Security & AI Governance

## Objective
Build a local reference implementation for audit logs, RBAC, consent checks, encrypted storage, retention rules, and governance documentation.

## Requirements
- Python 3.10+
- `cryptography`

## Setup (PowerShell)
Run from the repository root:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\day55_security_ai_governance\requirements.txt
```

## Run
```powershell
python -m day55_security_ai_governance.src.main
```

## Tests
```powershell
python -m unittest discover -s .\day55_security_ai_governance\tests -v
```

## Outputs
- `output/governance_report.json`
- `output/governance_report.md`
- `output/audit_verification.json`

## Important security note
The local demo creates a process-local encryption key if `ZECpath_STORAGE_KEY` is missing. That key is not persistent across separate runs. For a repeatable local demo, generate a key once and set it in the current PowerShell session before running the app. Never commit the key or place it in screenshots.

Example:
```powershell
$key = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
$env:ZECpath_STORAGE_KEY = $key
python -m day55_security_ai_governance.src.main
```

For subsequent sessions, retrieve the key from a secure secret manager; do not store it in source code. A new key cannot decrypt data encrypted with a previous key.

## Scope and limitations
- Synthetic candidate data only.
- RBAC is not authentication.
- Hash chaining is tamper-evident, not tamper-proof.
- Retention settings are proposed defaults requiring legal/privacy review.
- Human review remains required; automatic rejection is disabled.
