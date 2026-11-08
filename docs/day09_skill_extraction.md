# Day 9 — Skill extraction

The root uses the Day 9 dictionary and alias-based rules. Skills are
normalized to canonical names, deduplicated, categorized, and annotated with
source section, match type, and rule-derived confidence. Recognized section
content is preferred; if no target section exists, extraction falls back to
the full resume. Stack detections can include both the stack label and
components; a stack alone is not proof that each component was independently
used.

The dictionary is finite and rule-based, not a learned NLP model. Unsupported
synonyms, ambiguous short terms, context, negation, and misspellings can cause
false positives/negatives. Confidence values are heuristic, not calibrated
probabilities. The root score uses extracted and recruiter-reported skills;
it does not treat the confidence as a validated quality probability.

See the engine and tests under `day9_skill_extraction/`. No independent
representative-corpus precision/recall evaluation has been completed.
