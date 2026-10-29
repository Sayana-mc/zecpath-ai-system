# Final UI/API Adjustment Recommendations

These are implementation recommendations, not claims that the existing deployed UI or API was changed.

## Recruiter UI
- Show candidate ID, target role, score, scoring version, and review status together.
- Display required and preferred skill coverage separately.
- Present missing evidence and review flags in plain language.
- Provide filters for status and role, plus stable sorting and pagination.
- Include a visible simulation/demo indicator when using synthetic data.
- Keep human review actions explicit; do not expose an automatic reject action driven only by score.
- Ensure keyboard navigation, labels, contrast, and readable empty/error states.

## API
- Validate required fields and referenced job IDs before scoring.
- Return structured errors with a stable `code`, safe `message`, and `request_id`.
- Version scoring configuration and response schema.
- Use authentication and authorization in a real deployment.
- Add timeouts, bounded retries for transient errors, idempotency where relevant, and rate limits.
- Do not log raw resume contents or unnecessary personal data.
- Add contract tests and backward-compatibility checks before release.

## Suggested error response shape
```json
{
  "error": {
    "code": "INVALID_CANDIDATE_JOB_REFERENCE",
    "message": "Candidate references an unknown job.",
    "request_id": "demo-request-id"
  }
}
```
