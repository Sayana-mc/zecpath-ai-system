# Day 11 — Education and certification parsing

The root parses education from a detected education section (falling back to
full text), returning rule-detected degree type/name, field, institution, and
graduation year. Certification extraction is now included in the persisted
resume profile and uses the detected certification section where available.
Normalization preserves the complete credential name while standardizing
known prefixes; a regression test covers AWS certification names.

The parsers are deterministic patterns, not a model. Institution and
qualification parsing may be incomplete for unfamiliar formats. Certification
issuer, issue/expiry dates, evidence confidence, and related skills are not
reliably extracted. Root scoring does not currently use certification
relevance; education alignment is a limited heuristic. Nontraditional
education should not be treated as automatically inferior. See
`day11_education_certification/tests/`.
