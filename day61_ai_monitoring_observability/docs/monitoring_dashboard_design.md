# Monitoring Dashboard Design — Day 61

## Row 1: Service health
Cards: request count, API failure rate, p95 latency, model failure count, queue depth/oldest job. Filters: environment, service, endpoint, model version, time range.

## Row 2: Candidate processing
- Time series of resumes received/processed.
- Funnel: received → parsed → validated → screening completed → recruiter review.
- Error table grouped by type, endpoint, and retry count.
- Processing duration by pipeline stage.

## Row 3: Interview analytics
Show interview-analysis runs, operational completion rate, latency percentiles, and failure categories. Define “success” clearly: pipeline completion is not the same as hiring success.

## Row 4: Model quality and governance
Reviewed-set accuracy/precision/recall, drift by model version, human-review coverage, pending reviews, and audit completeness. Do not use these monitoring values as automatic rejection rules.

## Row 5: Alerts and audit
Active alerts by severity, owner, age, acknowledgement; recent audit events with authorized drill-down; correlation-ID links.

## Access
Operations sees service health; ML team sees model metrics and reviewed-set quality; recruiters see authorized workflow information; compliance reviewers see restricted audit records. Aggregate dashboard data and restrict candidate-level details.
