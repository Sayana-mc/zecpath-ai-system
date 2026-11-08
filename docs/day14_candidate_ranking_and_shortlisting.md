# Day 14 — Candidate ranking and shortlisting

The root API ranks saved scores for a single opening in descending score order
with candidate name as a deterministic tie-breaker. The persisted shortlist
endpoint accepts a caller-selected cutoff and returns candidate ID, score,
rank, and a human-review warning; it does not change application status or
write a shortlist decision. Score-input changes invalidate saved scores.

The separate Day 14 module is a file-based prototype and is not the root
engine. The root provides one threshold, not configurable shortlist/review/
reject zones, and has no pagination or persisted ranking snapshot. It does
not auto-reject candidates; missing data and low extraction confidence still
need explicit review policies. A cutoff is operational configuration, not a
universally valid hiring threshold.
