# Root ATS scoring methodology

## Status and source of truth

The root API scoring pipeline is implemented in `src.integrated_scoring`.
It combines Day 8 section segmentation, Day 9–11 rule-based extraction, Day 12 local
SentenceTransformer similarity, and Day 13's `generate_score_breakdown`.
There is no executable Day 20 scorer. The active role weights are in
`day13_ats_scoring/src/weight_manager.py`; the similarly named JSON
configurations are not loaded by that implementation and conflict for several
roles.

The pipeline is experimental decision support, not a validated employment
assessment. It does not automatically reject, hire, or change candidate
status.

## Inputs and components

For a candidate already associated with the selected opening:

1. **Skills:** merge candidate-reported skills and Day 9 extracted skills.
   The component is matched required skills divided by the number of unique
   normalized required skills. Preferred skills are displayed as evidence but
   are not part of this Day 13 component.
2. **Experience:** Day 10 parsed total duration (dated overlapping ranges are
   merged; undated duration estimates remain approximate) divided by the opening's minimum years, capped at 1. If either
   candidate years or job minimum is unavailable, the component result is
   unavailable. A configured minimum of zero yields a full component score.
3. **Education:** the first Day 11 education record is compared with the
   configured minimum via Day 13's degree-level mapping. Missing/unrecognized
   levels are unavailable.
4. **Semantic similarity:** the local `all-MiniLM-L6-v2` model encodes
   sectioned resume text after basic contact/common labeled personal-data
   filtering and job text containing title, description, required and
   preferred skills, and specified education/experience requirements.
   Cosine similarity is clamped to 0–1. It is not calculated without readable
   resume text.

## Formula and active weights

Each component is passed to the Day 13 normalizer, which maps 0–1 values to
0–100 and clamps to that range. The final score is:

```text
final = skill_0_100 * skill_weight
      + experience_0_100 * experience_weight
      + education_0_100 * education_weight
      + semantic_0_100 * semantic_weight
```

Weights come from the Day 13 Python `ROLE_WEIGHTS`; for unrecognized opening
titles, `DEFAULT_WEIGHTS` is used. Current default / Data Analyst weights are
35% skill, 20% experience, 15% education, and 30% semantic. Other defined
roles differ; response evidence returns the exact weights used. No weight file
was silently substituted or rewritten.

The final score is clamped to 0–100 and classified by the Day 13 thresholds.
Weighted component contributions and component scores are returned and saved
with the candidate.

## Missing values and cautions

The API evidence marks missing experience/education/semantic inputs with a
`null` component score and a reason. The existing Day 13 normalization maps a
missing component to zero for the final formula. Zero contribution is a
missing-evidence handling rule, not evidence that the applicant lacks a
qualification. Scores may therefore be misleading when data is incomplete.
The resume's text and skill overlap can also correlate with semantic
similarity; the components are not independent measurements.

The Day 9 dictionary is incomplete; Day 10 date parsing can misread irregular
timelines; Day 11 degree mapping is coarse; Day 12 general-purpose embeddings
are not calibrated for hiring. We have not validated scores for job relevance,
reliability, subgroup performance, calibration, or legal compliance.

## API evidence

`POST /api/v1/candidates/score` requires both `job_id` and `candidate_id`,
rejects cross-opening candidate IDs, refuses a missing/unavailable model with
HTTP 503 (no fabricated semantic score), persists score and evidence, and
returns job/candidate labels, matching/missing skills, extracted
education/experience, components, weights, contributions, classification,
ranking and `human_review_required: true`. Score inputs invalidate stale
results. The job-specific shortlist uses only persisted scores for that
opening.

The local model is loaded once per process from cache with
`local_files_only=True`. See the README for its one-time cache setup command.
