

\# Confidence Scoring



\## Purpose



Confidence estimates how complete and consistent the available evidence is.

It is not a probability of job success or a probability that a recommendation

is correct.



\## Formula



Let:



\- C = completed evaluation rounds

\- E = expected evaluation rounds

\- Q = evidence quality from 0 to 100

\- D = data consistency from 0 to 100



Coverage = (C / E) \* 100



Confidence = (Coverage \* 0.50) + (Q \* 0.30) + (D \* 0.20)



The engine rounds confidence to two decimal places.



\## Sample



C = 5

E = 5

Q = 90

D = 100



Coverage = (5 / 5) \* 100 = 100



Confidence = (100 \* 0.50) + (90 \* 0.30) + (100 \* 0.20)

Confidence = 50 + 27 + 20 = 97.00



\## Interpretation



A confidence score of 97.00 indicates high evidence completeness under this

prototype formula. It does not guarantee candidate performance.



Confidence below the selection threshold leads to HOLD\_REVIEW.



