\# Interview Flow Design



\## Conversation Phases



\### Phase 1 – Introduction



The AI starts the interview and asks self-introduction

questions.



\### Phase 2 – Core HR Questions



The AI asks questions related to:



\- Career journey

\- Strengths

\- Weaknesses

\- Teamwork

\- Culture fit

\- Career goals

\- Availability

\- Commitment



\### Phase 3 – Role-Based Evaluation



The AI generates questions according to:



\- Fresher / Experienced

\- Technical / Non-Technical



\### Phase 4 – Closing



The AI completes the interview and prepares the final

conversation state.



\## Interview State



The interview state stores:



\- Candidate ID

\- Experience level

\- Role type

\- Current phase

\- Current question ID

\- Candidate response

\- Follow-up eligibility

\- Completed questions



\## Follow-Up



A response can be marked as eligible for a follow-up question.

This allows future versions of the interview engine to

dynamically continue the conversation.

