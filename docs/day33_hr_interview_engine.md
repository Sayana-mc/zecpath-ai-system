# Day 33: AI HR Interview Engine & Question Generation

## 1. Overview & Objectives
The AI HR Interview Engine serves as the core conversational backbone for conducting structured, standardized, and unbiased human resource interviews across technical and non-technical tracks.

### Key Objectives
- Distinguish interview dynamics between **Fresher** and **Experienced** candidates.
- Differentiate question banks between **Technical** and **Non-Technical** tracks.
- Enforce a deterministic **Finite State Machine (FSM)** managing interview progression.
- Separate HR interview data and lifecycle from ATS resume screening and voice screening.

---

## 2. Question Personalization Strategy
Candidates are segmented across two primary dimensions:

### 2.1 Experience Level
- **Fresher Candidates:**
  - Focus on foundational understanding, academic/capstone project execution, self-learning velocity, and adaptability.
  - Explores potential, problem-solving mindset, and eagerness to learn rather than legacy production experience.
- **Experienced Candidates:**
  - Focus on past system architecture, trade-offs, cross-functional collaboration, team conflict resolution, tenure reasons, and demonstrated leadership.

### 2.2 Role Type
- **Technical Roles:**
  - Evaluates engineering discipline, system design discussions, API contract handling, reliability approaches, and technical communication.
- **Non-Technical Roles:**
  - Evaluates stakeholder negotiation, client management, conflict resolution, prioritization under business constraints, and cross-departmental alignment.

---

## 3. Finite State Machine (FSM) Phases
The interview flow follows a strict 6-state sequential model:

1. **CREATED:** Session initialized; role-tailored questions seeded into `hr_interview_questions`.
2. **INTRODUCTION:** Candidate presents professional/academic background; basic rapport established.
3. **CORE_HR_QUESTIONS:** Behavioral, cultural fit, teamwork, strengths/weaknesses exploration.
4. **ROLE_BASED_EVALUATION:** In-depth technical/operational challenge questions and situational judgment.
5. **CLOSING:** Candidate queries, availability, notice period, compensation expectations.
6. **COMPLETED:** Interview locked; aggregate scoring executed; 11-section report persisted.

