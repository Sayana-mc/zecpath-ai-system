# Day 12 — Semantic matching

The root uses the Day 12 `EmbeddingEngine`, configured for local
`all-MiniLM-L6-v2` inference and cosine similarity. Candidate/job embeddings
are produced together when scoring a resume. The job text includes title,
description, required/preferred skills, and specified education/experience
requirements. Personal names from header lines, labeled contact details, and
labeled attributes such as gender/date of birth are excluded from matching
input; scores preserve explicit evidence and human-review flags.

This is one overall embedding similarity, not separate validated skill,
experience, project, or responsibility models. Semantic thresholds are not
scientifically tuned. The model must be present in the local cache; failures
are surfaced as service unavailable. No embedding cache or content-hash
invalidation exists. Sanitization uses labels and format rules and is not a
guarantee of complete de-identification or proxy-bias removal. No benchmark
accuracy is claimed.
