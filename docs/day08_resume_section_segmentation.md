# Day 8 — Resume section segmentation

The root profile pipeline now calls the Day 8 rule-based segmenter. It
recognizes summary/profile, objective, skills, work-history, education,
certification, project, achievement, publication, and language headings,
with unrecognized lines retained in `OTHER`. Day 9 skills are scoped to
recognized skills/work/project/certification sections when those sections
exist; experience and education use their matching section, with full-text
fallback when their section is absent. The full segmentation is retained in
the extracted profile.

This is not a layout-aware classifier: extraction is line/heading based and
does not preserve reliable character offsets, confidence, or detection-method
metadata. Multi-column, table, and scanned-document handling is unverified.
No labeled evaluation corpus or measured precision/recall/F1 exists, so no
accuracy claim is made. Automated section tests are in
`day8_resume_section_segmentation/tests/`; root upload/scoring integration is
covered by `tests/test_api.py`.
