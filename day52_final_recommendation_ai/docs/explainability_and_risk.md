

\# Explainability and Risk Handling



\## Inputs



\- Day 51 unified score

\- Completed and expected evaluation rounds

\- Evidence quality and data consistency

\- Integrity and behavior review flags

\- Round-level assessment scores



\## Explainable output



Every recommendation contains:



\- Candidate and session identifiers

\- Target role

\- Final score and confidence

\- Decision category

\- Round coverage

\- Risk flags and evidence sources

\- Reasons supporting the recommendation

\- Conditions requiring human review

\- Decision rule version and audit safeguards



\## Integrity risk



An integrity flag must be supported by evidence and a traceable source.

Examples include an assessment log that requires verification or a documented

test-integrity concern. A flag triggers review, not automatic rejection.



\## Behavior risk



Only documented, job-related observations from a structured assessment

should be considered. Do not use vague impressions, protected traits,

disability-related assumptions, or personal characteristics unrelated to

the role.



\## Missing information



Missing rounds and incomplete records lead to HOLD\_REVIEW. Missing information

must not be silently interpreted as poor candidate performance.



\## Human oversight



The engine produces a recommendation only. An authorized human reviewer must

verify the evidence and make any actual employment decision.



