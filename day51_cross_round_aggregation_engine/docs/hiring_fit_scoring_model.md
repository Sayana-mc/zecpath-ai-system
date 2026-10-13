

\# Hiring Fit Scoring Model



\## Formula



Normalized round score = (raw score / maximum possible score) \* 100



Hiring Fit Score =

sum(normalized score \* configured round weight)

divided by the sum of weights for completed rounds.



\## Example: Data Scientist role



| Round | Score | Weight | Contribution |

|---|---:|---:|---:|

| ATS | 85 | 10% | 8.50 |

| Screening | 80 | 15% | 12.00 |

| HR interview | 75 | 15% | 11.25 |

| Technical interview | 90 | 25% | 22.50 |

| Machine test | 80 | 35% | 28.00 |

| Total | | 100% | 82.25 |



Hiring Fit Score = 82.25%.



\## Partial evaluations



Pending or missing rounds are excluded from the score denominator.

The remaining configured weights are proportionally renormalized.

The report remains marked PARTIAL so users can see that an evaluation is missing.



\## Illustrative score bands



\- 80-100: STRONG\_FIT

\- 60 to below 80: POTENTIAL\_FIT

\- Below 60: NEEDS\_REVIEW



These are demonstration bands, not validated hiring thresholds.

The score is not a probability of job success.



