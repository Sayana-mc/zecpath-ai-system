

\# Day 51 - Cross-Round Aggregation Framework



\## Objective

Combine scores from five hiring evaluation stages into a transparent,

role-specific unified candidate score object.



\## Input stages

1\. ATS: resume and job-requirement matching score.

2\. Screening: initial screening evaluation score.

3\. HR interview: communication and job-related HR rubric score.

4\. Technical interview: technical knowledge and reasoning score.

5\. Machine test: practical task evaluation score.



\## Workflow

1\. Load the candidate's target role and round evaluations.

2\. Load the approved weight configuration for that role.

3\. Validate scores and evaluation statuses.

4\. Normalize completed round scores to a 0-100 scale.

5\. Apply role-specific weights.

6\. Exclude pending or missing rounds from the denominator.

7\. Renormalize the remaining weights to total 100%.

8\. Generate the Hiring Fit Score and explanation.

9\. Save the unified candidate score as JSON.

10\. Route the result to a human reviewer.



\## Unified output

\- Candidate and session identifiers.

\- Target role and scoring version.

\- Round-level raw and normalized scores.

\- Configured and effective weights.

\- Weighted contributions and final score.

\- Missing and not-applicable rounds.

\- Score status, fit band and explanation.

\- Human-review safeguards.



\## Limitations

This prototype aggregates supplied scores. It does not independently validate

the quality of the upstream ATS, interview or machine-test assessments.



