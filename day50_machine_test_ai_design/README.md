

\# Day 50 - Machine Test AI Design



\## Objective

Design a prototype to evaluate real-world technical skills using coding,

debugging, file-based and mini system-design tasks.



\## Features

\- Configurable scoring weights.

\- Correctness calculation from supplied test results.

\- Efficiency, code-quality and problem-solving rubric scores.

\- Time-based scoring.

\- Code snapshot and execution-result metadata.

\- JSON report generation.

\- Input validation and unit tests.

\- Human review required; automatic rejection disabled.



\## Requirements

\- Python 3.10 or newer recommended.

\- No external Python packages required.



\## Run from the project root



Run the tests:



python -m unittest discover -s day50\_machine\_test\_ai\_design/tests -v



Run the evaluator:



python -m day50\_machine\_test\_ai\_design.src.main



Inspect the report:



Get-Content .\\day50\_machine\_test\_ai\_design\\output\\machine\_test\_report.json



\## Limitation

This prototype does not execute submitted code. Test results and rubric scores

are supplied as input and should be independently verified in a production system.



