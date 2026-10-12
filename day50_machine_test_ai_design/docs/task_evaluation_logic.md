

\# Task Evaluation Logic



\## Coding problems

\- Check test results, edge cases and output correctness.

\- Consider time and memory complexity during review.

\- Review naming, readability, modularity and error handling.



\## Debugging tasks

\- Record original and revised code snapshots.

\- Compare supplied test results before and after the fix.

\- Assess root-cause explanation and regression risk.



\## File-based tasks

\- Validate output format and required columns/keys.

\- Check missing values, duplicate records and invalid data.

\- Compare produced results against an expected answer.



\## Mini system design

Use a documented rubric to assess:

\- Requirement understanding.

\- Component design and data flow.

\- Reliability and scalability.

\- Security and privacy.

\- Trade-offs and explanation.



\## Metric definitions



Correctness:

Passed test cases / total test cases \* 100.

If no test results exist, correctness is zero and a review flag is generated.



Efficiency:

A reviewer-assigned score from 0 to 100 based on algorithmic complexity,

resource use and performance evidence.



Code quality:

A reviewer-assigned score from 0 to 100 based on readability, structure,

maintainability, error handling and relevant tests.



Problem-solving:

A reviewer-assigned score from 0 to 100 based on approach, decomposition,

reasoning and explanation.



Time management:

Calculated from elapsed time relative to the task's allotted time.



Important:

The current prototype trusts supplied execution results and rubric scores.

A production evaluator must verify test evidence and document rubric decisions.



