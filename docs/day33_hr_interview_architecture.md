# Day 33: HR Interview Architecture & State Machine

## 1. System Architecture Diagram

```mermaid
flowchart TD
    A["Recruiter / API Request"] -->|"POST /api/v1/hr-interviews"| B["HRInterviewPipeline"]
    B --> C["HRInterviewEngine"]
    C --> D["RoleBasedQuestionGenerator"]
    D --> E["Database: hr_interview_sessions"]
    D --> F["Database: hr_interview_questions"]
    
    subgraph Interview Lifecycle FSM
        G["CREATED"] --> H["INTRODUCTION"]
        H --> I["CORE_HR_QUESTIONS"]
        I --> J["ROLE_BASED_EVALUATION"]
        J --> K["CLOSING"]
        K --> L["COMPLETED"]
    end
    
    B --> G
    L --> M["HRScoringEngine"]
    M --> N["HRSummaryGenerator"]
    N --> O["Database: hr_interview_reports"]
```

## 2. Key Architecture Principles
1. **Additive Schema:** Operates entirely independently from `screenings` and `candidates` ATS resume scores.
2. **Deterministic State Machine:** Guarantees candidates cannot skip stages or modify completed interview records.
3. **Idempotent Storage:** Question sets are bound to `interview_id` and frozen at session creation.

