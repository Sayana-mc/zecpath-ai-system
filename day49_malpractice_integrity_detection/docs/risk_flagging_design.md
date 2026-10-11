

\# Risk Flagging System Design



\## Risk levels

\- LOW: 0–24 points

\- MODERATE: 25–49 points

\- HIGH: 50–100 points



These are prototype configuration ranges, not validated thresholds.



\## Warning system

Each event that crosses its configured threshold creates a warning

with the event name, observed count, threshold, risk tag, and message.



When three or more event categories cross thresholds, the prototype

adds a combined-pattern flag.



\## Real-time alert plan

The current prototype generates alerts after processing a JSON event

sample. A future implementation could process verified events as they

arrive and show a non-accusatory warning to an authorized reviewer.



\## Day 48 integration

The Day 48 signal-consistency index may be stored as contextual metadata.

It is excluded from the integrity risk score because behavioral variation

is not evidence of malpractice.



\## Decision policy

\- No automatic rejection.

\- Human review is required for flagged sessions.

\- Allow explanations, accommodations, and correction of event errors.

\- Keep event data only as long as necessary under an approved policy.

\- Restrict access to authorized reviewers.



