\# Day 47 – Technical Skill Scoring Model



\## Objective



Evaluate technical answers beyond surface-level responses using a configurable scoring rubric and an explainable report.



\## Deliverables



1\. Technical Scoring Engine

2\. Skill-Wise Scoring Breakdown

3\. Technical Evaluation Report Format



\## Scoring Parameters



\- Accuracy: 35%

\- Depth of Explanation: 25%

\- Logical Reasoning: 20%

\- Real-World Applicability: 20%



Each parameter is scored from 0 to 5. Question-type-specific weights are configured in `config/scoring\_rubric.json`.



\## Main Components



\- `config/scoring\_rubric.json`: Scoring parameters and question-type weights.

\- `data/technical\_answers.json`: Sample candidate answers and demo scores.

\- `src/scoring\_engine.py`: Score calculation, answer-depth classification, and report generation.

\- `src/main.py`: Executes the scoring workflow.

\- `tests/test\_day47.py`: Automated tests.

\- `output/technical\_evaluation\_report.json`: Generated evaluation report.

\- `docs/technical\_evaluation\_report\_format.md`: Report documentation.



\## Execution



Run from the project root:



```powershell

pytest .\\day47\_technical\_skill\_scoring\\tests\\test\_day47.py -v

python -m day47\_technical\_skill\_scoring.src.main

```



\## Limitations



The current module is a rule-based scoring demonstration. Parameter scores are provided in the sample dataset; the system does not independently assess technical correctness or replace human evaluation.



