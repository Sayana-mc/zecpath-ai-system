\# HR Interview AI – Developer Handbook



\## 1. Introduction



This handbook explains how developers can understand, integrate, test and maintain the HR Interview AI system.



\---



\## 2. Project Components



The HR AI system contains several logical components:



1\. Transcript Processing

2\. Answer Understanding

3\. Communication Evaluation

4\. HR Interview Scoring

5\. Unified Scoring

6\. Explainability

7\. Ethics and Compliance

8\. API Integration



\---



\## 3. Integration Steps



\### Step 1



Prepare candidate data.



\### Step 2



Send the candidate data to the screening API.



\### Step 3



Send interview responses to the interview evaluation endpoint.



\### Step 4



Receive structured JSON responses.



\### Step 5



Store the required scoring information.



\### Step 6



Display the result in the HR application.



\### Step 7



Send low-confidence or exceptional cases for human review.



\---



\## 4. Data Format



Candidate information should contain:



\- candidate\_id

\- role

\- responses



Each response should contain:



\- question\_id

\- response



\---



\## 5. Scoring Logic



The HR interview score is based on:



\- Relevance

\- Communication

\- Confidence

\- Consistency



Scores are normalized to a 0–100 range.



Component-level scores should be retained for explainability.



\---



\## 6. API Integration



The API communicates using JSON.



Example:



POST /api/v1/interview/evaluate



Request:



```json

{

&#x20;   "candidate\_id": "C001",

&#x20;   "question\_id": "Q001",

&#x20;   "question": "Tell me about yourself.",

&#x20;   "response": "I am a data science graduate with Python and SQL experience."

}

