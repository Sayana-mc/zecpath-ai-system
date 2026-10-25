# Scoring Logic and Decision Handling

## Historical proof-of-concept bands
Earlier project context described these resume-screening bands:
- 70–100: shortlist recommendation
- 50–69: review
- Below 50: reject recommendation in the proof of concept

These are historical prototype rules, not verified current production policy. Confirm the actual scoring function and approved policy before publishing or using thresholds. Do not use this document to authorize automatic rejection.

## Recommended pipeline
1. Validate extraction.
2. Compare extracted evidence with defined job criteria.
3. Calculate score using the implemented algorithm.
4. Validate score range and output schema.
5. Record criteria version, model version, evidence references, and timestamp.
6. Route recommendation for recruiter review.
7. Record reviewer outcome separately from model output.

## Explainability
Where supported, store score/scale, criteria version, evidence references, missing or ambiguous evidence, model version, timestamp, and review status. Never invent evidence.

## Quality and safety
Test boundary values (49, 50, 69, 70, 100) against the actual code. Evaluate on reviewed representative data; examine precision, recall, calibration, and errors as appropriate. Treat low confidence, extraction failure, or conflicting evidence as review conditions. Keep human review for consequential outcomes.

Accuracy = correct predictions / total labelled evaluation examples. Confidence and HTTP success are not accuracy.

## Source verification
Locate the current scoring function, prompt/template, thresholds, model configuration, and tests. Update this file only after confirming implementation and approved policy.
