# Final Polished Outputs

## Files
- `output/recruiter_summary.json`: detailed recruiter review summary with scoring version, records, review flags, and safety fields.
- `output/recruiter_summary.csv`: spreadsheet-friendly summary with one candidate per row.
- `output/run_report.txt`: readable run summary and report locations.

## Consistent score formula
`score = 0.80 × required_skill_coverage_percent + 0.20 × preferred_skill_coverage_percent`

Required skill coverage is the percentage of listed required skills detected in the resume text. Preferred skill coverage is calculated similarly. The result is clamped to 0–100 and rounded to one decimal place.

This is a transparent demonstration heuristic only; it does not assess context, skill depth, fairness, or job performance.

## Status behavior
- `HUMAN_REVIEW_REQUIRED`: at least one review flag is present.
- `INTERVIEW_REVIEW`: no review flag is present and interview response data is available.
- `SCREENING_REVIEW`: no review flag is present and interview response data is unavailable.

These labels route records for review; they are not final hiring decisions.
