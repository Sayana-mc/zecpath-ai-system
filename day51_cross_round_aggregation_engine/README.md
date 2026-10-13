

\# Day 51 - Cross-Round Aggregation Engine



\## Objective

Combine five evaluation stages into a unified role-specific Hiring Fit Score.



\## Features

\- ATS, Screening, HR Interview, Technical Interview and Machine Test aggregation.

\- Role-based weight configuration.

\- Score normalization to a common 0-100 scale.

\- Missing-round handling and weight renormalization.

\- Transparent round-level weighted contributions.

\- Unified candidate score JSON object.

\- Input validation and unit tests.

\- Human review required; automatic rejection disabled.



\## Requirements

Python 3.10 or newer recommended.

No external Python packages are required.



\## Run from the project root



Run tests:



python -m unittest discover -s day51\_cross\_round\_aggregation\_engine/tests -v



Run the aggregation engine:



python -m day51\_cross\_round\_aggregation\_engine.src.main



Inspect the generated report:



Get-Content .\\day51\_cross\_round\_aggregation\_engine\\output\\unified\_candidate\_score.json



\## Important

The prototype aggregates supplied evaluation scores. It does not independently

verify upstream assessment quality and must not be the sole basis for hiring.



