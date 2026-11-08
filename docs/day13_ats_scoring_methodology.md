# Day 13 — ATS scoring methodology

The active root score combines skill match, experience, education alignment,
and semantic similarity using the Python role-weight configuration in
`src/weight_manager.py` and the Day 13 score engine. Components are normalized
to 0–100; the API stores the final score and an explanation containing
component scores, weights, contributions, matching/missing requirements, and
human-review status.

When evidence is missing, the associated component is unavailable and
contributes zero under the current formula. This may lower scores without
proving lack of qualification; the evidence labels the missing input. The
score is an experimental deterministic/embedding heuristic, not an
employment-validated model. Weights and boundaries are not scientifically
validated. There is no stored formula/version history; edits to score inputs
clear the current saved score.

Weights must be reviewed in Python source: neighboring day-folder JSON
configurations are not the active source of truth. No automatic employment
decision is authorized by this score.
