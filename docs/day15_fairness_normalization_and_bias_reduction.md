# Day 15 — Fairness, normalization, and bias reduction

## Safeguard applied to the root score path

Resume sections are normalized before rule extraction. Semantic matching now
uses the sectioned profile representation instead of passing the candidate
display name or contact fields as model input. The helper also removes
labeled personal attributes (for example, gender, age, date of birth,
religion, nationality, and address), email addresses, and standalone phone
lines. Matching evidence and score output explicitly record this limited
masking and retain a human-review requirement. These safeguards are covered
by an API-level upload/score regression test.

## Limits and policy

This is basic masking, not full de-identification: unlabeled data, indirect
proxies, employer/institution names, location context, extraction differences,
and model behavior may still affect scores. Recruiter-reported skills remain
inputs. No protected traits are inferred. The repository has no authorized,
lawfully collected subgroup evaluation data, so group fairness metrics are
not calculated and no fairness claim is made. The Day 15 prototype's
min-max rescaling and keyword-score adjustment are not applied to root scores
because such dataset-relative transformations are not validated and could
distort candidate comparisons.

Scores and rankings are decision support only. Recruiters must review source
evidence, uncertainty, missing data, and corrections; employment gaps and
nontraditional education are not automatic negative evidence. A formal
fairness evaluation, legal review, explainability testing, and complete
personal-data minimization remain outstanding.
