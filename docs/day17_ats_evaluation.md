# Day 17 — ATS evaluation

`src/ats_evaluation.py` provides dependency-free binary precision, recall, F1,
accuracy, confusion-matrix, and CSV reviewed-pair helpers. The
`data/evaluation/day17_ats_review_template.csv` file contains column headers
only. Pending or malformed review rows are excluded.

There are no reviewed labels in this repository. Therefore the helper has not
been used to claim ATS accuracy, and no score threshold, ranking quality, or
candidate outcome quality is established. Synthetic integration tests check
the metric arithmetic only; they are not evaluation data.

Before reporting metrics, obtain permissioned examples, document label
definitions and reviewer agreement, separate development from held-out data,
and report limitations and relevant slices. See
[known limitations](day16_day23_known_limitations.md).
