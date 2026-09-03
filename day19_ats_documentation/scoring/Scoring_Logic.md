\# ATS Scoring Logic



\## 1. Purpose



The ATS scoring system evaluates how well a candidate resume matches a specific job requirement.



The resulting ATS score is used for candidate ranking and recruitment decision generation.



\## 2. Main Inputs



The scoring process considers information extracted from:



\- Candidate resume

\- Candidate skills

\- Candidate experience

\- Job requirements

\- Job title

\- Relevant resume sections



\## 3. Candidate Evaluation



The candidate is evaluated against the requirements of the target job.



Relevant candidate information is identified from the resume and compared with the job requirements.



The resulting score represents the candidate's overall ATS relevance.



\## 4. Candidate Ranking



Candidates are ordered according to their final ATS scores.



Higher-scoring candidates receive higher positions in the ranking.



The ranking output includes:



\- Candidate name

\- Final ATS score

\- Rank

\- Decision

\- Job ID

\- Job title



\## 5. Decision Categories



The ATS uses three decision categories:



\### SHORTLISTED



The candidate is considered suitable for the role based on the ATS evaluation.



\### REVIEW



The candidate requires additional human review.



\### REJECTED



The candidate does not sufficiently match the role according to the ATS evaluation.



\## 6. Testing of Scoring and Decisions



During Day 17, AI decisions were compared with manual reviewer decisions.



The test dataset contained 55 candidate-job cases.



Results:



Accuracy: 94.55%



Precision: 100%



Recall: 57.14%



F1 Score: 72.73%



Mismatch cases: 7



\## 7. Important Observation



The testing results indicate that the system produced no false-positive shortlist decisions in the tested dataset.



However, three manually shortlisted candidates were classified differently by the AI system.



This indicates that improving recall and decision thresholds should be considered in future optimization work.

