# Day 29 — AI Conversation Flow State Machine

## 1. Overview
The Day 29 conversation flow system governs dynamic voice screening dialogue. Rather than acting as a static question queue, it employs a finite state machine (FSM) and decision tree to handle conversational realities such as candidate silence, confusion, brief answers, and interruptions.

## 2. Finite State Machine States
- `START`: Initial state when session is instantiated.
- `ASKING`: System prompts candidate with an interview question.
- `WAITING`: System waits for candidate response; silence detection active.
- `CLARIFICATION`: Candidate asked for clarification or expressed confusion; system provides explanation.
- `FOLLOW_UP`: Candidate answer was too brief (<5 words); system prompts for elaboration.
- `RETRY`: STT error or unparseable response; system prompts candidate to repeat.
- `COMPLETED`: All questions completed or session concluded.

## 3. Transition Rules & Decision Logic
1. **Silence:** Candidate does not respond within timeout $\rightarrow$ Transition to `WAITING`, prompt politely: *"Take your time. Please answer when you are ready."*
2. **Candidate Confusion:** Candidate says *"I don't understand"* or *"Can you repeat?"* $\rightarrow$ Transition to `CLARIFICATION`, repeat question with simpler phrasing.
3. **Terse Answer:** Word count $< 5$ words $\rightarrow$ Transition to `FOLLOW_UP`, ask: *"Could you please provide a little more detail?"*
4. **Valid Answer:** Answer contains relevant detail $\rightarrow$ Store answer, transition to `ASKING` with next question.
5. **Interview Complete:** All questions answered $\rightarrow$ Transition to `COMPLETED`, thank candidate and close session.

