

\# Day 50 - Machine Test AI Framework



\## Objective

Evaluate practical technical skills using structured tasks, captured submissions,

test execution evidence and a configurable scoring model.



\## Supported task types



1\. Coding problems

&#x20;  - Algorithms, data structures and function implementation.

&#x20;  - Evaluate using predefined test cases, edge cases and constraints.



2\. Debugging tasks

&#x20;  - Candidate identifies and fixes a supplied defect.

&#x20;  - Compare test results before and after the proposed fix.

&#x20;  - Review the explanation of the root cause.



3\. File-based tasks

&#x20;  - Process CSV, JSON, TXT or spreadsheet data.

&#x20;  - Evaluate output structure, required fields, data correctness and error handling.



4\. Mini system design

&#x20;  - Candidate submits a text or diagram description.

&#x20;  - Review architecture, component responsibilities, scalability, reliability,

&#x20;    security and trade-offs using a human-scored rubric.



\## Workflow



1\. Select task and configure deadline.

2\. Display instructions and input data.

3\. Capture candidate answer and code snapshots.

4\. Run code only in an isolated execution environment managed separately.

5\. Collect test results and execution metadata.

6\. Calculate correctness, efficiency, quality, problem-solving and time scores.

7\. Generate a structured JSON report.

8\. Send the report for human review.



\## Input capture



\- Session and candidate identifiers.

\- Task ID and task type.

\- Allotted time and elapsed time.

\- Code or answer snapshots.

\- Test case results and execution logs.

\- Human-reviewed metric scores.



\## Output capture



\- Test pass count and correctness percentage.

\- Weighted score breakdown.

\- Final score out of 100.

\- Performance band.

\- Review flags and limitations.

\- Human-review recommendation.



\## Security and fairness



Do not execute untrusted submissions directly inside the evaluator.

Use a separate sandbox with resource limits and no unnecessary network access.

Store only necessary candidate data and define a retention policy.

Give candidates consistent instructions and equivalent test conditions.

Do not use speed alone to infer ability or misconduct.

Provide human review and a correction/appeal process.



\## Prototype limitations



This Day 50 implementation accepts execution results and rubric scores as input.

It captures code but does not run it, compile it, or independently verify test results.

The system is a design prototype, not a production hiring platform.



