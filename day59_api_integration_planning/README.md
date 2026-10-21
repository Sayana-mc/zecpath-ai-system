# Day 59 — API & Integration Planning
Python 3.10+, standard library only. This is a planning prototype, not a live API server.

Run from the parent folder `zecpath-ai-system`:
```powershell
python -m day59_api_integration_planning.src.main
python -m unittest discover -s .\day59_api_integration_planning\tests -v
```
Resume parsing is asynchronous (202 + job ID); real-time interview scoring is synchronous with a strict timeout. Human review is mandatory and automatic rejection is disabled.
