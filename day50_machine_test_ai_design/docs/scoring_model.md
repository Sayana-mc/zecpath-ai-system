

\# Machine Test Scoring Model



\## Weight distribution



| Metric | Weight |

|---|---:|

| Correctness | 50% |

| Efficiency | 15% |

| Code quality | 15% |

| Problem-solving | 10% |

| Time management | 10% |

| Total | 100% |



\## Formula



Final score =

(Correctness x 0.50) +

(Efficiency x 0.15) +

(Code quality x 0.15) +

(Problem-solving x 0.10) +

(Time management x 0.10)



Every raw metric is scored from 0 to 100.



\## Time scoring policy



Let ratio = elapsed seconds / allotted seconds.



\- Ratio <= 0.70: time score 100.

\- Ratio between 0.70 and 1.00: score decreases linearly from 100 to 50.

\- Ratio > 1.00: time score 0.



Correctness is not reduced by the time factor; time is a separate component.

In this prototype, exceeding the deadline produces a review flag.



\## Illustrative performance bands



\- 80 to 100: STRONG

\- 60 to below 80: COMPETENT

\- Below 60: NEEDS\_FURTHER\_REVIEW



These are demo thresholds, not validated hiring standards.



\## Sample calculation



Given:

\- Correctness: 75

\- Efficiency: 80

\- Code quality: 85

\- Problem-solving: 80

\- Time management: 100



Final score =

(75 x 0.50) + (80 x 0.15) + (85 x 0.15) +

(80 x 0.10) + (100 x 0.10)



= 37.50 + 12.00 + 12.75 + 8.00 + 10.00

= 80.25 / 100



The score is an illustrative decision-support result. A human reviewer must

consider task relevance, accommodations, test validity and contextual evidence.



