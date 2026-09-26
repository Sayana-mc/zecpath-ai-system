\# Day 36 – Behavioral Signal Logic Documentation



\## Objective



The objective of Day 36 is to assess confidence and behavioral signals from candidate responses.



\## 1. Hesitation Detection



The system detects:



\- Hesitation words

\- Pause markers

\- Repeated words

\- Uncertainty phrases



Examples:



\- um

\- uh

\- hmm

\- maybe

\- perhaps

\- I think

\- I am not sure



\## 2. Sentiment Analysis



The sentiment engine identifies:



\- Positive sentiment

\- Negative sentiment

\- Neutral sentiment



Positive indicators include words such as:



\- confident

\- successful

\- achieved

\- improved

\- excellent



Negative indicators include:



\- difficult

\- worried

\- stressed

\- confused

\- failed



A sentiment score from 0–100 is generated.



\## 3. Contradiction Detection



The system compares the current answer with previously available candidate information.



Example:



Previous information:

1 year experience



Current answer:

2 years experience



The system identifies this as a contradiction.



\## 4. Stress Indicators



Stress signals are calculated from:



\- Hesitation

\- Long pauses

\- Uncertainty

\- Repeated words

\- Negative sentiment



A stress score from 0–100 is generated.



\## 5. Confidence Score



The confidence score starts at 100.



Penalties are applied for detected:



\- Hesitation

\- Pauses

\- Repeated words

\- Uncertainty



The final confidence score is normalized between 0 and 100.



\## 6. Important Interpretation



These signals are behavioral indicators only.



They should not be treated as medical, psychological, or definitive assessments of a candidate.



The system uses textual response characteristics to identify communication patterns.

